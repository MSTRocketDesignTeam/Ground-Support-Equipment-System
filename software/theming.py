import tkinter as tk
import tkinter.font as font


class Custom_Button():
    def __init__(self, parent, text_, action, bgColor_,**kwargs):
        self.normal_color = bgColor_
        self.text_color = 'black'
        self.hover_color = '#b0b0b0'
        self.active_color = '#94ff21'
        self.toggle_color = '#f4ea80'
        self._helv20 = font.Font(family='Helvetica', size=20)

        button = tk.Label(parent, text=text_, fg=self.text_color,
                          bg=self.normal_color, font=self._helv20, padx=15, pady=15, relief='raised')
        button.bind(
            '<Enter>', self.enter_action)
        button.bind(
            '<Leave>', self.leave_action)
        button.bind(
            '<Double-Button>', self.double_action)

        toggle = kwargs.get('toggle', False)
        if toggle:
            button.pack(side=tk.LEFT)
        else:
            button.pack(pady=5)

        self.button = button
        self.enter_flag = False
        self.action = action

        self.toggled = False

    def enter_action(self, event):
        self.enter_flag = True
        if not self.toggled:
            self.button.config(bg=self.hover_color)

    def leave_action(self, event):
        if not self.toggled:
            self.enter_flag = False
            self.button.config(bg=self.normal_color)

    def double_action(self, event):
        if self.enter_flag:
            self.button.config(bg=self.active_color)
            self.action()

        self.enter_flag = False

    def set_text(self, text_):
        self.button.config(text=text_)

    def set_toggle(self, state):
        self.toggled = state
        if state:
            self.button.config(bg=self.toggle_color)
        else:
            self.button.config(bg=self.normal_color)


class Custom_Panel():
    def __init__(self, root, row_, column_, text_):
        self.panel = tk.LabelFrame(root, text=text_, bg='black',
                                   fg='white', padx=15, pady=15, relief='groove', width=300, height=300)
        self.panel.grid(row=row_, column=column_,
                        sticky='nsew', padx=5, pady=5)


class Custom_Toggle():
    def __init__(self, parent, label_text, handle_toggle,  **kwargs):
        frame = tk.LabelFrame(parent, relief='solid',
                              text=label_text, bg='black', fg='white', labelanchor='n', font=get_font('h14'))
        frame.pack()

        self.on = Custom_Button(
            frame, 'On', self.toggle_on, 'white', toggle=True)
        self.off = Custom_Button(
            frame, 'Off', self.toggle_off, 'white', toggle=True)

        # Default toggle:
        default_state = kwargs.get('default', 'off')

        self.on.set_toggle(default_state == 'on')
        self.off.set_toggle(default_state == 'off')

        self.handle_toggle = handle_toggle

    def toggle_on(self):
        self.on.set_toggle(True)
        self.off.set_toggle(False)

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
