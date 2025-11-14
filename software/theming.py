import tkinter as tk
import tkinter.font as font
from tkinter import ttk
from tkinter import BooleanVar

class Custom_CheckButton:


    def __init__(self, parent, text_, action,default=False, **kwargs):
        self.action = action
        self.state = tk.BooleanVar(value=default)
        self.basetext = text_
        self.button = ttk.Checkbutton(parent, text=text_, variable=self.state)
        self.button.bind('<Button-1>', self.block_click, add='+')
        self.button.bind('<Double-Button-1>', self.on_click)
        if kwargs.get('toggle', False):
            self.button.pack(side='left')
        else:
            self.button.pack(pady=5)

    def on_click(self, event):
        self.action()
        return "break"  

    def set_text(self, text_):
        self.button.config(text=text_)

    def set_toggle(self, state):
        self.toggled = bool(state)
        try:
            self.state.set(bool(state))
        except Exception:
            pass

    def block_click(self, event):
        return "break"



class Custom_Button:



    def __init__(self, parent, text_, action, default=False, **kwargs):
        self.action = action
        self.toggled = bool(default)
        self.basetext = text_
        self.button = ttk.Button(parent, text=text_)
        self.button.bind('<Double-Button-1>', self.on_click)
        toggle = kwargs.get('toggle', False)
        if toggle:
            self.button.pack(side='left')
        else:
            self.button.pack(pady=5)

    def on_click(self, event):
        self.action()

    def set_text(self, text_):
        self.button.config(text=text_)

    def set_toggle(self, state):
        self.toggled = state



    def enter_action(self, event):
        self.enter_flag = True

    def leave_action(self, event):
        if not self.toggled:
            self.enter_flag = False

    def double_action(self, event):
        if self.enter_flag:
            self.action()
        self.enter_flag = False

    def set_text(self, text_):
        self.button.config(text=text_)

    def set_toggle(self, state):
        self.toggled = state
        if state:
            self.button.config()

class Custom_Panel():
    def __init__(self, root, row_, column_, text_):
        self.panel = ttk.LabelFrame(root, text=text_, relief='groove')
        self.panel.grid(row=row_, column=column_,
                        sticky='nsew')


class Custom_Toggle():
    def __init__(self, parent, label_text, handle_toggle, default='off', **kwargs):
        frame = ttk.LabelFrame(parent, relief='solid',
                              text=label_text, labelanchor='n')
        frame.pack()
        # normalize incoming default (accept 'on'/'off' or boolean)
        if isinstance(default, str):
            is_on = (default == 'on')
        else:
            is_on = bool(default)

        # create checkbuttons with initial states
        self.on = Custom_CheckButton(frame, 'On', self.toggle_on, default=is_on, toggle=True)
        self.off = Custom_CheckButton(frame, 'Off', self.toggle_off, default=not is_on, toggle=True)

        self.handle_toggle = handle_toggle

    def toggle_on(self):
        self.off.set_toggle(False)
        self.on.set_toggle(True)

        self.handle_toggle(True)

    def toggle_off(self):
        self.on.set_toggle(False)
        self.off.set_toggle(True)

        self.handle_toggle(False)


def get_font(font_string):
    '''
    Returns the font specified by the font string.

    The first character specifies the font, and the remaining characters specify the size.

    Supported fonts:
    'h' -> 'Helvetica'
    'c' -> 'Courier'

    Examples:
    font_string = 'c12' (Courier 12pt)
    font_string = 'h16' (Helvetica 16pt)

    '''
    font_families = {
        'c': 'Courier',
        'h': 'Helvetica'
    }

    return font.Font(family=font_families[font_string[0]], size=int(font_string[1:]))
