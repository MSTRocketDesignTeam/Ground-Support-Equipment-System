import gpiod
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import sv_ttk
 
chip = gpiod.Chip('gpiochip4')

#servo line initialization
fuelServoPin = 2
fuelServoLine = chip.get_line(fuelServoPin)
fuelServoLine.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
fuelServoLine.set_value(1) #"Initialize" the pin at high, to account for the fact that some raspberry pi GPIO pins (like pin 2) are set to high upon bootup by the kernel. Adjust logic accordingly, if GPIO pin selections are changed.

oxServoPin = 3
oxServoLine = chip.get_line(oxServoPin)
oxServoLine.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
oxServoLine.set_value(1)


def runFuel():
	openTime = int(runTime.get(1.0, "end-1c"))
	fuelServoLine.set_value(0)
	time.sleep(openTime)
	fuelServoLine.set_value(1)
	
def runOx():
	openTime = int(runTime.get(1.0, "end-1c"))
	oxServoLine.set_value(0)
	time.sleep(openTime)
	oxServoLine.set_value(1)

def runBoth():
	openTime = int(runTime.get(1.0, "end-1c"))
	fuelServoLine.set_value(0)
	oxServoLine.set_value(0)
	time.sleep(openTime)
	fuelServoLine.set_value(1)
	oxServoLine.set_value(1)


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
