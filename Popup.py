#
# Popup window
# ------------
#
import time
import curses
import curses.panel
import sys
import os

from Globals import *
import Win

class Popup:

    # Lock wrapper
    def cursesLock(function):
        def wrapper(self,*args,**kwargs):
            self.lock.acquire()
            try:
                return function(self,*args,**kwargs)
            finally:
                self.lock.release()
        return wrapper

    def __init__(self, lock):
        self.lock = lock

    @cursesLock
    def get_int(self, s, title, prompt, width, height, x_offs, y_offs):
        okcancel_len = len(ok) + cancel_offs + len(cancel)

        msg_height = 7
        msg_width = len(prompt) + int_field + 6
        msg_width = max(msg_width, len(title) + 6, okcancel_len + 6)
        x = (width - msg_width) // 2 + x_offs
        y = (height - msg_height) // 2 + y_offs
        w = Win.Win(None, title, msg_height, msg_width, x, y, '', True, False)
        w.clear()
        x = 4
        y = 2
        w.set_color(PROMPT_COLOR)
        w.pr(x, y, prompt)
        x += len(prompt) + 2
        inp_x = x
        inp_y = y
        w.set_color(INP_FIELD_COLOR)
        w.pr(x, y, ' ' * int_field)
        y += 2
        x = x_offs + (msg_width - okcancel_len) // 2
        self._redraw_okcancel(w, x, y, True)

        p = curses.panel.new_panel(w.win())
        p.show()
        rc = ''
        rc1 = True
        inp_idx = 0
        while True:
            c = s.getch()
            if c >= ord('0') and c <= ord('9'):
                w.set_color(INP_FIELD_COLOR)
                w.pr(inp_x + inp_idx, inp_y, chr(c))
                rc += chr(c)
                self._redraw_okcancel(w, x, y, rc1)
                inp_idx += 1
            elif c == curses.KEY_BACKSPACE:
                if inp_idx > 0:
                    inp_idx -= 1
                    rc = rc[0:len(rc)-1]
                    w.set_color(INP_FIELD_COLOR)
                    w.pr(inp_x + inp_idx, inp_y, ' ')
                    self._redraw_okcancel(w, x, y, rc1)
            elif c == ord('\t'):
                rc1 = not rc1
                self._redraw_okcancel(w, x, y, rc1)
            elif rc1 and c == curses.KEY_RIGHT:
                rc1 = False
                self._redraw_okcancel(w, x, y, False)
            elif not rc1 and c == curses.KEY_LEFT:
                rc1 = True
                self._redraw_okcancel(w, x, y, True)
            elif c == ord('\n') or c == curses.KEY_ENTER:
                break
        p.hide()
        curses.panel.update_panels()
        return 0 if rc =='' else int(rc), rc1

    @cursesLock
    def ok(self, title, width, height, x_offs, y_offs, msg, color):
        y, msg_width, w = self.show_multi(title, width, height, x_offs, y_offs, msg.split('\n'), color)
        x = (msg_width - len(ok)) // 2
        w.prc(x, y, ok, YESNO_SEL_COLOR)
        w.special_box(POPUP_BOX_COLOR)
        w.move(x, y)

        p = curses.panel.new_panel(w.win())
        p.show()
        w.win().getch()
        p.hide()
        curses.panel.update_panels()

    def _redraw_yesno(self, w, x, y, v):
        w.prc(x, y, yes, YESNO_SEL_COLOR if v else YESNO_NSEL_COLOR)
        x += len(yes) + no_offs
        w.prc(x, y, no, YESNO_NSEL_COLOR if v else YESNO_SEL_COLOR)
        w.special_box(POPUP_BOX_COLOR)

    def _redraw_okcancel(self, w, x, y, v):
        w.prc(x, y, ok, YESNO_SEL_COLOR if v else YESNO_NSEL_COLOR)
        x += len(ok) + cancel_offs
        w.prc(x, y, cancel, YESNO_NSEL_COLOR if v else YESNO_SEL_COLOR)
        w.special_box(POPUP_BOX_COLOR)

    @cursesLock
    def yesno(self, s, title, width, height, x_offs, y_offs, msg, color, def_answ = True):
        yesno_len = len(yes) + no_offs + len(no)
        y, msg_width, w = self.show_multi(title, width, height, x_offs, y_offs, msg.split('\n'), color)
        y += 1
        x = x_offs + (msg_width - yesno_len) // 2
        self._redraw_yesno(w, x, y, def_answ)

        p = curses.panel.new_panel(w.win())
        p.show()
        rc = def_answ
        while True:
            c = s.getch()
            if c == ord('y') or c == ord('Y'):
                rc = True
                break
            elif c == ord('n') or c == ord('N'):
                rc = False
                break
            elif rc and c == curses.KEY_RIGHT:
                rc = False
                self._redraw_yesno(w, x, y, rc)
            elif not rc and c == curses.KEY_LEFT:
                rc = True
                self._redraw_yesno(w, x, y, rc)
            elif c == ord('\n') or c == curses.KEY_ENTER:
                break
        p.hide()
        curses.panel.update_panels()
        return rc

    def show_multi(self, title, width, height, x_offs, y_offs, msg, color):
        msg_height = len(msg) + 6
        msg_width = 0
        for m in msg:
            if len(m) > msg_width:
                msg_width = len(m)
        msg_width += 6
        x = (width - msg_width) // 2 + x_offs
        y = (height - msg_height) // 2 + y_offs
        w = Win.Win(None, title, msg_height, msg_width, x, y, '', True, False)
        w.clear()
        w.set_color(color)
        x = 2
        y = 1
        for m in msg:
            w.pr(x, y, m)
            y += 1
        y += 1
        return y, msg_width, w

