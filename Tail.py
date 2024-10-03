#
# Tail thread
# -----------
#
import time
import curses
import curses.panel
import sys
import os
import ctypes
import ctypes.util
from threading import Thread
from Globals   import *

# Constants for inotify
IN_MODIFY = 0x00000002

class Tail(Thread):
    def __init__(self, inp_instance, w, fname, read_existing = False):
        self.fname = fname
        self.inp = inp_instance
        self.read_existing = read_existing
        if not os.path.exists(self.fname):
            f = open(self.fname, 'w')
            f.close()
        self.f = open(self.fname, 'r')
        self.w = w
        self.libc = ctypes.CDLL(ctypes.util.find_library('c'))
        Thread.__init__(self)

    def start(self):
        Thread.start(self)

    def reread(self):
        self.w.clear()
        self.f.seek(0, os.SEEK_SET)
        lines = self.f.readlines()
        if len(lines) > self.w.last_visible_idx - 1:
            x = len(lines) - self.w.last_visible_idx - 1
            self.w.set_total(x)
            for line in lines[x:]:
                self.w.add(line.rstrip())
        else:
            x = len(lines)
            self.w.set_total(0)
            for line in lines:
                self.w.add(line.rstrip())
        self.w.addlasttime()
        self.inp.refresh()

    def run(self):
        inotify_fd = self.libc.inotify_init()
        wd = self.libc.inotify_add_watch(inotify_fd, self.fname.encode(), IN_MODIFY)
        if self.read_existing:
            lines = self.f.readlines()
            if len(lines) > self.w.last_visible_idx - 1:
                x = len(lines) - self.w.last_visible_idx - 1
                self.w.set_total(x)
                for line in lines[x:]:
                    self.w.add(line.rstrip())
                self.w.addlasttime()
                self.inp.refresh()
            else:
                x = len(lines)
                self.w.set_total(0)
                for line in lines:
                    self.w.add(line.rstrip())
                self.w.addlasttime()
                self.inp.refresh()
        else:
            self.f.seek(0, os.SEEK_END)
        self.w.addlasttime()

        while True:
            buffer = os.read(inotify_fd, 1024)
            while True:
                line = self.f.readline()
                if line:
                    self.w.add(line.rstrip())
                    self.inp.refresh()
                else:
                    break
            self.w.addlasttime()
