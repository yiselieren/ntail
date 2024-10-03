#
# General window
# ------------
#
import time
import datetime
import curses
import curses.panel
import sys
import os

from Globals import *

class Win:
    def cursesLock(function):
        def wrapper(self,*args,**kwargs):
            if self._lock:
                self._lock.acquire()
            try:
                return function(self,*args,**kwargs)
            finally:
                if self._lock:
                    self._lock.release()
        return wrapper

    def __init__(self, lock, title, h, w, x, y, filename, is_focus, draw_bot_cnt = True):
        self._title = ' ' + title + ' '
        self._height = h
        self._lock = lock
        self._width = w
        self._xoffs = x
        self._yoffs = y
        self._focus = is_focus
        self._draw_bot_cnt = draw_bot_cnt
        self.filename = filename
        self.visible_height = h - 2
        self.visible_width = w - 2
        self.text = []
        self.first = 1
        self.last = 1
        self.first_visible_idx = TOP_BW
        self.last_visible_idx = self._height  - TOP_BW - BOT_BW
        self.total = 0
        self.idx = self.first_visible_idx
        self.last_time = ''
        self.last_time_sec = time.time()
        self.auto_refresh = True

        if self._lock:
            self._lock.acquire()  # <<< LOCK
        self._w = curses.newwin(self._height, self._width, self._yoffs, self._xoffs)
        self._w.clear()
        max_title = self._width - LEFT_BW - RIGHT_BW - 2
        if len(self._title) > max_title:
            self._title = self._title[0:max_title]
        self.set_cursor()
        self._w.scrollok(True)
        self.box(is_focus)
        if self._lock:
            self._lock.release()  # >>> LOCK

    def win(self):
        return self._w
    def move(self, x, y):
        self._w.move(y, x)
    def refresh(self):
        self.box(self._focus)
    def set_color(self, c):
        self._w.attrset(curses.color_pair(c))
    def pr(self, x, y, s):
        self._w.addstr(y, x, s)
    def prc(self, x, y, s, color):
        self.set_color(color)
        self._w.addstr(y, x, s)
        self._w.clrtoeol()
        self._w.refresh()
    def set_cursor(self):
        self.move(0, 0)

    def set_total(self, n):
        self.total = n
        self.first = n+1
        self.last = n

    def addlasttime(self):
        self.last_time = ' ' + time.strftime('%Y-%m-%d %H:%M:%S') + ' '
        self.last_time_sec = time.time()

    @cursesLock
    def refresh_lock(self):
        self.box(self._focus)

    @cursesLock
    def clear(self):
        self.first = 1
        self.last = 1
        self.first_visible_idx = TOP_BW
        self.last_visible_idx = self._height  - TOP_BW - BOT_BW
        self.total = 0
        self.idx = self.first_visible_idx
        self._w.clear()

    @cursesLock
    def add(self, s):
        if self.idx > self.last_visible_idx:
            self._w.scroll()
            self.idx = self.last_visible_idx
            self.first += 1
        if len(s) > self.visible_width - 1:
            s = s[0:self.visible_width-1]
        self.prc(LEFT_BW , self.idx, s, NORM_COLOR)
        self.last += 1
        self.total += 1
        self.idx += 1
        self.box(self._focus)

    def box(self, is_focus = False):
        self._focus = is_focus
        self._w.attrset(curses.color_pair(FOCUS_COLOR if self._focus else NO_FOCUS_COLOR))
        self._w.box(0, 0)
        title = ' {} '.format(self._title)
        sizes = '{}x{} '.format(self.visible_width, self.visible_height)
        self._w.attrset(curses.color_pair(TITLE_COLOR))
        self._w.addstr(0, (self._width - len(title)) // 2, title)
        self._w.attrset(curses.color_pair(REG_COLOR))
        self._w.addstr(0, (self._width - len(title)) // 2 + len(title), sizes)
        if self._draw_bot_cnt:
            bot = " {}-{} of {} ".format(self.first, self.last, self.total)
            self._w.attrset(curses.color_pair(BOT_COLOR))
            bot_x =  3
            self._w.addstr(self._height-1, bot_x, bot)
            if self.auto_refresh:
                lt0 = 'Last modified:'
                lt1 = '{} '.format(self.last_time)
                lt2 = '{} ago '.format(datetime.timedelta(seconds=int(time.time() - self.last_time_sec + 0.5)))
                tl = len(lt0) + len(lt1) + len(lt2)
                if self.last_time != '' and (tl) <= (self._width - bot_x - len(bot) - 3):
                    bot_x = self._width - 3 - tl
                    self._w.attrset(curses.color_pair(FOCUS_COLOR_R if self._focus else NO_FOCUS_COLOR_R))
                    self._w.addstr(self._height-1, bot_x, lt0)
                    bot_x += len(lt0)
                    self._w.attrset(curses.color_pair(LAST_TIME_COLOR1))
                    self._w.addstr(self._height-1, bot_x, lt1)
                    bot_x = self._width - 3 - len(lt2)
                    self._w.attrset(curses.color_pair(LAST_TIME_COLOR2))
                    #self._w.attrset(curses.color_pair(FOCUS_COLOR_R if self._focus else NO_FOCUS_COLOR_R))
                    self._w.addstr(self._height-1, bot_x, lt2)
            else:
                lt1 = '{} '.format(self.last_time)
                if self.last_time != '' and len(lt1) <= (self._width - bot_x - len(bot) - 3):
                    bot_x = self._width - 3 - len(lt1)
                    self._w.attrset(curses.color_pair(LAST_TIME_COLOR1))
                    self._w.addstr(self._height-1, bot_x, lt1)
        self.set_cursor()
        self._w.refresh()

    def special_box(self, color):
        self._w.attrset(curses.color_pair(color))
        self._w.box(0, 0)
        title = ' {} '.format(self._title)
        self._w.attrset(curses.color_pair(TITLE_COLOR))
        self._w.addstr(0, (self._width - len(title)) // 2, title)
        self.set_cursor()
        self._w.refresh()

    def in_focus(self):
        self.box(True);
    def out_of_focus(self):
        self.box(False);
    def focus(self):
        return self._focus
