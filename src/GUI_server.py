#!/usr/bin/env python
# Note: In some IDLE the identation can be produce a error, just change the identation for the correct one of this file.

import Tkinter as tk
import ttk
from Tkinter import StringVar
import tkFileDialog
from ttk import Frame, Style
import time
from time import sleep
import threading
import random
import Queue
import sys
import select
import signal
import socket               # Import socket module
from numpy import*
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from numpy import*
from numpy.linalg import*
from scipy import interpolate
from tkMessageBox import *
import select

"""Maximum number of elements in the array_a for plotting"""
maxd = 1000000
"""Maximun number of elemets that can be seen in the plot"""
maxp = 200
"""array of the elemets obtained (acceleration)"""
array_a = zeros((3,maxd));
"""array of the elemets obtained (rotation)"""
array_r = zeros((3,maxd));
"""Visualization array_a"""
index_a = zeros((1,1));
"""Visualization array_r"""
index_r = zeros((1,1));

def decode(line):
        """Acceleration decodification"""
        """Return values: success, option, value1, value2, value3"""
        """option = 0 for aceleration data, then value1 = acceleration x, value2 = acceleration y, value3 = acceleration z"""
        """option = 1 for gyroscope data, then value1 = rotation x, value2 = rotationy, value3 = rotation z"""
        line_list = line.split(";")
        if(line_list[0] == 'a'):
                if(len(line_list)==5 and line_list[4] != ''):
                        x = line_list[2]
                        y = line_list[3]
                        z = line_list[4]
                        return True,0,x,y,z
        if(line_list[0] == 'y'):
                if(len(line_list)==5 and line_list[4] != ''):
                        x = line_list[2]
                        y = line_list[3]
                        z = line_list[4]
                        return True,1,x,y,z
        return False,0,0,0,0

