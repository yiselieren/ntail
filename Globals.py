# Global consts
LEFT_BW     = 1
RIGHT_BW    = 1
TOP_BW      = 1
BOT_BW      = 1
PROBE_DELAY = 1.0
VERT_MARGIN = 5
HORIZONT_MARGIN = 8

# Initialize after curses.intscr()
USABLE_LINES   = 0
DRAWABLE_LINES = 0
USABLE_COLS    = 0
DRAWABLE_COLS  = 0

# Colors
FOCUS_COLOR           = 1
NO_FOCUS_COLOR        = 2
TITLE_COLOR           = 3
REG_COLOR             = 4
BOT_COLOR             = 5
SPEC_COLOR            = 6
NORM_COLOR            = 7
ERR_COLOR             = 8
HELP_COLOR            = 9
YESNO_SEL_COLOR       = 10
YESNO_NSEL_COLOR      = 11
DETAILS_BOX_COLOR     = 12
POPUP_BOX_COLOR       = 13
LINE_NUMBERS_COLOR    = 14
PROMPT_COLOR          = 15
INP_FIELD_COLOR       = 16
LAST_TIME_COLOR1      = 17
LAST_TIME_COLOR2      = 18
FOCUS_COLOR_R         = 19
NO_FOCUS_COLOR_R      = 20

# For popup windows
ok = "[ OK ]"
cancel = " [ Cancel ] "
yes = "[ Yes ]"
no = "[ No ]"
no_offs = 3
cancel_offs = 3
int_field = 7

DBG = './debug.log'
def dbg(s):
    with open(DBG, "a") as f:
        f.write(s + '\n')
