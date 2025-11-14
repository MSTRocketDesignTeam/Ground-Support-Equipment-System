import random

class Controller():
    '''
    This class handles the bulk of work for the system by packaging low 
    level micropython functions into events that can be triggered by the GUI.
    '''

    def __init__(self, timestamp):

        # Setup controller state map:
        #  0 >>> Nominal
        #  1 >>> Caution
        #  2 >>> Warning
        # -1 >>> Unknown
        #
        # False >>> Off
        # True  >>> On

        self.state = {
            'fill_valve': -1,
            'ox_valve': -1,
            'fuel_valve': -1,

            'auto_mode': False,
            'interlocks': False,

            'arm': False,
            'igniter_lit': False,

            'LEC_link_status': -1,
            'LEC_status': -1,
            'GUI_status': -1,

            'fuel_tank_pt': -1,
            'ox_tank_pt': -1,
            'fuel_venturi_pt': -1,
            'ox_venturi_pt': -1,
            'chamber_pt': -1,
            'ox_tc': -1,
            'chamber_tc': -1,

            'error_override_flag': False,
            'emergency_stop_flag': False,

            'tank_fill': 0,
        }

        self.record = {}

    def estop(self):
        '''
        Runs the emergency stop procedure to safe the entire
        system as quickly as possible.
        '''

        self.state['estop'] = 1

        # Insert calls to micropython

        message = 'E-Stop Button Pressed'
        status = 2
        return (message, status)

    def open_fill(self):
        '''
        Attempts to open the fill valve and handles
        the corresponding error code from micropython.
        '''
        message = 'Fill valve opened'
        status = 2

        return (message, status)

    def close_fill(self):
        '''
        Attempts to close the oxidizer valves and handles the
        corresponding error code from micropython.
        '''
        message = 'Fill valve closed'
        status = 2
        return (message, status)

    def launch(self):
        message = 'Launch button pressed'
        status = 2

        return (message, status)

    def readSensors(self, numSensors):
        sensorReadings = []
        for _ in range(numSensors):
            sensorReadings.append(random.randint(100, 999))
        return sensorReadings
    
    def update_sensor_data(self, myRoot, myLabels):
        sensorReadings = self.readSensors(len(myLabels))
        myLabels[0].config(text=f"Fuel Tank PT: {sensorReadings[0]} psi")
        myLabels[1].config(text=f"Ox tank PT: {sensorReadings[1]} psi")
        myLabels[2].config(text=f"Fuel Venturi PT: {sensorReadings[2]} psi")
        myLabels[3].config(text=f"Ox Venturi PT: {sensorReadings[3]} psi")
        myLabels[4].config(text=f"Chamber PT: {sensorReadings[4]} psi")
        myLabels[5].config(text=f"Ox TC {sensorReadings[5]} F")
        myLabels[6].config(text=f"Chamber TC {sensorReadings[6]} F")
        
        myRoot.after(100, lambda: self.update_sensor_data(myRoot, myLabels))

    def get_fill_state(self):
        '''Returns the fill state of the oxidizer tank as an ordered tuple.'''
        return (.3, 60)

    def record_state(self):
        pass

    def ignite(self):
        message = 'Ignite button pressed'
        status = 2

        return (message, status)

    def dump(self):
        message = 'Dump button pressed'
        status = 2

        return (message, status)

    def open_mains(self):
        message = 'Mains open button pressed'
        status = 2

        return (message, status)

    def set_interlocks(self, state):
        self.state['interlocks'] = state

        
        message = 'Interlocks mode set to ' + ('off', 'on')[state]
        status = 2

        return (message, status)

    def set_auto(self, state):
        self.state['auto_mode'] = state

        message = 'Auto mode set to ' + ('off', 'on')[state]
        status = 2

        return (message, status)
