import tkinter as tk
from tkinter import ttk
import serial
import threading
from datetime import datetime, timezone
import csv
import sv_ttk

class GUI_Window():

    DEFAULT_CTRL = "<LCCLCCLLU>"
    BUTTON_GRID_OPTS = {"padx": 3, "pady": 3}
    FRAME_OPTS = {"borderwidth" : 5, "relief" : "ridge", "padding" : (8,8,8,8)}
    FRAME_GRID_OPTS = {"padx" : 10, "pady" : 10}
    FRAME_TITLE_LABEL_OPTS = {"borderwidth" : 2, "relief" : "solid", "padding": (4,3,4,3)}
    FRAME_TITLE_GRID_OPTS = {"padx": 3, "pady": 3}
    SENSOR_NAME_LABEL_OPTS = {"width":15, "anchor":"w", "borderwidth":1, "relief":"solid", "padding":(4,3,4,3)}

    def __init__(self):

        self.root = tk.Tk()
        self.root.geometry('1200x700')
        self.root.title('GSEC GUI')

        sv_ttk.set_theme("dark")

        self.start_timestamp = datetime.now(timezone.utc)

        # control string as list for fast updates
        self.ctrlString = list(self.DEFAULT_CTRL)

        self.sensorData = []
        self.GSECPicoCommState = "red"
        self.LECUCommState = "red"

        # Serial
        self.port = "COM3"
        try:
            self.ser = serial.Serial(self.port, 115200, timeout=0.05, write_timeout=0.05)
            self.GSECPicoCommState = "green"
            print("Serial connected")
        except:
            print("Serial not connected — running in GUI-only mode")
            self.GSECPicoCommState = "red"
            self.ser = None

        #self.serialThread = threading.Thread(target=self.read_serial_data)
        #self.serialThread.daemon = True
        #self.serialThread.start()

        # GUI panels
        self.setup_GN2_fill_ops_panel(0,0)
        self.setup_N2O_purge_ops_panel(1,0)
        self.setup_GSECU_sensor_readouts(4,0)
        self.setup_e_stop(2,1)
        self.setup_N2O_fill_ops(0,2)
        self.setup_console(2,2)
        self.setup_COM_panel(0, 3, self.GSECPicoCommState, self.LECUCommState)
        self.setup_LECU_sensor_readouts(4,2)

        # loops
        if (self.GSECPicoCommState == "green"):
            self.root.after(100,self.ctrl_loop)
            #self.root.after(500,self.print_sensorData)
        elif ((self.GSECPicoCommState == "red")):
            self.root.after(500, self.print_ctrlString)
        
        #self.root.after(100,self.update_sensor_data)
        #self.root.after(250,self.write_sensor_data_to_file)

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
                msg = "".join(self.ctrlString) + "\n"
                self.ser.write(msg.encode())
        except Exception as e:
            print("Serial error:", e)
        finally:
            self.root.after(100, self.ctrl_loop)

    # ---------------- SERIAL ---------------- #

    def read_serial_data(self):

        while True:

            try:
                if self.ser.in_waiting:

                    data = self.ser.readline().decode().strip()
                    values = list(map(float,data.split()))

                    self.sensorData = values

            except:
                pass

    # ---------------- SEQUENCES ---------------- #

    def open_GN2_fill(self):

        self.update_ctrlString(1,'H')

        self.root.after(500,
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

        self.root.after(500,
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

        self.root.after(500,
            lambda: self.update_ctrlString(3,'O')
        )

        self.log("Open N2O Fill Valve")

    def close_N2O_fill(self):

        self.update_ctrlString(1,'H')

        self.root.after(250,
            lambda: self.update_ctrlString(3,'C')
        )

        self.root.after(1000,
            lambda: self.update_ctrlString(1,'L')
        )

        self.log("Close N2O Main Valve")

    def launch_sequence(self):

        self.log("Launch sequence start")

        self.update_ctrlString(1,'H')      # set GSECU Servo Pwr Switch high
        self.update_ctrlString(4,'H')      # set LECU Servo Pwr Switch high

        self.root.after(250,
            lambda: self.update_ctrlString(3,'C')      # close N2O Fill Valve
        )

        self.root.after(1000,
            lambda: self.update_ctrlString(1,'L')      # set GSECU Servo Pwr Switch low
        )

        self.root.after(2000,
            lambda: self.update_ctrlString(7,'H')      # set QD relay pin high
        )

        self.root.after(3000,
            lambda: self.update_ctrlString(7,'L')      # set QD relay pin low
        )

        self.root.after(8000,
            lambda: self.update_ctrlString(8,'H')      # set igniter relay pin high
        )

        self.root.after(9000,
            lambda: self.update_ctrlString(6,'O')      # open mains
        )

        self.root.after(11000,
            lambda: self.update_ctrlString(8,'L')      # set igniter relay pin low
        )

    # ---------------- PANELS ---------------- #

    def setup_COM_panel(self, c, r, GSECPicoCommState, LECUCommState):
        panel = ttk.Frame(self.root, **self.FRAME_OPTS)
        panel.grid(column=c,row=r, **self.FRAME_GRID_OPTS)

        ttk.Label(panel,text="COM Status", **self.FRAME_TITLE_LABEL_OPTS).grid(row=0,column=0, **self.FRAME_TITLE_GRID_OPTS)
        tk.Label(panel, text="GSEC Pico", bg=GSECPicoCommState).grid(row=1,column=0)
        tk.Label(panel, text="LECU", bg=LECUCommState).grid(row=2,column=0)

    def setup_GN2_fill_ops_panel(self,c,r):

        panel = ttk.Frame(self.root, **self.FRAME_OPTS)
        panel.grid(column=c,row=r, **self.FRAME_GRID_OPTS)

        ttk.Label(panel,text="GN2 Fill Ops", **self.FRAME_TITLE_LABEL_OPTS).grid(row=0,column=0, **self.FRAME_TITLE_GRID_OPTS)

        ttk.Button(panel,text="Open GN2 Fill Valve",
                   command=self.open_GN2_fill).grid(row=1,column=0, **self.BUTTON_GRID_OPTS)

        ttk.Button(panel,text="Close GN2 Fill Valve",
                   command=self.close_GN2_fill).grid(row=2,column=0, **self.BUTTON_GRID_OPTS)

    def setup_N2O_purge_ops_panel(self,c,r):

        panel = ttk.Frame(self.root, **self.FRAME_OPTS)
        panel.grid(column=c,row=r, **self.FRAME_GRID_OPTS)

        ttk.Label(panel,text="N2O Purge Ops", **self.FRAME_TITLE_LABEL_OPTS).grid(row=0,column=0, **self.FRAME_TITLE_GRID_OPTS)

        ttk.Button(panel,text="Open N2O Main Valve",
                   command=self.open_N2O_main_purge).grid(row=1,column=0, **self.BUTTON_GRID_OPTS)

        ttk.Button(panel,text="Close N2O Main Valve",
                   command=self.close_N2O_main_purge).grid(row=2,column=0, **self.BUTTON_GRID_OPTS)

    def setup_N2O_fill_ops(self,c,r):

        panel = ttk.Frame(self.root, **self.FRAME_OPTS)
        panel.grid(column=c,row=r, **self.FRAME_GRID_OPTS)

        ttk.Label(panel,text="N2O Fill Ops", **self.FRAME_TITLE_LABEL_OPTS).grid(row=0,column=0,  columnspan=2, **self.FRAME_TITLE_GRID_OPTS)

        ttk.Button(panel,text="Open N2O Fill Valve",
                   command=self.open_N2O_fill).grid(row=1,column=0, **self.BUTTON_GRID_OPTS)
        
        ttk.Button(panel,text="Close N2O Fill Valve",
                   command=self.close_N2O_fill).grid(row=2,column=0, **self.BUTTON_GRID_OPTS)

        ttk.Button(panel,text="Start Launch Sequence",
                   command=self.launch_sequence).grid(row=1,column=1, **self.BUTTON_GRID_OPTS)
        

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

    def setup_GSECU_sensor_readouts(self,c,r):

        panel = ttk.Frame(self.root, **self.FRAME_OPTS)
        panel.grid(column=c,row=r, **self.FRAME_GRID_OPTS)

        ttk.Label(panel,text="GSECU Sensor Readouts", **self.FRAME_TITLE_LABEL_OPTS).grid(row=0,column=0,columnspan=2, **self.FRAME_TITLE_GRID_OPTS)

        ttk.Label(panel, text='N2O K-Bottle PT', **self.SENSOR_NAME_LABEL_OPTS).grid(column=0, row=1, padx=3, pady=3, sticky="e")
        self.N2OKBtlPT = ttk.Label(panel,text="Waiting...")
        self.N2OKBtlPT.grid(column=1, row=1)

        ttk.Label(panel,text="N2O K Bottle PT").grid(row=1,column=0)

        self.fillLinePT = ttk.Label(panel,text="Waiting...")
        self.fillLinePT.grid(column=1,row=2)

        ttk.Label(panel,text="Fill Line PT").grid(row=2,column=0)

    def setup_LECU_sensor_readouts(self,c,r):

        panel = ttk.Frame(self.root, **self.FRAME_OPTS)
        panel.grid(column=c,row=r, **self.FRAME_GRID_OPTS)

        ttk.Label(panel,text="LECU Sensor Readouts", **self.FRAME_TITLE_LABEL_OPTS).grid(row=0,column=0,columnspan=2, **self.FRAME_TITLE_GRID_OPTS)

        self.fuelTankPT = ttk.Label(panel,text="Waiting...")
        self.fuelTankPT.grid(row=1,column=1)

        ttk.Label(panel,text="Fuel Tank PT").grid(row=1,column=0)

    # ---------------- SENSOR UPDATE ---------------- #

    def update_sensor_data(self):

        if len(self.sensorData) >= 2:

            self.N2OKBtlPT.config(text=f"{self.sensorData[0]:.2f}")
            self.fillLinePT.config(text=f"{self.sensorData[1]:.2f}")

        self.root.after(100,self.update_sensor_data)

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
            with open("engine_test_data.csv","a",newline="") as f:

                writer = csv.writer(f)
                writer.writerow(row)

        except:
            pass

        self.root.after(250,self.write_sensor_data_to_file)

    # ---------------- SAFETY ---------------- #

    def e_stop(self):

        self.ctrlString = list(self.DEFAULT_CTRL)
        self.log("E-STOP ACTIVATED")

    def on_close(self):

        try:
            self.ser.close()
        except:
            pass

        self.root.destroy()

