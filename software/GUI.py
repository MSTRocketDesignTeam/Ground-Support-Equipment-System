import tkinter as tk
import tkinter.ttk as ttk
import serial
import threading
from datetime import datetime, timezone
import sys
from theming import Custom_Button, Custom_Panel, Custom_Toggle, get_font
import sv_ttk

from controller import Controller

class GUI_Window():
    '''
    Sets up the launch GUI
    '''

    def __init__(self):
        root = tk.Tk()

        root.geometry('1200x700')
        # root.resizable(False, False)
        root.title('GSEC GUI')

        self.root = root

        self.start_timestamp = datetime.now(timezone.utc)
        self.controller = Controller(self.start_timestamp)

        # Setup basic GUI elements
        self.setup_console(0)
        self.setup_caution_panel(0, 1)
        self.setup_sensor_readouts(0, 2)
        self.setup_modes_panel(1, 2)
        self.setup_kill_panel(1, 3)
        self.setup_ox_monitor(2, 0)
        self.setup_auto_control_section(2, 1)
        self.setup_manual_control_section(2, 2)
        
        #Start serial line and specify the Pi Pico's USB/Serial address
        self.ser = serial.Serial('/dev/ttyACM0', 115200)
        
        # Start reading from the serial port in a separate thread
        self.serialThread = threading.Thread(target=self.read_serial_data)
        self.serialThread.daemon = True  # Make sure this thread exits when the app closes
        self.serialThread.start()
        
        self.sensorData = []
        self.root.after(100, self.update_sensor_data)

        root.configure(bg='black')

        self.exit_attempt = False

        self.mode = None
        #sv_ttk.set_theme("dark")

        self.root.mainloop()

    def setup_modes_panel(self, row_, column_):
        '''Sets up a panel with buttons for toggling auto launch interlock modes.'''

        mp = Custom_Panel(self.root, row_, column_, 'Modes')

        Custom_Toggle(mp.panel, 'Interlocks', self.run('set_interlocks'))
        Custom_Toggle(mp.panel, 'Auto Mode', self.run('set_auto'))
        
        
    def read_serial_data(self):
        while True:
            if self.ser.in_waiting > 0:
                # Read the data sent from the Pico
                data = self.ser.readline().decode('utf-8').strip()
                # Split the received string into individual integers
                self.sensorData = list(map(int, data.split()))
                
    

    def setup_caution_panel(self, row_, column_):
        '''
        Generates a panel with caution circles for cautions
        falling into the category of master, comms, sensors,
        or GUI. Other issues will be reported directly to the
        console.
        '''
        cp = Custom_Panel(self.root, row_, column_, 'Status Lights')
        cp.panel.grid(row=0, column=column_, rowspan=2)

        canvas = tk.Canvas(cp.panel, width=250, height=450)

        master_caution = canvas.create_oval(30, 15, 80, 65)
        canvas.create_text(55, 80, text='Master')
        canvas.itemconfig(master_caution, fill='green')

        sensors_caution = canvas.create_oval(30, 115, 80, 165)
        canvas.create_text(55, 180, text='Sensors')
        canvas.itemconfig(sensors_caution, fill='green')

        comms_caution = canvas.create_oval(130, 15, 180, 65)
        canvas.create_text(155, 80, text='Comms')
        canvas.itemconfig(comms_caution, fill='green')

        gui_caution = canvas.create_oval(130, 115, 180, 165)
        canvas.create_text(155, 180, text='GUI')
        canvas.itemconfig(gui_caution, fill='green')

        canvas.pack()

        self.caution_panel = {
            'master': master_caution,
            'sensors': sensors_caution,
            'coms': comms_caution,
            'GUI': gui_caution,
            'canvas': canvas
        }

        self.caution_states = {
            'master': 0,
            'sensors': 0,
            'coms': 0,
            'GUI': 0
        }

    def set_caution(self, caution_type, state):

        color_states = ['green', 'yellow', 'red']
        self.caution_states[caution_type] = state

        self.caution_panel['canvas'].itemconfig(
            self.caution_panel[caution_type], fill=color_states[state])

        if state > self.caution_states['master']:
            self.caution_states['master'] = state

            self.caution_panel['canvas'].itemconfig(
                self.caution_panel['master'], fill=color_states[state])

    def setup_kill_panel(self, row_, column_):
        '''
        Provides a button to exit the program and a
        button to immediately restore the program to a
        safe operating condition and then exit (E-stop)
        '''

        mp = Custom_Panel(self.root, row_, column_, 'Program Termination')

        Custom_Button(mp.panel, 'Emergency Stop', self.run('estop'), 'red')
        Custom_Button(mp.panel, 'Exit Program', self.prg_exit, 'white')
        Custom_Button(mp.panel, 'Dump Oxidizer', self.run('dump'), 'white')

        self.set_control_mode = None
        self.set_interlocks = None

        self.go_emergency_stop = None
        self.go_safe_exit = None

    def setup_auto_control_section(self, row_, column_):
        '''
        Provides a button to run the automatic launch sequencer which
        will fire commands to light the igniter and open the main valves.
        '''
        ap = Custom_Panel(self.root, row_, column_, 'Automated Controls')

        Custom_Button(ap.panel, 'Start launch sequence', self.run('launch'), 'white')

    def setup_manual_control_section(self, row_, column_):
        '''
        Provides buttons for oxidizer dump as well as manual
        ignition and manual main valve actuation.
        '''
        mp = Custom_Panel(self.root, row_, column_, 'Manual Controls')

        Custom_Button(mp.panel, 'Igniter', self.run('ignite'), 'white')
        
        Custom_Button(mp.panel, 'Open Mains', self.run('open_mains'), 'white')


    def setup_sensor_readouts(self, row_, column_):
        '''Displays all sensor readouts in table format.'''

        sp = Custom_Panel(self.root, row_, column_, 'Sensors')

        self.fuel_tank_PT = tk.Label(
            sp.panel, text='Fuel tank PT         waiting...', font=get_font('c12'))
        self.ox_tank_PT = tk.Label(
            sp.panel, text='Ox tank PT           waiting...', font=get_font('c12'))
        self.fuel_venturi_flow_PT = tk.Label(
            sp.panel, text='Fuel Venturi PT     waiting...', font=get_font('c12'))
        self.ox_venturi_flow_PT = tk.Label(
            sp.panel, text='Ox Venturi PT       waiting...', font=get_font('c12'))
        self.chamber_PT = tk.Label(
            sp.panel, text='Chamber PT           waiting... ', font=get_font('c12'))
        self.ox_TC = tk.Label(
            sp.panel, text='Ox TC                waiting... ', font=get_font('c12'))
        self.chamber_TC = tk.Label(
            sp.panel, text='Chamber TC           waiting... ', font=get_font('c12'))

        sensor_list = [self.fuel_tank_PT, self.ox_tank_PT, self.fuel_venturi_flow_PT,
                       self.ox_venturi_flow_PT, self.chamber_PT, self.ox_TC, self.chamber_TC]

        for sensor in sensor_list:
            sensor.pack(anchor='w', pady=2)
        sp.panel.pack_propagate(False)

    def update_sensor_data(self):
        if self.sensorData:
                sensorDataString = list(map(str, self.sensorData))
                for i in range(len(sensorDataString)):
                        if (int(sensorDataString[i]) < 10):
                                sensorDataString[i] = "0" + sensorDataString[i]
                self.fuel_tank_PT.config(text=f"Fuel Tank PT: {sensorDataString[0]} psi")
                self.ox_tank_PT.config(text=f"Ox Tank PT: {sensorDataString[1]} psi")
                self.fuel_venturi_flow_PT.config(text=f"Fuel Venturi PT: {sensorDataString[2]} psi")
                self.ox_venturi_flow_PT.config(text=f"Ox Venturi PT: {sensorDataString[3]} psi")
                self.chamber_PT.config(text=f"Chamber PT: {sensorDataString[4]} psi")
                self.ox_TC.config(text=f"Ox TC: {sensorDataString[5]} F")
                self.chamber_TC.config(text=f"Chamber TC: {sensorDataString[6]} F")
        self.root.after(250, self.update_sensor_data) #recursively call this function every 250ms


    def setup_ox_monitor(self, row_, column_):
        '''
        Displays the oxidizer button to actuate fill
        and estimated fill state.
        '''

        op = Custom_Panel(self.root, row_, column_, 'Nitrous Fill')

        s = ttk.Style()
        s.configure('TProgressbar', thickness=20)

        Custom_Button(op.panel, 'Open Fill Valve', self.run('open_fill'), 'white')
        Custom_Button(op.panel, 'Close Fill Valve', self.run('close_fill'), 'white')
        fill_time = tk.Label(
            op.panel, text='Time to fill:\t\t-- Not Started --')
        progress_label = tk.Label(op.panel, text='Fill progress:')
        progress = ttk.Progressbar(op.panel, orient='horizontal',
                                   length=250, mode='determinate')

        fill_time.pack(pady=5, anchor='w')
        progress_label.pack(anchor='w')
        progress.pack()

        self.ox_progress_bar = progress

    def setup_console(self, column_):
        '''
        Sets up the console for later messages to be logged and
        the launch sequence to be recorded.
        '''

        cp = Custom_Panel(self.root, 0, column_, 'Console')
        cp.panel.grid(row=0, column=column_, rowspan=2)

        console = tk.Text(cp.panel, width=40, height=20,
                          wrap='word', font=get_font('c16'))

        console.pack()
        console.configure(state='disabled')

        self.console = console

        self.run_console_log('STARTUP', 0)

    def run_console_log(self, text, state):
        '''
        Logs a message to the console and to the corresponding
        record file for future reference.

        text - the message to be logged
        state - the message status to be logged:
            0 >>> Standard operation
            1 >>> Caution
            2 >>> Warning
            3 >>> No status
        '''

        if text == 'STARTUP':
            fmt = '%m-%d-%Y, %H:%M:%S UTC : CONSOLE STARTUP\n\n'
            text = 'Missouri S&T RDT Ground Control\n\n' \
                '>> Standard Operation\nxx Caution\n!! Warning\n\n' \
                'ALL BUTTONS MUST BE DOUBLE CLICKED\n'
            state = 3
            self.console_file = open(self.start_timestamp.strftime(
                'GSECLOG_%m_%d_%Y_%H_%M_%S.txt'), 'a+')
        else:
            fmt = '%H:%M:%S : '

        state_indicators = ['>> ', 'xx ', '!! ', '']

        str_date_time = datetime.now(timezone.utc).strftime(fmt)

        full_text = state_indicators[state] + str_date_time + text + '\n'
        self.console.configure(state='normal')
        self.console.insert(tk.END, full_text)
        self.console.configure(state='disabled')

        try:
            self.console_file.write(full_text)
        except:
            self.console.configure(state='normal')
            self.console.insert(
                tk.END, '!! WARNING - The console is no longer logging to the output file. '
                'Please restart the application or manually record events logged to the console.')
            self.console.configure(state='disabled')

            self.set_caution('GUI', 1)

        self.console.yview_pickplace('end')

    def prg_exit(self):
        '''
        Immediately terminates program operation without running safing procedures
        '''

        try:
            self.run_console_log('Program exited', 1)
            self.console_file.close()
            self.exit_attempt = True
        except:
            print('error')
            self.run_console_log(
                'An error occured while trying to exit the program. This probably occured because of an error in saving the log file. To proceed anyway, please click this button again.', 2)

        if self.exit_attempt:
            sys.exit(0 if self.exit_attempt == False else 1)
        else:
            self.exit_attempt = True

    def run(self, function_name):
        '''
        Handles exectution of commands to the controller.
        '''

        func = getattr(self.controller, function_name)

        return lambda *args: self.run_console_log(*func(*args))

    def set_mode(self, mode):
        assert (mode in ['launch', 'test'])

        self.mode = mode
