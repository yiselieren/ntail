#
# Mini help window
# ----------------
#
import curses
import curses.panel
import sys
import os

from Globals import *

class Minihelp:
    def cursesLock(function):
        def wrapper(self,*args,**kwargs):
            self._lock.acquire()
            try:
                return function(self,*args,**kwargs)
            finally:
                self._lock.release()
        return wrapper

    def __init__(self, lock, h, w, txt):
        self._lock = lock
        self._height = h
        self._width = w
        self.text = txt

        self._lock.acquire()  # <<< LOCK
        self._w = curses.newwin(self._height, self._width, self._height, 0)
        self._lock.release()  # >>> LOCK

        self.refresh_lock()

    @cursesLock
    def refresh_lock(self):
        self.refresh()

    def refresh(self):
        self._w.attrset(curses.color_pair(SPEC_COLOR) | curses.A_BOLD)
        self._w.clear()
        txt = ' {} '.format(self.text)
        self._w.addstr(0, (self._width - len(txt)) // 2, txt)
        self._w.move(0, 0)
        self._w.refresh()