class GuiPart:
    def __init__(self, master, stopserver, startserver,maxp):
            """Constructor"""
            self.master = master
            self.initUI(stopserver,startserver)
            self.maxp=maxp
            self.initsample = 0
            """Init value used to save a sample"""
            self.finalsample = 200
            """Final value used to save a sample"""
            self.recording = False
            """Indicate when the gesture are recording"""
            self.count = 0
            """Variable to see if the folder it was already selected"""
            self.folderselected = False

    def initUI(self,stopserver,startserver):
                """Definition of the GUI"""
                master = self.master
                self.master.title("WearAMI online")
                self.openButton = tk.Button(master, text = 'Start server', width = 30 , height = 3, command = startserver).grid(row=1,column=0, padx = 10, pady = 10)
                self.closelButton = tk.Button(master, text = 'Stop server', width = 30 , height = 3, command = stopserver).grid(row=2,column=0, padx = 10, pady = 10)
                self.plotButton = tk.Button(master, text = 'Plot Online', width = 30 , height = 3, command = self.see).grid(row=3,column=0, padx = 10, pady = 10)
                self.getButton = tk.Button(master, text = 'Get gesture', width = 30 , height = 3, command = self.getGesture).grid(row=4,column=0, padx = 10, pady = 10)
                self.saveButton = tk.Button(master, text = 'Save gesture', width = 30 , height = 3, command = self.save).grid(row=5,column=0, padx = 10, pady = 10)

                self.figure = Figure(figsize=(5,5), dpi=100)
                """Figure variable to plot with matplotlib"""
                self.canvas = FigureCanvasTkAgg(self.figure, master)
                #self.toolbar = NavigationToolbar2TkAgg(self.canvas, master)
                self.canvas.get_tk_widget().grid(row=1,column=1,rowspan = 5,padx = 10, pady = 10)
                #self.toolbar.grid(row=6,column=1)
                self.canvas.draw()
                off = tk.Scale(self.master, from_=200, to=1000, orient=tk.HORIZONTAL, resolution=10, length=300, command = self.changex, label = 'X label').grid(row=6,column=0)
                self.v = 5
                self.radio1 = tk.Radiobutton(self.master, text="Gyroscope", variable=self.v, command = self.showGyro).grid(row=8,column=1, padx = 10, pady = 10)
                self.radio2 = tk.Radiobutton(self.master, text="Accelerometer", variable=self.v, command = self.showAcce).grid(row=8,column=2, padx = 10, pady = 10)
                self.show = 1

    def showGyro(self):
            """Show the data of the Gyroscope"""
            self.show = 0
            print 0

    def showAcce(self):
            """Show the data of the Accelerometer"""
            self.show = 1
            print 1

    def see(self):
        """New thread to plot the data"""
        #self.plotButton['state']=tk.DISABLED
        self.thread2 = threading.Thread(target=self.plotData)
        self.thread2.start()

    def changex(self,val):
        """Change the x axis dimension"""
        self.maxp = float(val)

    def getGesture(self):
        """Save a gesture"""
        if (self.recording==False):
                self.initsample_a = index_a[0,0]
                self.initsample_r = index_r[0,0]
                self.recording=True
                print "Recording data..."
        else:
                self.finalsample_a = index_a[0,0]
                self.finalsample_r = index_r[0,0]
                self.recording=False
                self.plotsampleData()

    def save(self):
            """Save sample"""
            if(self.folderselected == False):
                    self.folder=tkFileDialog.askdirectory()
                    self.folderselected =True
            sample = transpose(array_a[:,(self.initsample_a):self.finalsample_a])
            savetxt("Tests/acc(" + str(self.count+1) +').txt', sample, delimiter=',', fmt='%.5f')
            sample = transpose(array_r[:,(self.initsample_r):self.finalsample_r])
            savetxt("Tests/gyr(" + str(self.count+1) +').txt', sample, delimiter=',', fmt='%.5f')
            print "Sample number " +  str(self.count + 1) + " saved"
            self.count = self.count + 1


    def plotData(self):
        """Plot the data obtained (Online)"""
        a1 = self.figure.add_subplot(311)
        a2 = self.figure.add_subplot(312)
        a3 = self.figure.add_subplot(313)
        a1.grid(True)
        a2.grid(True)
        a3.grid(True)
        while(1):
                a1.clear()
                a2.clear()
                a3.clear()
                #Aceleration
                if(self.show == 1):
                        if (index_a[0,0] > self.maxp):
                                a1.plot(array_a[0,(index_a[0,0]-self.maxp):index_a[0,0]])
                                a2.plot(array_a[1,(index_a[0,0]-self.maxp):index_a[0,0]])
                                a3.plot(array_a[2,(index_a[0,0]-self.maxp):index_a[0,0]])
                        else:
                                a1.plot(array_a[0,0:index_a[0,0]])
                                a2.plot(array_a[1,0:index_a[0,0]])
                                a3.plot(array_a[2,0:index_a[0,0]])
                #Rotation
                if(self.show == 0):
                        if (index_r[0,0] > self.maxp):
                                a1.plot(array_r[0,(index_r[0,0]-self.maxp):index_r[0,0]])
                                a2.plot(array_r[1,(index_r[0,0]-self.maxp):index_r[0,0]])
                                a3.plot(array_r[2,(index_r[0,0]-self.maxp):index_r[0,0]])
                        else:
                                a1.plot(array_r[0,0:index_r[0,0]])
                                a2.plot(array_r[1,0:index_r[0,0]])
                                a3.plot(array_r[2,0:index_r[0,0]])
                self.canvas.draw()
                """Reset" counter"""
                if(index_a[0,0]> maxd):
                        index_a[0,0] = 0
                if(index_r[0,0] > maxd):
                        index_r[0,0] = 0


    def plotsampleData(self):
        """Plot a sample data"""
        a1 = self.figure.add_subplot(311)
        a2 = self.figure.add_subplot(312)
        a3 = self.figure.add_subplot(313)
        a1.grid(True)
        a2.grid(True)
        a3.grid(True)
        a1.clear()
        a2.clear()
        a3.clear()
        a1.plot(array_a[0,(self.initsample_a):self.finalsample_a])
        a2.plot(array_a[1,(self.initsample_a):self.finalsample_a])
        a3.plot(array_a[2,(self.initsample_a):self.finalsample_a])
        self.canvas.draw()
        """Reset" counter"""
        if(index_a[0,0] > maxd):
                index_a[0,0] = 0
        if(index_r[0,0] > maxd):
                index_r[0,0] = 0



