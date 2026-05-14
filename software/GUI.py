import tkinter as tk
from tkinter import ttk
import serial
import threading
from datetime import datetime, timezone
import csv
import sv_ttk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

# Sensor Locations
# 0: N2O Bottle PT
# 1: Fill Line PT
# 2: Purge Bottle PT
# 3: Wet Mass Load Cell
# 4: Purge Bottle TC
# 5: GSEC Internal TC
# 6: N2O Bottle TC

# Format: (slope, intercept)
sensor_scales = [
        (0.00023718752,-2.12623638812),
        (0.00023718752,-2.12623638812),
        (0.00023718752,-2.12623638812),
        (1,0),
        (0,0),
        (0,0),
        (0,0),
        (0.00023718752,-2.12623638812),
        (0.00023718752,-2.12623638812),
        (0.00023718752,-2.12623638812),
        (0.00023718752,-2.12623638812),
        (0.00023718752,-2.12623638812),
        (0.00023718752,-2.12623638812),
        (0.00023718752,-2.12623638812),
        (0,0),
        (0,0),
        (0,0)
]


class GUI_Window():
    ESTOP_CTRL   = "<HCCHCCLLU>"
    DEFAULT_CTRL = "<LCCLCCLLU>"
    BUTTON_GRID_OPTS = {"padx": 3, "pady": 3}
    FRAME_OPTS = {"borderwidth" : 5, "relief" : "ridge", "padding" : (8,8,8,8)}
    FRAME_GRID_OPTS = {"padx" : 10, "pady" : 10}
    FRAME_TITLE_LABEL_OPTS = {"borderwidth" : 2, "anchor" : "center", "relief" : "solid", "padding": (4,3,4,3)}
    FRAME_TITLE_GRID_OPTS = {"padx": 3, "pady": 3}
    TRM_LNCH_SEQ_LBL_OPTS = {"borderwidth":1, "relief":"solid"}
    SNSR_NAME_LABEL_OPTS = {"width":15, "anchor":"w", "borderwidth":1, "relief":"solid", "padding":(4,3,4,3)}
    SNSR_RDING_LABEL_OPTS = {"width":10, "anchor":"w", "borderwidth":1, "relief":"solid", "padding":(4,3,4,3)}
    SNSR_UNIT_LABEL_OPTS = {"width":5, "anchor":"w", "borderwidth":1, "relief":"solid", "padding":(4,3,4,3)}
    TMR_DESC_LABEL_OPTS = {"width":25, "anchor":"w", "borderwidth":2, "relief":"solid", "padding":(4,3,4,3)}
    TMR_LABEL_OPTS = {"width":3, "anchor":"w", "borderwidth":2, "relief":"solid", "padding":(4,3,4,3)}
    DEF_PREBRN_PRGE_FILL_TM = 140
    DEF_PSTBRN_PRGE_FILL_TM = 7
    DEF_N2O_PRGE_TM = 3
    DEF_N2O_FILL_TIME = 300
    
    def __init__(self):

        self.root = tk.Tk()
        self.root.geometry('1920x1080')
        self.root.title('GSEC GUI')
        sv_ttk.set_theme("dark")

        self.start_timestamp = datetime.now(timezone.utc)

        # control string as list for fast updates
        self.ctrlString = list(self.DEFAULT_CTRL)

        self.sensorData = []
        self.GSECPicoCommState = "red"
        self.LECUCommState = "red"
        self.purgeFillTmr = self.DEF_PREBRN_PRGE_FILL_TM
        self.N2OMainPurgeTmr = self.DEF_N2O_PRGE_TM
        self.N2OFillTmr = self.DEF_N2O_FILL_TIME
        self.fired = False
        self.QD_actuated = False
        self.lastSent = self.ctrlString

        # Serial
        self.port = "/dev/ttyACM0"
        try:
            self.ser = serial.Serial(self.port, 115200, timeout=0.05, write_timeout=0.05)
            self.GSECPicoCommState = "green"
            self.serialThread = threading.Thread(target=self.read_serial_data)
            self.serialThread.daemon = True
            self.serialThread.start()
            self.sensor_lock = threading.Lock()
            print("Serial connected")
        except:
            print("Serial not connected — running in GUI-only mode")
            self.GSECPicoCommState = "red"
            self.ser = None


        # GUI panels
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=1)
        self.root.columnconfigure(0,weight=1)
        self.root.columnconfigure(1,weight=1)
        self.root.columnconfigure(2,weight=1)
        self.setup_GN2_fill_ops_panel(0,0)
        self.setup_N2O_purge_ops_panel(1,0)
        self.setup_N2O_fill_ops(2,0)
        self.setup_console(0,1)
        self.setup_GSECU_sensor_readouts(1,1)
        self.setup_LECU_sensor_readouts(2,1)
        #self.setup_term_lnch_seq_stat_bar(0,2)
        self.setup_COM_panel(1, 2, self.GSECPicoCommState, self.LECUCommState)
        self.setup_e_stop(2,2)
        

        # loops
        if (self.GSECPicoCommState == "green"):
            self.root.after(100, self.ctrl_loop)
            self.root.after(100, self.update_sensor_data)
            #self.root.after(100, self.write_sensor_data_to_file)
        elif ((self.GSECPicoCommState == "red")):
            self.root.after(500, self.print_ctrlString)
        self.root.after(1000, self.update_purge_fill_tmr)
        self.root.after(1000, self.update_N2O_main_purge_tmr)
        self.root.after(1000, self.update_N2O_fill_tmr)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    # ---------------- CONTROL STRING ---------------- #

    def update_ctrlString(self,index,value):
        self.ctrlString[index] = value

    def print_ctrlString(self):
        print(self.ctrlString)
        #print(self.ser.readline().decode().strip())
        self.root.after(500, self.print_ctrlString)

    def print_sensorData(self):
        self.read_serial_data()
        print(self.sensorData)
        self.root.after(500, self.print_sensorData)

    def ctrl_loop(self):
        try:
            if self.ser and self.ser.is_open:
                self.GSECPicoCommState = "green"
                self.GSECPicoCommStateLabel.config(bg=self.GSECPicoCommState)
                msg = "".join(self.ctrlString)
                if msg != self.lastSent:
                    self.ser.write(msg.encode())
                    self.lastSent = msg
        except Exception as e:
            self.GSECPicoCommState = "red"
            self.GSECPicoCommStateLabel.config(bg=self.GSECPicoCommState)
            print("Serial error:", e)
        finally:
            self.root.after(100, self.ctrl_loop)

    # ---------------- SERIAL ---------------- #

    def read_serial_data(self):
        while True:
            try:
                if self.ser and self.ser.in_waiting:
                    prelimData = self.ser.readline()
                    data = prelimData.decode(errors='ignore').strip()
                    

                    if data:
                        values = [int(x.strip()) for x in data.split(',')]
                        
                        # Apply Scales
                        for i, scale in enumerate(sensor_scales):
                                values[i] = values[i]*scale[0] + scale[1]

                        # Optional: validate packet length
                        if len(values) == 17:
                            with self.sensor_lock:
                                self.sensorData = values
                        else:
                            print("Bad packet length:", data)

            except Exception as e:
                pass

    # ---------------- LAUNCH/FIRE SEQUENCE TIMERS ---------------- #

    def update_purge_fill_tmr(self):
        if (self.ctrlString[2] == 'O'):
            self.purgeFillTmr -= 1
            self.purgeFillTmrLabel.config(text=self.purgeFillTmr)
        else:
            if (self.fired):
                self.purgeFillTmr = self.DEF_PSTBRN_PRGE_FILL_TM
            else:
                self.purgeFillTmr = self.DEF_PREBRN_PRGE_FILL_TM
            self.purgeFillTmrLabel.config(text=self.purgeFillTmr)
        self.root.after(1000, self.update_purge_fill_tmr)

    def update_N2O_main_purge_tmr(self):
        if (self.ctrlString[5] == 'O'):
            self.N2OMainPurgeTmr -= 1
            self.N2OPurgeTmrLabel.config(text=self.N2OMainPurgeTmr)
        else:
            self.N2OMainPurgeTmr = self.DEF_N2O_PRGE_TM
            self.N2OPurgeTmrLabel.config(text=self.N2OMainPurgeTmr)
        self.root.after(1000, self.update_N2O_main_purge_tmr)

    def update_N2O_fill_tmr(self):
        if (self.ctrlString[3] == 'O'):
            self.N2OFillTmr -= 1
            self.N2OFillTmrLabel.config(text=self.N2OFillTmr)
        else:
            self.N2OFillTmr = self.DEF_N2O_FILL_TIME
            self.N2OFillTmrLabel.config(text=self.N2OFillTmr)
        self.root.after(1000, self.update_N2O_fill_tmr)
        

    # ---------------- SEQUENCES ---------------- #

    def open_GN2_fill(self):

        self.update_ctrlString(1,'H')

        self.root.after(250,
            lambda: self.update_ctrlString(2,'O')
        )

        self.log("Open GN2 Fill Valve")

    def close_GN2_fill(self):

        self.update_ctrlString(1,'H')

        self.root.after(250,
            lambda: self.update_ctrlString(2,'C')
        )

        self.root.after(1000,
            lambda: self.update_ctrlString(1,'L')
        )

        self.log("Close GN2 Fill Valve")

    def open_N2O_main_purge(self):

        self.update_ctrlString(4,'H')

        self.root.after(250,
            lambda: self.update_ctrlString(5,'O')
        )

        self.log("Open N2O Main Valve")

    def close_N2O_main_purge(self):

        self.update_ctrlString(4,'H')

        self.root.after(250,
            lambda: self.update_ctrlString(5,'C')
        )

        self.root.after(1000,
            lambda: self.update_ctrlString(4,'L')
        )

        self.log("Close N2O Main Valve")

    def open_N2O_fill(self):
        self.update_ctrlString(1,'H')

        self.root.after(250,
            lambda: self.update_ctrlString(3,'O')
        )

        self.log("Open N2O Fill Valve")
        
    def actuate_qd(self):
            self.QD_actuated = True
            self.log("Actuate QD")

    def close_N2O_fill(self):

        self.update_ctrlString(1,'H')

        self.root.after(250,
            lambda: self.update_ctrlString(3,'C')
        )

        self.root.after(1000,
            lambda: self.update_ctrlString(1,'L')
        )
        
        self.root.after(2750,
                lambda: self.update_ctrlString(7,'H')
        )
        
        self.root.after(4000,
                lambda: [self.update_ctrlString(7,'L'), self.actuate_qd()]
        )

        self.log("Close N2O Main Valve")
        
    def launch_sequence(self):
        if self.QD_actuated:
                self.log("Launch sequence start")
                self.fired = True
                #self.update_ctrlString(1,'H')      # set GSECU Servo Pwr Switch high
                self.update_ctrlString(4,'H')      # set LECU Servo Pwr Switch high
                self.update_ctrlString(8,'H')
                self.ignition.config(bg="green")
                
                self.root.after(500,
                    lambda: [self.update_ctrlString(6,'O'), self.mainsOpened.config(bg="green")]      # open mains and update terminal launch sequence status bar accordingly
                )

                self.root.after(2000,
                    lambda: self.update_ctrlString(8,'L')      # set igniter relay pin low
                )
        else:
                self.log("Unable to start launch sequence - QD not actuated")

    # ---------------- PANELS ---------------- #

    def setup_COM_panel(self, c, r, GSECPicoCommState, LECUCommState):
        panel = ttk.Frame(self.root, **self.FRAME_OPTS)
        panel.grid(column=c,row=r, **self.FRAME_GRID_OPTS)

        ttk.Label(panel,text="COM Status", **self.FRAME_TITLE_LABEL_OPTS).grid(row=0,column=0, **self.FRAME_TITLE_GRID_OPTS)
        self.GSECPicoCommStateLabel = tk.Label(panel, text="GSEC Pico", bg=GSECPicoCommState)
        self.GSECPicoCommStateLabel.grid(row=1,column=0)
        self.LECUCommStateLabel = tk.Label(panel, text="LECU", bg=LECUCommState)
        self.LECUCommStateLabel.grid(row=2,column=0)

    def setup_GN2_fill_ops_panel(self,c,r):

        panel = ttk.Frame(self.root, **self.FRAME_OPTS)
        panel.grid(column=c,row=r, **self.FRAME_GRID_OPTS)

        ttk.Label(panel, text="Purge Fill Ops", **self.FRAME_TITLE_LABEL_OPTS).grid(row=0, column=0, columnspan=2, **self.FRAME_TITLE_GRID_OPTS)
        ttk.Label(panel, text="Purge Fill Time Remaining (s):", **self.TMR_DESC_LABEL_OPTS).grid(row=1, column=0)
        self.purgeFillTmrLabel = ttk.Label(panel, text=self.purgeFillTmr, **self.TMR_LABEL_OPTS)
        self.purgeFillTmrLabel.grid(row=1, column=1)

        ttk.Button(panel,text="Open GN2 Fill Valve",
                   command=self.open_GN2_fill).grid(row=2, column=0, columnspan=2, **self.BUTTON_GRID_OPTS)

        ttk.Button(panel,text="Close GN2 Fill Valve",
                   command=self.close_GN2_fill).grid(row=3, column=0, columnspan=2, **self.BUTTON_GRID_OPTS)

    def setup_N2O_purge_ops_panel(self,c,r):

        panel = ttk.Frame(self.root, **self.FRAME_OPTS)
        panel.grid(column=c,row=r, **self.FRAME_GRID_OPTS)

        ttk.Label(panel,text="N2O Purge Ops", **self.FRAME_TITLE_LABEL_OPTS).grid(row=0,column=0, **self.FRAME_TITLE_GRID_OPTS)
        ttk.Label(panel, text="N2O Purge Time Remaining (s):", **self.TMR_DESC_LABEL_OPTS).grid(row=1, column=0)
        self.N2OPurgeTmrLabel = ttk.Label(panel, text=self.N2OMainPurgeTmr, **self.TMR_LABEL_OPTS)
        self.N2OPurgeTmrLabel.grid(row=1, column=1)

        ttk.Button(panel,text="Open N2O Main Valve",
                   command=self.open_N2O_main_purge).grid(row=2,column=0, **self.BUTTON_GRID_OPTS)

        ttk.Button(panel,text="Close N2O Main Valve",
                   command=self.close_N2O_main_purge).grid(row=3,column=0, **self.BUTTON_GRID_OPTS)

    def setup_N2O_fill_ops(self,c,r):

        panel = ttk.Frame(self.root, **self.FRAME_OPTS)
        panel.grid(column=c,row=r, **self.FRAME_GRID_OPTS)

        ttk.Label(panel,text="N2O Fill Ops", **self.FRAME_TITLE_LABEL_OPTS).grid(row=0,column=0,  columnspan=2, **self.FRAME_TITLE_GRID_OPTS)
        ttk.Label(panel, text="N2O Fill Time Remaining (s):", **self.TMR_DESC_LABEL_OPTS).grid(row=1, column=0)
        self.N2OFillTmrLabel = ttk.Label(panel, text=self.N2OFillTmr, **self.TMR_LABEL_OPTS)
        self.N2OFillTmrLabel.grid(row=1, column=1)

        ttk.Button(panel,text="Open N2O Fill Valve",
                   command=self.open_N2O_fill).grid(row=2,column=0, **self.BUTTON_GRID_OPTS)
        
        ttk.Button(panel,text="Close N2O Fill Valve",
                   command=self.close_N2O_fill).grid(row=2,column=1, **self.BUTTON_GRID_OPTS)
        ttk.Button(panel,text="Start Launch Sequence",
                   command=self.launch_sequence).grid(row=3,column=1, **self.BUTTON_GRID_OPTS)
                           
    def setup_term_lnch_seq_stat_bar(self, c, r):
        panel = ttk.Frame(self.root, **self.FRAME_OPTS)
        panel.grid(column=c,row=r, **self.FRAME_GRID_OPTS)

        ttk.Label(panel,text="Terminal Launch Sequence Status Bar", **self.FRAME_TITLE_LABEL_OPTS).grid(row=0,column=0,  columnspan=4, **self.FRAME_TITLE_GRID_OPTS)
        self.ignition = tk.Label(panel, text="Ignition", bg="orange", fg="blue", **self.TRM_LNCH_SEQ_LBL_OPTS)
        self.ignition.grid(row=1,column=2)
        self.mainsOpened = tk.Label(panel, text="Mains Opened", bg="orange", fg="blue", **self.TRM_LNCH_SEQ_LBL_OPTS)
        self.mainsOpened.grid(row=1,column=3)

    def setup_e_stop(self,c,r):
        panel = ttk.Frame(self.root, **self.FRAME_OPTS)
        panel.grid(column=c,row=r)

        btn = tk.Button(panel,
                        text="E-STOP",
                        bg="red",
                        fg="white",
                        font=("Segoe UI",14,"bold"),
                        command=self.e_stop)

        btn.grid(row=0,column=0)

    # ---------------- SENSORS ---------------- #
    
    #def setup_WMLC_plot(self,c,r):
     # TODO: implement WMLC plot   
            

    def setup_GSECU_sensor_readouts(self,c,r):

        panel = ttk.Frame(self.root, **self.FRAME_OPTS)
        panel.grid(column=c,row=r, **self.FRAME_GRID_OPTS)

        ttk.Label(panel,text="GSECU Sensor Readouts", width=34, **self.FRAME_TITLE_LABEL_OPTS).grid(row=0,column=0,columnspan=3, **self.FRAME_TITLE_GRID_OPTS)

        ttk.Label(panel, text="N2O K-Bottle PT", **self.SNSR_NAME_LABEL_OPTS).grid(row=1, column=0, padx=3, pady=3, sticky="e")
        self.N2OKBtlPT = ttk.Label(panel,text="Waiting...", **self.SNSR_RDING_LABEL_OPTS)
        self.N2OKBtlPT.grid(row=1, column=1)
        ttk.Label(panel, text="psi", **self.SNSR_UNIT_LABEL_OPTS).grid(row=1,column=2)

        ttk.Label(panel,text="Fill Line PT", **self.SNSR_NAME_LABEL_OPTS).grid(row=2, column=0)
        self.fillLinePT = ttk.Label(panel,text="Waiting...", **self.SNSR_RDING_LABEL_OPTS)
        self.fillLinePT.grid(row=2, column=1)
        ttk.Label(panel, text="psi", **self.SNSR_UNIT_LABEL_OPTS).grid(row=2,column=2)

        ttk.Label(panel,text="Purge K-Bottle PT", **self.SNSR_NAME_LABEL_OPTS).grid(row=3, column=0)
        self.PurgeKBtlPT = ttk.Label(panel,text="Waiting...", **self.SNSR_RDING_LABEL_OPTS)
        self.PurgeKBtlPT.grid(row=3, column=1)
        ttk.Label(panel, text="psi", **self.SNSR_UNIT_LABEL_OPTS).grid(row=3,column=2)

        ttk.Label(panel,text="Wet Mass LC", **self.SNSR_NAME_LABEL_OPTS).grid(row=4, column=0)
        self.wetMassLC = ttk.Label(panel,text="Waiting...", **self.SNSR_RDING_LABEL_OPTS)
        self.wetMassLC.grid(row=4, column=1)
        ttk.Label(panel, text="lbm", **self.SNSR_UNIT_LABEL_OPTS).grid(row=4,column=2)

        ttk.Label(panel,text="Purge K-Bottle TC", **self.SNSR_NAME_LABEL_OPTS).grid(row=5, column=0)
        self.PurgeKBtlTC = ttk.Label(panel,text="Waiting...", **self.SNSR_RDING_LABEL_OPTS)
        self.PurgeKBtlTC.grid(row=5, column=1)
        ttk.Label(panel, text="F", **self.SNSR_UNIT_LABEL_OPTS).grid(row=5,column=2)

        ttk.Label(panel,text="GSECU Internal TC", **self.SNSR_NAME_LABEL_OPTS).grid(row=6, column=0)
        self.GSECUintTC = ttk.Label(panel,text="Waiting...", **self.SNSR_RDING_LABEL_OPTS)
        self.GSECUintTC.grid(row=6, column=1)
        ttk.Label(panel, text="F", **self.SNSR_UNIT_LABEL_OPTS).grid(row=6,column=2)

        ttk.Label(panel,text="N2O K-Bottle TC", **self.SNSR_NAME_LABEL_OPTS).grid(row=7, column=0)
        self.N2OKBtlTC = ttk.Label(panel,text="Waiting...", **self.SNSR_RDING_LABEL_OPTS)
        self.N2OKBtlTC.grid(row=7, column=1)
        ttk.Label(panel, text="F", **self.SNSR_UNIT_LABEL_OPTS).grid(row=7,column=2)

        ttk.Label(panel,text="GSECU Net Current", **self.SNSR_NAME_LABEL_OPTS).grid(row=8, column=0)
        self.GSECUINA237 = ttk.Label(panel,text="Waiting...", **self.SNSR_RDING_LABEL_OPTS)
        self.GSECUINA237.grid(row=8, column=1)
        ttk.Label(panel, text="Amps", **self.SNSR_UNIT_LABEL_OPTS).grid(row=8,column=2)


    def setup_LECU_sensor_readouts(self,c,r):

        panel = ttk.Frame(self.root, **self.FRAME_OPTS)
        panel.grid(column=c,row=r, **self.FRAME_GRID_OPTS)

        ttk.Label(panel,text="LECU Sensor Readouts", width=34, **self.FRAME_TITLE_LABEL_OPTS).grid(row=0,column=0,columnspan=3, **self.FRAME_TITLE_GRID_OPTS)

        ttk.Label(panel, text="Fuel Tank PT", **self.SNSR_NAME_LABEL_OPTS).grid(row=1, column=0, padx=3, pady=3, sticky="e")
        self.fuelTankPT = ttk.Label(panel,text="Waiting...", **self.SNSR_RDING_LABEL_OPTS)
        self.fuelTankPT.grid(row=1, column=1)
        ttk.Label(panel, text="psi", **self.SNSR_UNIT_LABEL_OPTS).grid(row=1,column=2)

        ttk.Label(panel,text="Ox Tank PT", **self.SNSR_NAME_LABEL_OPTS).grid(row=2, column=0)
        self.oxTankPT = ttk.Label(panel,text="Waiting...", **self.SNSR_RDING_LABEL_OPTS)
        self.oxTankPT.grid(row=2, column=1)
        ttk.Label(panel, text="psi", **self.SNSR_UNIT_LABEL_OPTS).grid(row=2,column=2)

        ttk.Label(panel,text="Fuel dPT", **self.SNSR_NAME_LABEL_OPTS).grid(row=3, column=0)
        self.fueldPT = ttk.Label(panel,text="Waiting...", **self.SNSR_RDING_LABEL_OPTS)
        self.fueldPT.grid(row=3, column=1)
        ttk.Label(panel, text="psi", **self.SNSR_UNIT_LABEL_OPTS).grid(row=3,column=2)

        ttk.Label(panel,text="Ox dPT", **self.SNSR_NAME_LABEL_OPTS).grid(row=4, column=0)
        self.oxdPT = ttk.Label(panel,text="Waiting...", **self.SNSR_RDING_LABEL_OPTS)
        self.oxdPT.grid(row=4, column=1)
        ttk.Label(panel, text="psi", **self.SNSR_UNIT_LABEL_OPTS).grid(row=4,column=2)

        ttk.Label(panel,text="Ox Manifold PT", **self.SNSR_NAME_LABEL_OPTS).grid(row=5, column=0)
        self.oxManPT = ttk.Label(panel,text="Waiting...", **self.SNSR_RDING_LABEL_OPTS)
        self.oxManPT.grid(row=5, column=1)
        ttk.Label(panel, text="psi", **self.SNSR_UNIT_LABEL_OPTS).grid(row=5,column=2)

        ttk.Label(panel,text="Fuel Manifold PT", **self.SNSR_NAME_LABEL_OPTS).grid(row=6, column=0)
        self.fuelManPT = ttk.Label(panel,text="Waiting...", **self.SNSR_RDING_LABEL_OPTS)
        self.fuelManPT.grid(row=6, column=1)
        ttk.Label(panel, text="psi", **self.SNSR_UNIT_LABEL_OPTS).grid(row=6,column=2)

        ttk.Label(panel,text="Chamber PT", **self.SNSR_NAME_LABEL_OPTS).grid(row=7, column=0)
        self.chamberPT = ttk.Label(panel,text="Waiting...", **self.SNSR_RDING_LABEL_OPTS)
        self.chamberPT.grid(row=7, column=1)
        ttk.Label(panel, text="psi", **self.SNSR_UNIT_LABEL_OPTS).grid(row=7,column=2)

        ttk.Label(panel,text="Chamber Shell TC1", **self.SNSR_NAME_LABEL_OPTS).grid(row=8, column=0)
        self.CSTC1 = ttk.Label(panel,text="Waiting...", **self.SNSR_RDING_LABEL_OPTS)
        self.CSTC1.grid(row=8, column=1)
        ttk.Label(panel, text="F", **self.SNSR_UNIT_LABEL_OPTS).grid(row=8,column=2)

        ttk.Label(panel,text="Chamber Shell TC2", **self.SNSR_NAME_LABEL_OPTS).grid(row=9, column=0)
        self.CSTC2 = ttk.Label(panel,text="Waiting...", **self.SNSR_RDING_LABEL_OPTS)
        self.CSTC2.grid(row=9, column=1)
        ttk.Label(panel, text="F", **self.SNSR_UNIT_LABEL_OPTS).grid(row=9,column=2)

        ttk.Label(panel,text="N2O Tank TC", **self.SNSR_NAME_LABEL_OPTS).grid(row=10, column=0)
        self.N2OTankTC = ttk.Label(panel,text="Waiting...", **self.SNSR_RDING_LABEL_OPTS)
        self.N2OTankTC.grid(row=10, column=1)
        ttk.Label(panel, text="F", **self.SNSR_UNIT_LABEL_OPTS).grid(row=10,column=2)

        ttk.Label(panel,text="LECU Net Current", **self.SNSR_NAME_LABEL_OPTS).grid(row=11, column=0)
        self.LECUINA237 = ttk.Label(panel,text="Waiting...", **self.SNSR_RDING_LABEL_OPTS)
        self.LECUINA237.grid(row=11, column=1)
        ttk.Label(panel, text="Amps", **self.SNSR_UNIT_LABEL_OPTS).grid(row=11,column=2)

    # ---------------- SENSOR UPDATE ---------------- #

    def update_sensor_data(self):

        with self.sensor_lock:
            data = self.sensorData.copy()

        if len(data) >= 17:
            self.N2OKBtlPT.config(text=f"{data[0]:.2f}")
            self.fillLinePT.config(text=f"{data[1]:.2f}")
            self.PurgeKBtlPT.config(text=f"{data[2]:.2f}")
            self.wetMassLC.config(text=f"{data[3]:.2f}")
            self.PurgeKBtlTC.config(text=f"{data[4]:.2f}")
            self.GSECUintTC.config(text=f"{data[5]:.2f}")
            self.N2OKBtlTC.config(text=f"{data[6]:.2f}")
            self.fuelTankPT.config(text=f"{data[7]:.2f}")
            self.oxTankPT.config(text=f"{data[8]:.2f}")
            self.fueldPT.config(text=f"{data[9]:.2f}")
            self.oxdPT.config(text=f"{data[10]:.2f}")
            self.oxManPT.config(text=f"{data[11]:.2f}")
            self.fuelManPT.config(text=f"{data[12]:.2f}")
            self.chamberPT.config(text=f"{data[13]:.2f}")
            self.CSTC1.config(text=f"{data[14]:.2f}")
            self.CSTC2.config(text=f"{data[15]:.2f}")
            self.N2OTankTC.config(text=f"{data[16]:.2f}")

        self.root.after(100, self.update_sensor_data)

    # ---------------- CONSOLE ---------------- #

    def setup_console(self,c,r):

        panel = ttk.Frame(self.root, **self.FRAME_OPTS)
        panel.grid(column=c,row=r, **self.FRAME_GRID_OPTS)

        ttk.Label(panel,text="Console", **self.FRAME_TITLE_LABEL_OPTS).pack()

        self.console = tk.Text(panel,height=10,width=50)
        self.console.pack()

    def log(self,msg):

        t = datetime.now().strftime("%H:%M:%S")
        self.console.insert(tk.END,f"[{t}] {msg}\n")
        self.console.see(tk.END)

    # ---------------- CSV LOGGING ---------------- #

    def write_sensor_data_to_file(self):
        timestamp = (datetime.now(timezone.utc)-self.start_timestamp).total_seconds()

        row = [timestamp] + self.sensorData

        try:
            with open(f"data{self.start_timestamp.strftime('%m-%d-%Y %H:%M:%S')}.csv","a",newline="") as f:

                writer = csv.writer(f)
                writer.writerow(row)

        except:
            pass

        self.root.after(100,self.write_sensor_data_to_file)

    # ---------------- SAFETY ---------------- #

    def e_stop(self):
        self.update_ctrlString(1,'H')      # set GSECU Servo Pwr Switch high
        self.update_ctrlString(4,'H')      # set LECU Servo Pwr Switch high
        self.fired = False
        self.QD_actuated = False
        self.ignition.config(bg="orange")
        self.mainsOpened.config(bg="orange")
        self.root.after(100, lambda: setattr(self, "ctrlString", list(self.ESTOP_CTRL)))
        self.root.after(1100, lambda: setattr(self, "ctrlString", list(self.DEFAULT_CTRL)))
        self.log("E-STOP ACTIVATED")

    def on_close(self):

        try:
            self.ser.close()
        except:
            pass

        self.root.destroy()


