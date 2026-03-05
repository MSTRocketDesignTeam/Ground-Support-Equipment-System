import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import sv_ttk
import serial
import serial
import time



# On Raspberry Pi, USB serial devices usually appear as /dev/ttyUSB0 or /dev/ttyACM0
port = "/dev/ttyACM0"
baud_rate = 115200  # Match the device's baud rate
ser = serial.Serial(port, baud_rate, timeout=1)
time.sleep(2) #Let device initialize


#First index is the fuel control character, second index is the ox control character
# 'F' is closed, 'T' is open
ser.write(b"FF")   
ser.flush()

def runFuel():
	openTime = int(runTime.get(1.0, "end-1c"))
	ser.write(b"TF")
	ser.flush()
	time.sleep(openTime)
	ser.write(b"FF")
	ser.flush()
	
def runOx():
	openTime = int(runTime.get(1.0, "end-1c"))
	ser.write(b"FT")
	ser.flush()
	time.sleep(openTime)
	ser.write(b"FF")
	ser.flush()

def runBoth():
	openTime = int(runTime.get(1.0, "end-1c"))
	ser.write("TT".encode('utf-8'))
	ser.flush()
	time.sleep(openTime)
	ser.write(b"FF")
	ser.flush()


root = tk.Tk()
root.geometry('700x700')
root.resizable(True, True)
root.title('Cold Flow GUI')

#RDT Logo initialization
rdtLogo = Image.open(r"../assetsAndImages/RDT_LOGO.png")
resizedImage = rdtLogo.resize((500, 150))
rdtImagePhoto = ImageTk.PhotoImage(resizedImage)
rdtLogoLabel = ttk.Label(root, image=rdtImagePhoto)

#Run Time widgets initialization
runTimeFrame = ttk.Frame(root, borderwidth=5, relief="solid")
runTime = tk.Text(runTimeFrame, height = 1, width = 5)
runTimeLabel = ttk.Label(runTimeFrame, width=20, text="Test Flow Time (seconds): ")
runTimeLabel.pack()
runTime.pack()

#Control buttons initialization
runFuelButton = ttk.Button(root, text = "Run Fuel Line Cold Flow", command=lambda: runFuel())
runOxButton = ttk.Button(root, text = "Run Ox Line Cold Flow", command=lambda: runOx())
runBothLinesButton = ttk.Button(root, text = "Run Both Lines Cold Flow", command=lambda: runBoth())

#Arrange all widgets in grid
runTimeFrame.grid(row=3, column=1, padx=10, pady=10)
runFuelButton.grid(row=0, column=0, padx=10, pady=10)
runOxButton.grid(row=0, column=1, padx=10, pady=10)
runBothLinesButton.grid(row=0, column=2, padx=10, pady=10)
rdtLogoLabel.grid(row=5, column=1, padx=10, pady=10)

sv_ttk.set_theme("dark")
root.mainloop()

#Clean up
fuelServoLine.release()
oxServoLine.release()

