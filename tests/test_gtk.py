# $Id: test_gtk.py,v 1.8 2001/08/21 10:08:22 kjetilja Exp $

## System modules
import sys, threading

## Gtk modules
from gtk import *

## PycURL module
import pycurl


def progress(download_t, download_d, upload_t, upload_d):
    global round, pbar
    threads_enter()
    if download_t == 0:
        pbar.set_activity_mode(1)
        round = round + 0.1
        if round >= 1.0:  round = 0.0
    else:
        pbar.set_activity_mode(0)
        round = float(download_d) / float(download_t)
    pbar.update(round)
    threads_leave()
    return 0 # Anything else indicates an error


def close_app(*args):
    global t, win
    win.destroy()
    mainquit()
    return TRUE


class Test(threading.Thread):

    def __init__(self, url, target_file):
        threading.Thread.__init__(self)
        self.target_file = target_file
        self.curl = pycurl.init()
        self.curl.setopt(pycurl.URL, url)
        self.curl.setopt(pycurl.FILE, target_file)
        self.curl.setopt(pycurl.FOLLOWLOCATION, 1)
        self.curl.setopt(pycurl.NOPROGRESS, 0)
        self.curl.setopt(pycurl.PROGRESSFUNCTION, progress)
        self.curl.setopt(pycurl.MAXREDIRS, 5)

    def run(self):
        self.curl.perform()
        self.curl.cleanup()        
        self.target_file.close()
        

# Check command line args
if len(sys.argv) < 3:
    print "Usage: %s <URL> <filename>" % sys.argv[0]
    raise SystemExit

# Launch a window with a statusbar
win = GtkDialog()
win.set_title("PycURL progress")
win.show()
vbox = GtkVBox(spacing=5)
vbox.set_border_width(10)
win.vbox.pack_start(vbox)
vbox.show()
label = GtkLabel("Downloading %s" % sys.argv[1])
label.set_alignment(0, 0.5)
vbox.pack_start(label, expand=FALSE)
label.show()
pbar = GtkProgressBar()
pbar.set_usize(200, 20)
vbox.pack_start(pbar)
pbar.show()
win.connect("destroy", close_app)
win.connect("delete_event", close_app)

# Start thread for fetching url
f = open(sys.argv[2], 'w')
round = 0.0
t = Test(sys.argv[1], f)
t.start()

# Start GTK mainloop
threads_enter()
mainloop()
threads_leave()