class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self, master):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI. We spawn a new thread for the worker.
        """
        self.master = master

        # Set up the GUI part
        self.gui = GuiPart(master, self.stopserver, self.startserver, maxp)

        # Set up the thread to do asynchronous I/O
        # More can be made if necessary

        # Start the periodic call in the GUI to check if the queue contains
        # anything
        #self.periodicCall()

##    def periodicCall(self):
##        """
##        Check every 100 ms if there is something new in the queue.
##        """
##        self.gui.processIncoming()
##        if not self.running:
##            # This is the brutal stop of the system. You may want to do
##            # some cleanup before actually shutting it down.
##            import sys
##            sys.exit(1)
##        self.master.after(100, self.periodicCall)

    def workerThread(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select()'.
        One important thing to remember is that the thread has to yield
        control.
        """
        #A server must perform the sequence socket(), bind(), listen(), accept()
        HOST = socket.gethostname()   # Get local machine name
        PORT = 8080                # Reserve a port for your service.

        print "Host IP:" , HOST


        #Running an example several times with too small delay between executions, could lead to this error:
        # socket.error: [Errno 98] Address already in use
        # There is a socket flag to set, in order to prevent this, socket.SO_REUSEADDR:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(0)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('', PORT))

        self.server.listen(5)

        # Sockets from which we expect to read
        inputs = [ self.server ]

        # Sockets to which we expect to write
        outputs = [ ]

        # Outgoing message queues (socket:Queue)
        message_queues = {}
        #----------

        #conn, addr = self.s.accept() # This call typically blocks until a client connects with the server.
        #print 'Connected by', addr

        i=0
        i2=0
        while self.running:
                # Wait for at least one of the sockets to be ready for processing
                readable, writable, exceptional = select.select(inputs, outputs, inputs)

                # Handle inputs
                for s in readable:

                        if s is self.server:
                            # A "readable" server socket is ready to accept a connection
                            connection, client_address = s.accept()
                            print >>sys.stderr, 'new connection from', client_address
                            connection.setblocking(0)
                            inputs.append(connection)

                            # Give the connection a queue for data we want to send
                            message_queues[connection] = Queue.Queue()

                        else:
                            data = s.recv(1024)
                            if data:
                                # A readable client socket has data
                                list_data = data.split("\n")
                                for line in list_data:
                                        condition, option, x,y,z = decode(line)
                                        if(condition == True and option == 0 and i < maxd):
                                            try:
                                                    array_a[0,i] = x
                                                    array_a[1,i] = y
                                                    array_a[2,i] = z
                                                    i = i+1
                                                    index_a[0,0]= i
                                            except ValueError,e:
                                                    i = i
                                        if(condition == True and option == 1 and i2 < maxd):
                                            try:
                                                    array_r[0,i2] = x
                                                    array_r[1,i2] = y
                                                    array_r[2,i2] = z
                                                    i2 = i2+1
                                                    index_r[0,0] = i2
                                            except ValueError,e:
                                                    i2 = i2
                                
                                message_queues[s].put(data)
                                # Add output channel for response
                                if s not in outputs:
                                    outputs.append(s)
                            else:
                                # Interpret empty result as closed connection
                                print >>sys.stderr, 'closing', client_address, 'after reading no data'
                                # Stop listening for input on the connection
                                if s in outputs:
                                    outputs.remove(s)
                                inputs.remove(s)
                                s.close()

                                # Remove message queue
                                del message_queues[s]

        print "Number of lines:", i + i2

    def stopserver(self):
        """Stop the server execution"""
        self.running = 0
        sleep(1.5)
        print "Server closed"
        self.master.destroy()


    def startserver(self):
        """Start a new thread for the server"""
        self.running = 1
        self.thread1 = threading.Thread(target=self.workerThread)
        self.thread1.start()



root = tk.Tk()
client = ThreadedClient(root)
root.mainloop()
