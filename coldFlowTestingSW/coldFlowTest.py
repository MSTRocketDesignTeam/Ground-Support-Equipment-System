#import gpiod
import time
import sv_ttk
import tkinter as tk
from tkinter import ttk
#chip = gpiod.Chip('gpiochip4')
#servoPin = 2
#servoLine = chip.get_line(servoPin)
#servoLine.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)


def runFuel():
	openTime = int(runTime.get(1.0, "end-1c"))
	print(openTime + 7)
	#fuelServoLine.set_value(1)
	#delay() find a better "sleep" function to use than sleep()
	#fuelServoLine.set_value(0)
	return
	
def runOx():
	openTime = int(runTime.get(1.0, "end-1c"))
	print(openTime + 7)
	#oxServoLine.set_value(1)
	#delay() find a better "sleep" function to use than sleep()
	#oxServoLine.set_value(0)
	return

def runBoth():
	openTime = int(runTime.get(1.0, "end-1c"))
	print(openTime + 7)
	#fuelServoLine.set_value(1)
	#oxServoLine.set_value(1)
	#delay() find a better "sleep" function to use than sleep()
	#fuelServoLine.set_value(0)
	#oxServoLine.set_value(0)
	return


pwd = input("Enter password: ")
while (pwd != "12345"):
	pwd = input("Enter password: ")


root = tk.Tk()
root.geometry('700x700')
root.resizable(True, True)
root.title('Cold Flow GUI')

runTime = tk.Text(root, height = 5, width = 20)
runFuelButton = ttk.Button(root, text = "Run Fuel Line Cold Flow", command=lambda: runFuel())
runOxButton = ttk.Button(root, text = "Run Ox Line Cold Flow", command=lambda: runOx())
runBothLinesButton = ttk.Button(root, text = "Run Both Lines Cold Flow", command=lambda: runBoth())
	
#runTime.pack()
#runFuelButton.pack(ipadx=5, ipady=5, expand=True)
#runOxButton.pack(ipadx=5, ipady=5, expand=True)
#runBothLinesButton.pack(ipadx=5, ipady=5, expand=True)
	
runTime.grid(row=1, column=1)
runFuelButton.grid(row=0, column=0)
runOxButton.grid(row=0, column=1)
runBothLinesButton.grid(row=0, column=2)


sv_ttk.set_theme("dark")
root.mainloop()

#servoLine.release()
