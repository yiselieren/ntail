#
# File details window
# -------------------
#
import time
import curses
import curses.panel
import sys
import os

from Globals import *

class Details:
    def cursesLock(function):
        def wrapper(self,*args,**kwargs):
            self._lock.acquire()
            try:
                return function(self,*args,**kwargs)
            finally:
                self._lock.release()
        return wrapper

    def __init__(self, lock, filename, h, w, x, y, show_numbers = True):
        self._title = ' ' + filename + ' '
        self._height = h
        self._pg = h - 3
        self._lock = lock
        self._width = w
        self._xoffs = x
        self._yoffs = y
        self.first = 1
        self.last = 1
        self.filename = filename
        self.show_numbers = show_numbers
        max_title = self._width - LEFT_BW - RIGHT_BW - 2
        if len(self._title) > max_title:
            self._title = self._title[0:max_title]

        self.lines = []
        with open(self.filename) as f:
            while True:
                line = f.readline()
                if not line:
                    break
                self.lines.append(line.rstrip())
        shift = len('{}'.format(len(self.lines)))
        self.fmt = '{{:0{}}}'.format(shift)
        self.shift = shift + 2

        self._lock.acquire()        # <<<  LOCK
        self._w = curses.newwin(self._height, self._width, self._yoffs, self._xoffs)
        self._w.clear()
        self._w.scrollok(True)
        self.box()
        self.p = curses.panel.new_panel(self._w)
        self.p.show()
        self._lock.release()        # >>>   LOCK

    def box(self):
        self._w.attrset(curses.color_pair(DETAILS_BOX_COLOR))
        self._w.box(0, 0)
        self._w.attrset(curses.color_pair(TITLE_COLOR))
        self._w.addstr(0, (self._width - len(self._title)) // 2, self._title)
        self._w.attrset(curses.color_pair(BOT_COLOR))
        bot = " {}-{} of {} ".format(self.first, self.last, len(self.lines))
        self._w.addstr(self._height-1, (self._width - len(bot)) // 2, bot)
        self._w.move(0, 0)
        self._w.refresh()

    def reread(self):
        self.first = 1
        self.last = 1
        self.lines = []
        with open(self.filename) as f:
            while True:
                line = f.readline()
                if not line:
                    break
                self.lines.append(line.rstrip())

        shift = len('{}'.format(len(self.lines)))
        self.fmt = '{{:0{}}}'.format(shift)
        self.shift = shift + 2

        self.end()

    @cursesLock
    def refresh(self):
        self.box()

    @cursesLock
    def goto(self, line_n):
        if line_n >= len(self.lines):
            self.end(True)
        elif line_n < 1:
            self.beggining(True)
        else:
            self.first = line_n
            self.last = self.first + min(len(self.lines) - self.first, self._height-2)
            self._w.clear()
            for i in range(self.first, self.last):
                l = self.lines[i-1]
                if self.show_numbers:
                    if len(l) > self._width - self.shift - 1:
                        l = l[0:self._width-self.shift-1]
                    self._w.attrset(curses.color_pair(LINE_NUMBERS_COLOR))
                    self._w.addstr(i - self.first + 1, 1, self.fmt.format(i))
                    self._w.clrtoeol()
                    self._w.attrset(curses.color_pair(NORM_COLOR))
                    self._w.addstr(i - self.first + 1, self.shift, l)
                else:
                    if len(l) > self._width - 1:
                        l = l[0:self._width-1]
                    self._w.attrset(curses.color_pair(NORM_COLOR))
                    self._w.addstr(i - self.first + 1, 1, l)
                self._w.clrtoeol()

    def beggining(self, nolock = False):
        self.first = 1
        n = min(len(self.lines), self._height-2)
        idx = 1

        if not nolock:
            self._lock.acquire()      # <<<  LOCK
        self._w.attrset(curses.color_pair(NORM_COLOR))
        self._w.clear()
        for i in range(0,n):
            l = self.lines[idx-1]
            if self.show_numbers:
                if len(l) > self._width - self.shift - 1:
                    l = l[0:self._width-self.shift-1]
                self._w.attrset(curses.color_pair(LINE_NUMBERS_COLOR))
                self._w.addstr(idx, 1, self.fmt.format(i+1))
                self._w.clrtoeol()
                self._w.attrset(curses.color_pair(NORM_COLOR))
                self._w.addstr(idx, self.shift, l)
            else:
                if len(l) > self._width - 1:
                    l = l[0:self._width-1]
                self._w.attrset(curses.color_pair(NORM_COLOR))
                self._w.addstr(idx, 1, l)
            self._w.clrtoeol()
            idx += 1
        self.last = n
        self.box()
        if not nolock:
            self._lock.release()      # >>>   LOCK

    def end(self, nolock = False):
        idx = 1
        self.last = len(self.lines)
        if len(self.lines) > self._height + 1:
            x = len(self.lines) - self._height + 2

            if not nolock:
                self._lock.acquire()      # <<<  LOCK
            self._w.attrset(curses.color_pair(NORM_COLOR))
            self._w.clear()
            for line in self.lines[x:]:
                if self.show_numbers:
                    if len(line) > self._width - self.shift - 1:
                        line = line[0:self._width-self.shift-1]
                    self._w.attrset(curses.color_pair(LINE_NUMBERS_COLOR))
                    self._w.addstr(idx, 1, self.fmt.format(idx + x))
                    self._w.clrtoeol()
                    self._w.attrset(curses.color_pair(NORM_COLOR))
                    self._w.addstr(idx, self.shift, line)
                else:
                    if len(line) > self._width - 1:
                        line = line[0:self._width-1]
                    self._w.addstr(idx, 1, line)
                self._w.clrtoeol()
                idx += 1
            self.first = len(self.lines) - self._height + 3
            self.box()
            if not nolock:
                self._lock.release()      # >>>   LOCK

        else:

            self._lock.acquire()      # <<<  LOCK
            self._w.attrset(curses.color_pair(NORM_COLOR))
            self._w.clear()
            i = 1
            for line in self.lines:
                if self.show_numbers:
                    if len(line) > self._width - self.shift  - self.shift - 1:
                        line = line[0:self._width-self.shift-1]
                    self._w.attrset(curses.color_pair(LINE_NUMBERS_COLOR))
                    self._w.addstr(idx, 1, self.fmt.format(i))
                    self._w.clrtoeol()
                    self._w.attrset(curses.color_pair(NORM_COLOR))
                    self._w.addstr(idx, self.shift, line)
                else:
                    if len(line) > self._width - 1:
                        line = line[0:self._width-1]
                    self._w.addstr(idx, 1, line)
                self._w.clrtoeol()
                self.first = 1
                idx += 1
                i += 1
            self.box()
            self._lock.release()      # >>>   LOCK


    def hide(self):
        self._lock.acquire()         # <<<  LOCK
        self.p.hide()
        curses.panel.update_panels()
        self._lock.release()         # >>>   LOCK

    @cursesLock
    def up(self):
        if self.first > 1:
            self.first -= 1
            self.last -= 1
            self._w.scroll(-1)
            if self.show_numbers:
                self._w.attrset(curses.color_pair(LINE_NUMBERS_COLOR))
                self._w.addstr(1, 1, self.fmt.format(self.first))
                self._w.clrtoeol()
                self._w.attrset(curses.color_pair(NORM_COLOR))
                self._w.addstr(1, self.shift, self.lines[self.first-1])
            else:
                self._w.attrset(curses.color_pair(NORM_COLOR))
                self._w.addstr(1, 1, self.lines[self.first-1])
            self._w.clrtoeol()
            self.box()

    @cursesLock
    def down(self):
        if self.last < len(self.lines):
            self.first += 1
            self.last += 1
            self._w.scroll(1)
            if self.show_numbers:
                self._w.attrset(curses.color_pair(LINE_NUMBERS_COLOR))
                self._w.addstr(self._height - 2, 1, self.fmt.format(self.last))
                self._w.clrtoeol()
                self._w.attrset(curses.color_pair(NORM_COLOR))
                self._w.addstr(self._height - 2, self.shift, self.lines[self.last-1])
            else:
                self._w.attrset(curses.color_pair(NORM_COLOR))
                self._w.addstr(self._height - 2, 1, self.lines[self.last-1])
            self._w.clrtoeol()
            self.box()

    def pgup(self):
        for n in range(0,self._pg):
            self.up()

    def pgdown(self):
        for n in range(0,self._pg):
            self.down()

