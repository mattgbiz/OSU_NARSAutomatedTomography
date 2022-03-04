#This file is for running tomography simulations with Manual XYZ Stage control
from tkinter import *
import XYZMotion_Station, SMC100Final, NewCameraControl#FewViewPart2 CameraControl
import time, pytz, subprocess, os.path, shutil, os
from datetime import datetime
import numpy as np
from PIL import Image, ImageTk, ImageEnhance
import threading
from threading import Thread
from tkinter import filedialog

currentPath = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
#print(currentPath)
IconPath = os.path.abspath(os.path.join(currentPath, 'OSU_NRL.ico'))
PNGPath = os.path.abspath(os.path.join(currentPath, 'OSU_NRL.png'))

class TomographyClass:
    def __init__(self,root):
        #Setup the root for the class
        self.root = root
        root.title('Automated Tomography with Manual XYZ Control')
        root.iconbitmap(IconPath)

        #Variables for closing things out at the end, they become true if they get used
        self.SMCUsed = False
        self.CameraUsed = False
        self.XYZUsed = False
        self.ExceptionThrown = False
        #Setup the overall structure for the code
        self.TomographyFrame = LabelFrame(root,text='Tomography')
        self.XYZFrame = LabelFrame(root,text='Manual Control of XYZ')
        #Tomography SubFrames
        self.InputTomographyFrame = LabelFrame(self.TomographyFrame, text='1. Input Experimental Parameters',pady=20)
        self.InitializeTomographyFrame = LabelFrame(self.TomographyFrame, text='2. Open Programs and Initialize Devices',pady=5)
        self.ImageFrame = LabelFrame(self.TomographyFrame, text='Previous Images')
        self.GeneralFrame = LabelFrame(self.TomographyFrame, text='3. Run the Tomography and Monitor It',padx=150,pady=30)
        self.OptionalFrame = LabelFrame(self.TomographyFrame, text='Options That May Pop-Up',bg='black',fg='white',padx=100,pady=50)
        
        #Put these on the screen
        self.TomographyFrame.grid(row=0,column=0)
        self.XYZFrame.grid(row=1,column=0)
        self.InputTomographyFrame.grid(row=0,column=0)
        self.InitializeTomographyFrame.grid(row=0,column=1)
        self.ImageFrame.grid(row=0,column=2)
        self.GeneralFrame.grid(row=1,column=0,columnspan=2)
        self.OptionalFrame.grid(row=1,column=2)
        
        #*********************************************************************************************
        #Add the Items to Input Frame
        self.FileNameLabel = Label(self.InputTomographyFrame, text='File Name')
        self.FileNameEntry = Entry(self.InputTomographyFrame,width=50)
        self.FileNameEntry.insert(0,'Experiment')
        self.FileLocationLabel = Label(self.InputTomographyFrame, text= 'File Location')
        self.FileLocationEntry = Entry(self.InputTomographyFrame, width = 50)
        self.FileLocationEntry.insert(0,currentPath)
        self.ExposureLabel = Label(self.InputTomographyFrame, text = 'Exposure Time (s)')
        self.ExposureEntry = Entry(self.InputTomographyFrame)
        self.ExposureEntry.insert(0,'30.0')
        self.NumberImagesLabel = Label(self.InputTomographyFrame, text='Num Images @ Each Deg')
        self.NumberImagesEntry = Entry(self.InputTomographyFrame)
        self.NumberImagesEntry.insert(0,'3')
        self.EMGainLabel = Label(self.InputTomographyFrame,text='EM Gain')
        self.EMGainEntry = Entry(self.InputTomographyFrame)
        self.EMGainEntry.insert(0,'3')
        self.SMCPortLabel = Label(self.InputTomographyFrame,text='SMC Port')
        self.SMCPortEntry = Entry(self.InputTomographyFrame)
        self.SMCPortEntry.insert(0,'COM4')
        #Have a browse spot for finding the .txt file
        self.BrowseLabel = Label(self.InputTomographyFrame, text='Browse for the text file that was the remaining values from last experiment')
        self.BrowseButton = Button(self.InputTomographyFrame, text ='Browse',command=self.FileBrowse)
        self.BrowseEntry = Entry(self.InputTomographyFrame,width=50)
        self.CameraPortLabel = Label(self.InputTomographyFrame,text='Camera Port')
        self.CameraPortEntry = Entry(self.InputTomographyFrame)
        self.CameraPortEntry.insert(0,'COM1')
        self.SubmitButton = Button(self.InputTomographyFrame,text='Enter',command=self.Submit)
        #Now Toss these on the Screen
        self.FileNameLabel.grid(row=0,column=0)
        self.FileNameEntry.grid(row=0,column=1,columnspan=3)
        self.FileLocationLabel.grid(row=1,column=0)
        self.FileLocationEntry.grid(row=1,column=1,columnspan=3)
        self.ExposureLabel.grid(row=2,column=0)
        self.ExposureEntry.grid(row=2,column=1)
        self.NumberImagesLabel.grid(row=3,column=0)
        self.NumberImagesEntry.grid(row=3,column=1)
        self.EMGainLabel.grid(row=2,column=2)
        self.EMGainEntry.grid(row=2,column=3)
        self.CameraPortLabel.grid(row=4,column=0)
        self.CameraPortEntry.grid(row=4,column=1)
        self.SMCPortLabel.grid(row=4,column=2)
        self.SMCPortEntry.grid(row=4,column=3)
        self.BrowseLabel.grid(row=5,columnspan=4)
        self.BrowseButton.grid(row=6,column=0,sticky='e')
        self.BrowseEntry.grid(row=6,column=1,columnspan=2,sticky='w')
        self.SubmitButton.grid(row=6,column=3,sticky='w')

        #************************************************************************************
        #Initialize Programs Frame
        self.MMOverallLabel = Label(self.InitializeTomographyFrame, text='If MicroManager is not open, close GUI, open MicroManager, then reopen GUI')
        self.MMReadyButton = Button(self.InitializeTomographyFrame,text='MM Ready!',command=self.MMReady)
        self.CameraOverallLabel = Label(self.InitializeTomographyFrame,text='Take any number of test images to check camera focus, click ready when done')
        self.SnapImageButton = Button(self.InitializeTomographyFrame,text='Snap Image',command= self.SnapImage)
        self.CameraReadyButton = Button(self.InitializeTomographyFrame,text='Camera Ready',command=self.CameraReady)
        self.SMCOverallLabel = Label(self.InitializeTomographyFrame,text='Test The connection of SMC controller and when it passes, hit "SMC Ready"')
        self.TestSMCButton = Button(self.InitializeTomographyFrame,text='Test SMC',command=self.TestSMC)
        self.SMCResultLabel = Label(self.InitializeTomographyFrame, text=' ')
        self.SMCReadyButton = Button(self.InitializeTomographyFrame,text='SMC Ready',command=self.SMCReady)
        self.FirstPick = True
        self.MMState = False
        self.CameraState = False
        self.SMCState = False
        self.CameraIncrement = 1
        self.SMCTestResult = 0
        #Toss these on the screen
        self.MMOverallLabel.grid(row=0,column=0,columnspan=3)
        self.MMReadyButton.grid(row=2,column=2,sticky='e')
        self.CameraOverallLabel.grid(row=3,column=0,columnspan=3)
        self.SnapImageButton.grid(row=4,column=0,sticky='w')
        self.CameraReadyButton.grid(row=4,column=2,sticky='e')
        self.SMCOverallLabel.grid(row=5,column=0,columnspan=3)
        self.TestSMCButton.grid(row=6,column=0,sticky='w')
        self.SMCResultLabel.grid(row=6,column=1)
        self.SMCReadyButton.grid(row=6,column=2,sticky='e')

        #************************************************************************************
        #Previous Image Frame
        #self.ImageTextLabel = Label(self.ImageFrame,text='Brightness Enchanced on JPEG')
        """self.BrightEntry = Entry(self.ImageFrame,width=10)
        self.BrightEntry.insert(0,'50.0')
        self.ImageLabel = Label(self.ImageFrame,text='hi')"""
        self.ContrastLabel = Label(self.ImageFrame, text='Contrast Enhanced on Tif')
        self.ContrastEntry = Entry(self.ImageFrame,width=10)
        self.ContrastEntry.insert(0,'50.0')
        self.ImageLabel2 = Label(self.ImageFrame,text='bye')
        #self.ShowImage('C:/Users/mattg_000/Documents/Research/PythonScripts/OSU_NRL.png')
        #self.ShowImage(PNGPath)
        self.ShowContrast(PNGPath)
        #toss these on the screen
        self.ContrastLabel.grid(row=0,column=1)
        self.ContrastEntry.grid(row=0,column=2)
        self.ImageLabel2.grid(row=1,column=1,columnspan=2)
        #************************************************************************************
        #General/Start Frame
        self.StartButton = Button(self.GeneralFrame,text='Start',bg='green',fg='white',padx=30,pady=20,command=self.StartExperiment)
        self.StartButton['state'] = DISABLED
        self.PauseButton = Button(self.GeneralFrame,text='Pause',bg='yellow',fg='black',padx=30,pady=20,command=self.Pause)
        self.PauseButton['state'] = DISABLED
        self.Paused = False
        self.SendRemainingButton = Button(self.GeneralFrame,text='Remaining To Text',wraplength=60,padx=15,pady=14,command=self.RemainingToText)
        self.CloseButton = Button(self.GeneralFrame,text='Stop and Close',bg='red',wraplength=30,padx=25,pady=5,command=self.Stop)
        self.GeneralMessageLabel = Label(self.GeneralFrame,text='General Experiment Messages/Error Will Appear Here')
        self.ErrorMessageLabel = Label(self.GeneralFrame,text='Error Messages Will Appear Here')
        self.SaveMessageLabel = Label(self.GeneralFrame, text='Last Save Location/File Will Appear Here')
        #Toss onto the screen
        self.StartButton.grid(row=0,rowspan=3,column=0,padx=5)
        self.PauseButton.grid(row=0,rowspan=3,column=1,padx=5)
        self.SendRemainingButton.grid(row=0,rowspan=3,column=2,padx=5)
        self.CloseButton.grid(row=0,rowspan=3,column=3,padx=5)
        self.GeneralMessageLabel.grid(row=0,column=4,padx=5)
        self.SaveMessageLabel.grid(row=1,column=4,padx=5)
        self.ErrorMessageLabel.grid(row=2,column=4,padx=5)

        #************************************************************************************
        #OptionalFrame Stuffs
        self.HiddenLabel = Label(self.OptionalFrame, text='John Cena',fg='black',bg='black')
        self.HiddenLabel.grid(row=0,column=0)

        #************************************************************************************
        #XYZ Frame
        self.ShowXYZButton = Button(self.XYZFrame,text='Show Control Of XYZ Stage',wraplength=60,padx=50,pady=10,command=self.ShowXYZ)
        self.ShowXYZButton.grid(row=0,column=0,columnspan=3)
        self.XYZConnected = False

    #****************************************************************************************
    def FileBrowse(self):
        print('Complete Dialogue')
        self.TextName = filedialog.askopenfilename(title = 'Select The .txt File', filetypes=(('txt','*.txt'),('All Files','*.*')))
        self.BrowseEntry.insert(0,self.TextName)
    #Functions for frame 1 and optional frame
    def Submit(self):
        #Get all of the data from the entries
        self.FileName = str(self.FileNameEntry.get())
        self.FileLocation = str(self.FileLocationEntry.get())
        self.ExposureTime = float(self.ExposureEntry.get())*1000 #making this into ms
        self.EMGain = int(self.EMGainEntry.get())
        self.SMCPort = str(self.SMCPortEntry.get())
        self.CameraPort = str(self.CameraPortEntry.get())
        self.NumImagesPerDeg = int(self.NumberImagesEntry.get())
        #Get the browsed file
        self.TextLocation = self.BrowseEntry.get()
        InputText = open(self.TextLocation,'r',newline='\r\n')
        DataText = InputText.read().splitlines()
        InputText.close()
        print(DataText)
        
        self.DegreeList = []
        for row in range(0,len(DataText)):
            #Separate the degrees out
            self.DegreeList.append(float(DataText[row]))
        #self.Start = float(self.StartDegreeEntry.get())
        #self.Rotation = float(self.RotationEntry.get())
        #self.Max = float(self.MaxDegreeEntry.get())
        #self.Few = int(self.FewVar.get())
        print(self.DegreeList)

        #If any of the inputs are negative we have a high max
        if min(self.DegreeList)<-5.0:
            self.HighMax = True
            self.DegMes = [x+180.0 for x in self.DegreeList]
        else:
            self.HighMax = False
            self.DegMes = self.DegreeList 

        #Check to make sure the maximum degree, start degree and rotation
        """self.Proceed1 = 0
        print(self.Proceed1)
        self.CheckDivisibility(self.Start,self.Max,self.Rotation)
        print(self.Proceed1)
        self.waitVar1 = IntVar()
        while self.Proceed1 == 0:
            print('in While loop')
            self.InputTomographyFrame.wait_variable(self.waitVar1)
        print('Past While Loop')"""

        #Ensure that the users is not overwriting an old experiment if they don't mean to
        self.PathCheck = self.FileLocation + '/' + self.FileName + str(self.DegreeList[0]) + '.tif'
        if os.path.exists(self.PathCheck) == True:
            self.Proceed2 = 0
            self.waitVar2 = IntVar()
            self.ReNameOverall()
            while self.Proceed2 == 0:
                self.InputTomographyFrame.wait_variable(self.waitVar2)
        #Also check if the file location exists and if it doesnt create it
        if os.path.exists(self.FileLocation) == False:
            os.mkdir(self.FileLocation)

        #Make the List of degrees that the stage will go to
        #self.DegreeList = np.arange(self.Start, (self.Max+self.Rotation), self.Rotation).tolist() 
        
        #Next Check the Few View Check Button and see if the Few View algorithm needs to be run
        """if self.Few == 1:
            self.FewView = True
            import FewViewPart2
            FewView = FewViewPart2.FewView(self.DegreeList,self.Start,self.Max)
            self.DegreeList = FewView.MakeFewView()

            #Do stuff with importing the few view calculator"""
        #print(self.NormalList)
        #Next Check the Max degree and if it is over 180 degree as the stage has to go around to negative
        #Only do this if the few view hasn't been run since we make things negative in few view
        """if self.Max > 180.0 and self.Few == 0:
            self.HighMax = True
            self.HighMaxList = np.arange(self.Start, (self.Max+self.Rotation),self.Rotation).tolist()
            for i in range(0,len(self.DegreeList)):
                if self.DegreeList[i] <= 180.0:
                    self.HighMaxList[i] = self.DegreeList[i]
                elif self.DegreeList[i] > 180.0:
                    self.HighMaxList[i] = self.DegreeList[i] - 360.0
            self.DegreeList = self.HighMaxList
        print('Here is the final degree list to be used: {}'.format(self.DegreeList))"""
        
        #When all done Return the optional frame to black
        self.OptionalFrame.grid_forget()
        self.OptionalFrame = LabelFrame(self.TomographyFrame,text='Remaining Degrees Listed Here',bg='black',fg='white',padx=10,pady=10)
        self.OptionalFrame.grid(row=1,column=2)
        self.HiddenLabel = Label(self.OptionalFrame,text='Houdini',bg='black',fg='black')
        self.HiddenLabel.grid(row=0,column=0)
        self.DegreeMessage = ' '.join(map(str, self.DegMes))
        self.ListMessage(self.DegreeMessage)

    def ReNameOverall(self):
        self.OptionalFrame.grid_forget()
        self.OptionalFrame = LabelFrame(self.TomographyFrame, text = 'Re-Name Option')
        self.OptionalFrame.grid(row=1,column=2)
        #Make the labels for this
        self.InstructionLabel3 = Label(self.OptionalFrame,text='The file already exists in the specified location')
        self.InstructionLabel4 = Label(self.OptionalFrame,text='Change entries as desired and select appropriate button')
        self.ChangeNameLabel = Label(self.OptionalFrame,text='File Name To Change:')
        self.ChangeNameEntry = Entry(self.OptionalFrame,width=40)
        self.ChangeNameEntry.insert(0,self.FileName)
        self.ChangeLocationLabel = Label(self.OptionalFrame,text='Path To Change:')
        self.ChangeLocationEntry = Entry(self.OptionalFrame,width=40)
        self.ChangeLocationEntry.insert(0,self.FileLocation)
        self.OverwriteButton = Button(self.OptionalFrame,text='Overwrite',command=self.Overwrite)
        self.ChangeNameButton = Button(self.OptionalFrame,text='Change Name',command=self.ChangeName)
        self.ChangeLocationButton = Button(self.OptionalFrame,text='Change Path',command=self.ChangeLocation)
        self.ChangeBothButton = Button(self.OptionalFrame,text='Change Both',command=self.ChangeBoth)
        #Toss em on the screen
        self.InstructionLabel3.grid(row=0,column=0,columnspan=4)
        self.InstructionLabel4.grid(row=1,column=0,columnspan=4)
        self.ChangeNameLabel.grid(row=2,column=0)
        self.ChangeNameEntry.grid(row=2,column=1,columnspan=3)
        self.ChangeLocationLabel.grid(row=3,column=0)
        self.ChangeLocationEntry.grid(row=3,column=1,columnspan=3)
        self.OverwriteButton.grid(row=4,column=0)
        self.ChangeNameButton.grid(row=4,column=1)
        self.ChangeLocationButton.grid(row=4,column=2)
        self.ChangeBothButton.grid(row=4,column=3)

    def Overwrite(self):
        #Does nothing but continue the function as normal
        print('User Chose to overwrite')
        self.waitVar2.set(1)
        self.Proceed2 = 1
    def ChangeName(self):
        self.FileName = self.ChangeNameEntry.get()
        self.FileNameEntry.delete(0,END)
        self.FileNameEntry.insert(0,self.FileName)

        self.waitVar2.set(1)
        self.Proceed2 = 1    
    def ChangeLocation(self):
        self.FileLocation = self.ChangeLocationEntry.get()
        self.FileLocationEntry.delete(0,END)
        self.FileLocationEntry.insert(0,self.FileLocation)

        self.waitVar2.set(1)
        self.Proceed2 = 1
    def ChangeBoth(self):
        self.FileName = self.ChangeNameEntry.get()
        self.FileLocation = self.ChangeLocationEntry.get()
        self.FileNameEntry.delete(0,END)
        self.FileLocationEntry.delete(0,END)
        self.FileNameEntry.insert(0,self.FileName)
        self.FileLocationEntry.insert(0,self.FileLocation)

        self.waitVar2.set(1)
        self.Proceed2 = 1

    #****************************************************************************
    #Functions that go with Opeing Programs and initializing devices
    def OpenMM(self):
        #Run the Program to open MM
        subprocess.Popen(self.MMLocationEntry.get())
        self.OpenMMButton.grid_forget()
        self.OpenMMButton = Button(self.InitializeTomographyFrame,text='Opening MM Wait for it to fully run',command=self.OpenMM)
        self.OpenMMButton.grid(row=2,column=0,columnspan=2,sticky='w')
    
    def MMReady(self):
        #This button really is just here to be sure that MM is open properly
        self.MMState=True
        if self.MMState == True and self.CameraState == True and self.SMCState == True:
            self.StartButton['state'] = NORMAL
        self.MMReadyButton.grid_forget()
        self.MMReadyButton = Button(self.InitializeTomographyFrame,text='MM Ready',bg='green',fg='white',command=self.MMReady)
        self.MMReadyButton.grid(row=2,column=2,sticky='e')
        #This is a test
        #self.DegreeMessage = ' '.join(map(str, self.DegreeList))
        #self.ListMessage(self.DegreeMessage)
        #self.RemainingList=[3.0,45.0,60.0]

    def SnapImage(self):
        if self.FirstPick == True: 
            #Initialize the Camera
            self.CameraPort = str(self.CameraPortEntry.get())
            self.Camera = NewCameraControl.CameraControl(self.CameraPort)
            self.FirstPick = False
            self.CameraUsed = True
        #Snap an image
        #self.BrightnessVal = float(self.BrightEntry.get())
        self.ContrastVal = float(self.ContrastEntry.get())
        self.SnapExposure = float(self.ExposureEntry.get())*1000
        self.SnapEMGain = int(self.EMGainEntry.get())
        if os.path.exists(self.FileLocation) == False:
            os.mkdir(self.FileLocation)
            self.ErrorMessage('Created a new folder as the input one did not exist')
        self.Image = self.Camera.TakeImage(self.SnapExposure,self.FileLocationEntry.get(),'TestImage',self.CameraIncrement,self.ContrastVal,self.SnapEMGain)
        #self.Image = 'optical.tif'
        #convert the image to jpg
        #self.ConvertImage()
        #Show the Image on the screen
        #self.ShowImage(self.FileLocationEntry.get()+'/ReSizedJPGs/'+'TestImage'+str(self.CameraIncrement)+'_brightened'+'.jpeg')
        self.ShowContrast(self.FileLocationEntry.get()+'/ReSizedJPGs/'+'TestImage'+str(self.CameraIncrement)+'_contrast'+'.jpeg')
        self.CameraIncrement +=1

    
    def CameraReady(self):
        self.CameraState = True
        if self.MMState == True and self.CameraState == True and self.SMCState == True:
            self.StartButton['state'] = NORMAL
        self.CameraReadyButton.grid_forget()
        self.CameraReadyButton = Button(self.InitializeTomographyFrame,text='Camera Readied',bg='green',fg='white',command=self.CameraReady)
        self.CameraReadyButton.grid(row=4,column=2,sticky='e')
    
    def TestSMC(self):
        print('Perfoming SMC General Test')
        self.SMCTestResult = SMC100Final.test_general(self.SMCPort)
        self.SMCUsed = True
        if self.SMCTestResult == 0:
            self.TestSMCButton.grid_forget()
            self.TestSMCButton = Button(self.InitializeTomographyFrame,text='SMC Failed, Check Connection',bg='red',command=self.TestSMC)
            self.TestSMCButton.grid(row=6,column=0,columnspan=2,sticky='w')
        elif self.SMCTestResult == 1:
            self.TestSMCButton.grid_forget()
            self.TestSMCButton = Button(self.InitializeTomographyFrame,text='SMC Passed, Press Ready',bg='green',fg='white',command=self.TestSMC)
            self.TestSMCButton.grid(row=6,column=0,columnspan=2,sticky='w')

    
    def SMCReady(self):
        self.SMCState = True
        if self.MMState == True and self.CameraState == True and self.SMCState == True:
            self.StartButton['state'] = NORMAL
        self.SMCReadyButton.grid_forget()
        self.SMCReadyButton = Button(self.InitializeTomographyFrame,text='SMC Readied',bg='green',fg='white',command=self.SMCReady)
        self.SMCReadyButton.grid(row=6,column=2,sticky='e')
        #Also I need to addd the condition of making the start button active

    #****************************************************************************88
    #Image Functions
    def ShowContrast(self,ImagePath2):
        self.ImageToShow2 = Image.open(ImagePath2)
        self.ImageToShow2 = self.ImageToShow2.resize((250,250),Image.ANTIALIAS)
        self.ReferencedImage2 = ImageTk.PhotoImage(self.ImageToShow2)
        self.ImageLabel2.destroy()
        self.ImageLabel2 = Label(self.ImageFrame, image=self.ReferencedImage2)
        self.ImageLabel2.image=self.ReferencedImage2
        self.ImageLabel2.grid(row=1,column=0,columnspan=2)

    def CloseContrast(self,ImagePath3):
        os.remove(ImagePath3)
        #os.remove(self.FileLocationEntry.get()+'/ReSizedJPGs/'+self.FileNameEntry.get()+str(self.CameraIncrement)+'_contrast.jpeg')

    #*******************************************************************************************
    #GeneralFrame Content
    def StartExperiment(self):
        print('Experiment Starting')
        if self.SMCUsed == False:
            self.SMCUsed = True
        if self.CameraUsed == False:
            self.CameraUsed = True
        #Make the experiment log
        self.GeneralMessage('Tomography experiment has started')
        tz = pytz.timezone('US/Eastern')
        Columbus_Current_Datetime = str(datetime.now(tz))
        Columbus_Current_Datetime = Columbus_Current_Datetime[0:9] + '_' + Columbus_Current_Datetime[11:12] + '.' + Columbus_Current_Datetime[14:15] + '.' + Columbus_Current_Datetime[17:18] 
        self.StartTime = time.time()
        self.LogName = self.FileLocation + '/' + self.FileName + str(Columbus_Current_Datetime) + '.txt'
        self.Log = open(self.LogName,'w+')
        self.Log.write('Tomography has started at: {}\r\n'.format(datetime.now(tz)))
        self.Log.write('The file name is {} and is saving to {} \r\n'.format(self.FileName,self.FileLocation))
        self.Log.write('This experiment was a leftover tomography after an error.')
        self.Log.write('A list of degrees was input from following file: {}'.format(self.TextLocation))
        #self.Log.write('Input Parameters- Exposure Time: {} EM Gain: {} Degree Increment: {} Start Degree: {} Max Degree: {} \r\n'.format(self.ExposureTime,self.EMGain,self.Rotation,self.Start,self.Max))
        #Create an instance of the SMC
        self.SMC = SMC100Final.SMC100(1,self.SMCPort)
        self.SMC.home()
        #Check to make sure camera is connected
        if self.FirstPick == True: 
            #Initialize the Camera
            print('Would have taken first picture')
            self.Camera = NewCameraControl.CameraControl(self.CameraPort)
        #Enable the PAuse button
        self.PauseButton['state'] = NORMAL

        #Now do the threads stuff
        print('About to start threads')
        self.TomographyComplete = False
        self.FirstPicture = True    #This is different from FirstPick this is with respect to the image shown in GUI during threading
        self.ControlThread = threading.Thread(target=self.ControlPeripherals)
        self.UpdateThread = threading.Thread(target=self.UpdateGUI) 
        self.UpdateKill = False
        self.ControlThread.start()
        self.UpdateThread.start()

    def ControlPeripherals(self):
        #This is the thread that will be in charge of running the rotation stage and camera during the experiment
        lastDegree = self.DegreeList[0]
        self.RemainingList = self.DegreeList
        for deg in self.DegreeList:
            #check the pause condition and if we are still paused, sleep
            """if self.Paused == True:
                self.PauseCond = 0
                self.waitPause = IntVar()
                while self.PauseCond == 0:
                    self.GeneralFrame.wait_variable(self.waitPause)
                    #if self.Paused == False:
                    #    self.PauseCond = 0:
                #Here we check the parameters to make sure they are the same
                self.ExposureTime = float(self.ExposureEntry.get())*1000
                #self.BrightRun = float(self.BrightEntry.get())
                self.ContrastRun = float(self.ContrastEntry.get())
                self.EMGain = int(self.EMGainEntry.get())"""
            #print('Inside Control Periphs function')
            #First the SMC stage needs to rotate to the position for the picutre
            try:
                self.SMC.improved_move_abs(deg,15) #the speed of the stage is usually set to 15 as my benchmark
            except:
                self.NewErrorMessage = 'Stage did not successfully rotate to {} deg'.format(deg)
                self.ExceptionThrown = True    
            #self.NewErrorMessage = 'The SMC Stage has rotated to {}'.format(lastDegree)
            #Now that at first deg we want to take a picture at the degree
            #self.BrightRun = float(self.BrightEntry.get())
            self.ContrastRun = float(self.ContrastEntry.get())
            #Make the value for the suffix be whatever the degree is plus 180 if the max is above 180
            if self.HighMax == True:
                self.suffix = deg + 180.0
            else:
                self.suffix = deg
            self.realSuffix = 1     #the deg suffix will be middle of name, real suffix is first,second,third
            while self.realSuffix <= self.NumImagesPerDeg:
                try:
                    #this has been changed from before, now we have the degree within the "filename" and the number of the image as the suffix
                    self.Image=self.Camera.TakeImage(self.ExposureTime,self.FileLocation,(self.FileName+str(self.suffix)+'_'),self.realSuffix,self.ContrastRun,self.EMGain)
                except:
                    self.NewErrorMessage = 'Camera did not take picture properly, error in camera'
                    self.ExceptionThrown = True
                else:    
                    self.ContrastPath = self.FileLocation+'/ReSizedJPGs/'+self.FileName+str(self.suffix)+'_'+str(self.realSuffix)+'_contrast'+'.jpeg'
                    #print('Contrast Path in Control Periph: {}'.format(self.ContrastPath))
                    self.ContrastTiff = self.FileLocation+'/ReSizedJPGs/'+self.FileName+str(self.suffix)+'_'+str(self.realSuffix)+'_contrast.tif'
                    self.JPGPath = self.FileLocation+'/ReSizedJPGs/'+self.FileName+str(self.suffix)+'_'+str(self.realSuffix)+'.jpeg'
                    self.NewSaveMessage = 'The Camera has just saved image: {} to the specificed location'.format(self.Image)
                self.realSuffix+=1
            lastDegree = deg
            #I add the self.Rotation to show where the stage is moving to next
            #self.NewErrorMessage = 'The SMC Stage has rotated to {}'.format((lastDegree+self.Rotation))
            #The sleep is added for threading purposes
            if self.ExceptionThrown == False:
                self.NewErrorMessage = 'No errors at this time'
            else:
                self.NewErrorMessage = 'whot'
                #send the remaining degrees to text and then show the general frame to be red to grab attention
                self.RemainingToText()
                self.GeneralFrame.grid_forget()
                self.GeneralFrame = LabelFrame(self.TomographyFrame, text='Error Error Error',fg='white',bg='red',padx=10,pady=10)
                self.GeneralFrame.grid(row=1,column=0,columnspan=2)
            time.sleep(0.01)
            #Do this so the last move done is up
            #lastDegree = deg
            self.FirstPicture = False
            #take out this first item in remaining list
            self.RemainingList = self.RemainingList[1:]
            self.DegreeMessage = ' '.join(map(str, self.RemainingList))
            #Extract how much time is expected to be left
            self.ImagesLeft = len(self.RemainingList)
            self.ExpectedTime = round(self.TimeRemaining(self.ExposureTime,self.ImagesLeft),2)
            #self.ListMessage(self.DegreeMessage)
            #Get the time and number of images remaining
            #self.TimeNow = time.time()
            #self.TimeElapsed = (self.TimeNow - self.StartTime)/60.0
            
            self.NewGenMessage = 'Expected time remaining {}min for the {} images left'.format(self.ExpectedTime,self.ImagesLeft)

        #after we leave the for loops tell user and kill the threads
        self.ErrorMessage('Tomography has completed')
        self.Log.write('Tomography completed, stage is homing\r\n')
        self.SMC.home()
        self.Log.close()
        
        self.UpdateKill = True    #kill the update part of the update gui
        #Delete the Resized Jpg folder as this wastes space on the computer
        #Need to put the icon on the screen at the end because need to not have any of those files open
        self.TomographyComplete = True
        self.ShowContrast(PNGPath)
        shutil.rmtree(self.FileLocation+'/ReSizedJPGs')
        #wait a few seconds to let it catch up
        
    
    def UpdateGUI(self):
        if self.UpdateKill != True:
            #print('Inside Update Gui function')
            """if self.Paused == True:
                self.PauseCond = 1
                while self.PauseCond == 1:
                    Thread.sleep(10)
                    if self.Paused == False:
                        self.PauseCond = 0:"""
            if self.FirstPicture == True:
                root.after((int(self.ExposureTime)+1000), self.UpdateGUI)
            else:
                root.after(500,self.UpdateGUI)
            #Put new image on screen
            #Commenting out for testing stage
            #self.ShowImage(self.ImagePath)
            if self.TomographyComplete == False:
                #print('Contrast Path in Update GUI: {}'.format(self.ContrastPath))
                self.ShowContrast(self.ContrastPath)
            else:
                self.ShowContrast(PNGPath)
            #And Show the last messages"""
            self.ErrorMessage(self.NewErrorMessage)
            self.Log.write((self.NewErrorMessage + '\r\n'))
            self.SaveMessage(self.NewSaveMessage)
            self.Log.write((self.NewSaveMessage + '\r\n'))
            self.GeneralMessage(self.NewGenMessage)
            #the remaining list is in terms of positive and negative values, use only positives like before
            if self.HighMax == True:
                self.DegMes = [x+180.0 for x in self.RemainingList]
            else:
                self.DegMes = self.DegreeList
            self.DegreeMessage = ' '.join(map(str, self.DegMes))   
            self.ListMessage(self.DegreeMessage)
            #self.ListMessage(self.RemainingList)
            #Sleep added for threading
            time.sleep(0.01)

    def Pause(self):
        #When you press the pause button, the if statements in the threads should make it such that nothing happens
        #self.CloseContrast(self.ContrastPath)
        #self.CloseContrast(self.ContrastTiff)
        #self.CloseContrast(self.JPGPath)
        #time.sleep(1)
        #shutil.rmtree(self.FileLocation+'/ReSizedJPGs')
        
        self.Paused = True
        #now the other conditions get changed in the control thread function as well
        self.PauseButton.destroy()
        self.PauseButton = Button(self.GeneralFrame,text='Unpause',bg='yellow',fg='black',padx=25,pady=20,command=self.Unpause)
        self.PauseButton.grid(row=0,rowspan=3,column=1,padx=5)

    def Unpause(self):
        self.Paused = False
        self.waitPause.set(1)
        self.PausedCond = 1
        #Hopefully this gets read by the threads and it actually changes things
        self.PauseButton.destroy()
        self.PauseButton = Button(self.GeneralFrame,text='Pause',bg='gray',fg='black',padx=30,pady=20,command=self.Pause)
        self.PauseButton.grid(row=0,rowspan=3,column=1,padx=5)


    def RemainingToText(self):
        tz = pytz.timezone('US/Eastern')
        Columbus_Current_Datetime = str(datetime.now(tz))
        Columbus_Current_Datetime = Columbus_Current_Datetime[0:9] + '_' + Columbus_Current_Datetime[11:12] + '.' + Columbus_Current_Datetime[14:15] + '.' + Columbus_Current_Datetime[17:18] 
        self.RemainingLogName = self.FileLocation + '/' + self.FileName + str(Columbus_Current_Datetime) + 'RemainingList.txt'
        print('Txt File is at {}'.format(self.RemainingLogName))
        self.RLog = open(self.RemainingLogName,'w+')
        for i in range(0,len(self.RemainingList)):
            self.RLog.write(str(self.RemainingList[i])+'\n')
        self.RLog.close()


    def Stop(self):
        print('Closing out')
        if self.XYZUsed == True:
            try:
                self.XYZ = XYZMotion_Station.VXM(self.XYZPortEntry.get(),9600,0.1)
            except:
                try:
                    #self.XYZ.home() don't home the stage as we want it in experimental position
                    self.XYZ.__del__()
                except:
                    self.GeneralMessage('Error in closing, XYZ stage would not home')
                    self.XYZClose = False
                else:
                    self.XYZClose = True
            else:
                #self.XYZ.home() don't home the stage as we want it in eperimental position
                self.XYZ.__del__()
                self.XYZClose = True
        else:
            #if it didn't get used then it is closed
            self.XYZClose = True
        if self.SMCUsed == True:
            try:
                self.SMC = SMC100Final.SMC100(1,self.SMCPortEntry.get())
            except:
                try:
                    self.SMC.home()
                    self.SMC.close()
                
                except:
                    self.ErrorMessage('Error in closing SMC, rotation stage would not home')
                    self.SMCClose = False
                else:
                    self.SMCClose = True
            else:
                self.SMC.home()
                self.SMC.close()
                self.SMCClose = True
        else:
            self.SMCClose = True
        if self.CameraUsed == True:
            try:
                self.Camera.CloseCamera()
            except:
                self.SaveMessage('Camera would not disconnect, check its status')
                self.CameraClose = False
            else:
                self.CameraClose = True
        else:
            self.CameraClose = True
        if self.SMCClose == True and self.CameraClose == True and self.XYZClose == True: 
            #only close if both get homed
            root.destroy()

    def GeneralMessage(self,Message):
        self.GeneralMessageLabel.destroy()
        self.GeneralMessageLabel = Label(self.GeneralFrame,text=str(Message))
        self.GeneralMessageLabel.grid(row=0,column=4)
    
    def ErrorMessage(self,Message):
        self.ErrorMessageLabel.destroy()
        self.ErrorMessageLabel = Label(self.GeneralFrame, text=str(Message))
        self.ErrorMessageLabel.grid(row=2,column=4)

    def SaveMessage(self,Message):
        self.SaveMessageLabel.destroy()
        self.SaveMessageLabel = Label(self.GeneralFrame,text=str(Message))
        self.SaveMessageLabel.grid(row=1,column=4)
    def ListMessage(self,Message):
        self.HiddenLabel.destroy()
        self.HiddenLabel = Label(self.OptionalFrame,text=str(Message),bg='white',fg='black',wraplength=480)
        self.HiddenLabel.grid(row=0,column=0)

    def TimeRemaining(self,ExposureTime,ImagesRemaining):
        #calculate how much time in total the expected movetime will be
        if ImagesRemaining > 20:    #chose 20 as arbitrary point, see if this needs to be switched
            MoveTime_s = 1.8866*ImagesRemaining+41.559
            ImageTime_s = (ExposureTime/1000)*ImagesRemaining  #this is in ms rn, need to fix
            self.TimeLeft = (MoveTime_s+ImageTime_s)/60.0
        else:
            #when we are nearing the end, the movement time will be drastically reduced as they will be small movements
            #I will say each movement will take just over a half second
            MoveTime_s = ImagesRemaining*0.53
            ImageTime_s = (ExposureTime/1000)*ImagesRemaining
            self.TimeLeft = (MoveTime_s+ImageTime_s)/60.0
        
        return self.TimeLeft


    def ShowXYZ(self):
        self.ShowXYZButton.grid_forget()
        #Ok so the Manual Control of the XYZ Stage has a lot of subframes
        self.InitiateXYZ = LabelFrame(self.XYZFrame,text='Initialize XYZ')
        self.StatusXYZ = LabelFrame(self.XYZFrame, text='Status of XYZ')
        self.ControlXYZ = LabelFrame(self.XYZFrame, text='Control XYZ Stage')
        #Toss these baddies
        self.InitiateXYZ.grid(row=0,column=0)
        self.StatusXYZ.grid(row=0,column=1)
        self.ControlXYZ.grid(row=1,column=0,columnspan=2)
        #Initiaze Frame Contents
        self.XYZPortLabel = Label(self.InitiateXYZ, text='Enter Port for XYZ:')
        self.XYZPortEntry = Entry(self.InitiateXYZ,width=10)
        self.XYZPortEntry.insert(0,'COM5')
        #self.LimitZVar = IntVar()
        #self.LimitZVar.set(0)
        #self.LimitZCheck = Checkbutton(self.InitiateXYZ,text='Select if Z Dirn is Restricted',variable=self.LimitZVar)
        self.XYZConnectButton = Button(self.InitiateXYZ,text='Connect',padx=58,pady=5,command=self.ConnectXYZ)
        self.XYZHomeButton = Button(self.InitiateXYZ,text='Home',padx=62,pady=5,command=self.HomeXYZ)
        self.XYZSetExperimental = Button(self.InitiateXYZ,text='Set Positions as Experimentals',pady=5,command=self.SetExperimentals)
        self.XYZGoToExperimental = Button(self.InitiateXYZ,text='Go To Experimental Positions',padx=2,pady=5,command=self.ExperimentalPositions)
        self.XYZHideButton = Button(self.InitiateXYZ,text='Hide XYZ Control',padx=34,pady=5,command=self.HideXYZ)
        self.XYZDisconnectButton = Button(self.InitiateXYZ,text='Disconnect',padx=49,pady=5,command=self.DisconnectXYZ)
        #Put on screen
        self.XYZPortLabel.grid(row=0,column=0)
        self.XYZPortEntry.grid(row=0,column=1)
        #self.LimitZCheck.grid(row=0,column=2)
        self.XYZConnectButton.grid(row=1,column=0,columnspan=2)
        self.XYZHomeButton.grid(row=1,column=2)
        self.XYZSetExperimental.grid(row=2,column=0,columnspan=2)
        self.XYZGoToExperimental.grid(row=2,column=2)
        self.XYZHideButton.grid(row=3,column=0,columnspan=2)
        self.XYZDisconnectButton.grid(row=3,column=2)

        #Status Frame Contents
        self.StagePositionsLabel = Label(self.StatusXYZ,text='Current Stage Positions')
        self.StageSpeedsLabel = Label(self.StatusXYZ,text='Current Motor Speeds')
        self.XmmLabel = Label(self.StatusXYZ,text='X Position (mm)')
        self.XmmEntry = Entry(self.StatusXYZ,width=15)
        self.XinLabel = Label(self.StatusXYZ,text='X Position (in)')
        self.XinEntry = Entry(self.StatusXYZ,width=15)
        self.XSpeedLabel = Label(self.StatusXYZ,text='X Speed (steps/sec)')
        self.XSpeedEntry = Entry(self.StatusXYZ,width=15)
        self.YmmLabel = Label(self.StatusXYZ,text='Y Position (mm)')
        self.YmmEntry = Entry(self.StatusXYZ,width=15)
        self.YinLabel = Label(self.StatusXYZ,text='Y Position (in)')
        self.YinEntry = Entry(self.StatusXYZ,width=15)
        self.YSpeedLabel = Label(self.StatusXYZ,text='Y Speed (steps/sec)')
        self.YSpeedEntry = Entry(self.StatusXYZ,width=15)
        self.ZmmLabel = Label(self.StatusXYZ,text='Z Position (mm)')
        self.ZmmEntry = Entry(self.StatusXYZ,width=15)
        self.ZinLabel = Label(self.StatusXYZ,text='Z Position (in)')
        self.ZinEntry = Entry(self.StatusXYZ,width=15)
        self.ZSpeedLabel = Label(self.StatusXYZ,text='Z Speed (steps/sec)')
        self.ZSpeedEntry = Entry(self.StatusXYZ,width=15)
        self.CurrentSetLabel = Label(self.StatusXYZ,text='Below Are The Current Set Points For The Experimental Positions')
        self.XSetLabel = Label(self.StatusXYZ, text='X Exp Position (mm):')
        self.XSetEntry = Entry(self.StatusXYZ,width=15)
        self.XSetEntry.insert(0,'20.0')
        self.YSetLabel = Label(self.StatusXYZ,text='Y Exp Position (mm):')
        self.YSetEntry = Entry(self.StatusXYZ,width=15)
        self.YSetEntry.insert(0,'10.0')
        self.ZSetLabel = Label(self.StatusXYZ,text='Z Exp Position (mm):')
        self.ZSetEntry = Entry(self.StatusXYZ,width=15)
        self.ZSetEntry.insert(0,'40.0')
        #Get them on the screen
        self.StagePositionsLabel.grid(row=0,column=0,columnspan=4)
        self.StageSpeedsLabel.grid(row=0,column=4,columnspan=2)
        self.XmmLabel.grid(row=1,column=0)
        self.XmmEntry.grid(row=1,column=1)
        self.XinLabel.grid(row=1,column=2)
        self.XinEntry.grid(row=1,column=3)
        self.XSpeedLabel.grid(row=1,column=4)
        self.XSpeedEntry.grid(row=1,column=5)
        self.YmmLabel.grid(row=2,column=0)
        self.YmmEntry.grid(row=2,column=1)
        self.YinLabel.grid(row=2,column=2)
        self.YinEntry.grid(row=2,column=3)
        self.YSpeedLabel.grid(row=2,column=4)
        self.YSpeedEntry.grid(row=2,column=5)
        self.ZmmLabel.grid(row=3,column=0)
        self.ZmmEntry.grid(row=3,column=1)
        self.ZinLabel.grid(row=3,column=2)
        self.ZinEntry.grid(row=3,column=3)
        self.ZSpeedLabel.grid(row=3,column=4)
        self.ZSpeedEntry.grid(row=3,column=5)
        self.CurrentSetLabel.grid(row=4,column=0,columnspan=6)
        self.XSetLabel.grid(row=5,column=0)
        self.XSetEntry.grid(row=5,column=1)
        self.YSetLabel.grid(row=5,column=2)
        self.YSetEntry.grid(row=5,column=3)
        self.ZSetLabel.grid(row=5,column=4)
        self.ZSetEntry.grid(row=5,column=5)     

        #*************************************
        #Control Frame Contents
        self.XMoveLabel = Label(self.ControlXYZ,text='X Movements: Range +/-63.206mm (2.4884in)')
        self.XZeroButton = Button(self.ControlXYZ,text='X Zero',command=lambda: self.ZeroStage('X'))
        self.YMoveLabel = Label(self.ControlXYZ,text='Y Movements: Range +/-63.632mm (2.5052in)')
        self.YZeroButton = Button(self.ControlXYZ,text='Y Zero',command=lambda: self.ZeroStage('Y'))
        self.ZMoveLabel = Label(self.ControlXYZ,text='Z Movements: Range +/-63.686mm (2.5073in)')
        self.ZZeroButton = Button(self.ControlXYZ,text='Z Zero',command=lambda: self.ZeroStage('Z'))
        self.MotorRangeLabel = Label(self.ControlXYZ,text='Set Motor Speeds: Range 1-6000 steps/s')
        self.XRelLabel = Label(self.ControlXYZ,text='X Relative Move:')
        self.XRelEntry = Entry(self.ControlXYZ,width=15)
        self.XRelEntry.insert(0,'5.0')
        self.XRelDropVar = StringVar()
        self.XRelDropVar.set('mm')
        self.XRelDropDown = OptionMenu(self.ControlXYZ, self.XRelDropVar, 'mm', 'in')
        self.XRelButton = Button(self.ControlXYZ,text='Move',command=lambda: self.XYZMoveRelative('X'))
        self.YRelLabel = Label(self.ControlXYZ,text='Y Relative Move:')
        self.YRelEntry = Entry(self.ControlXYZ)
        self.YRelEntry.insert(0,'5.0')
        self.YRelDropVar = StringVar()
        self.YRelDropVar.set('mm')
        self.YRelDropDown = OptionMenu(self.ControlXYZ,self.YRelDropVar,'mm','in')
        self.YRelButton = Button(self.ControlXYZ,text='Move',command=lambda: self.XYZMoveRelative('Y'))
        self.ZRelLabel = Label(self.ControlXYZ,text='Z Relative Move:')
        self.ZRelEntry = Entry(self.ControlXYZ)
        self.ZRelEntry.insert(0,'5.0')
        self.ZRelDropVar = StringVar()
        self.ZRelDropVar.set('mm')
        self.ZRelDropDown = OptionMenu(self.ControlXYZ,self.ZRelDropVar,'mm','in')
        self.ZRelButton = Button(self.ControlXYZ,text='Move',command=lambda: self.XYZMoveRelative('Z'))
        self.SpeedLabel = Label(self.ControlXYZ,text='Select Stage and Enter Speed:')
        self.StageVar = StringVar()
        self.StageVar.set('X')
        self.StageDropDown = OptionMenu(self.ControlXYZ,self.StageVar,'X','Y','Z')
        self.SpeedEntry = Entry(self.ControlXYZ)
        self.SpeedEntry.insert(0,'2000')
        self.SpeedButton = Button(self.ControlXYZ,text='Set',command=self.XYZSetSpeed)
        self.XAbsLabel = Label(self.ControlXYZ,text='X Absolute Move:')
        self.XAbsEntry = Entry(self.ControlXYZ,width=15)
        self.XAbsEntry.insert(0,'7.5')
        self.XAbsDropVar = StringVar()
        self.XAbsDropVar.set('mm')
        self.XAbsDropDown = OptionMenu(self.ControlXYZ, self.XAbsDropVar, 'mm', 'in')
        self.XAbsButton = Button(self.ControlXYZ,text='Move',command=lambda: self.XYZMoveAbsolute('X'))
        self.YAbsLabel = Label(self.ControlXYZ,text='Y Absolute Move:')
        self.YAbsEntry = Entry(self.ControlXYZ)
        self.YAbsEntry.insert(0,'7.5')
        self.YAbsDropVar = StringVar()
        self.YAbsDropVar.set('mm')
        self.YAbsDropDown = OptionMenu(self.ControlXYZ,self.YAbsDropVar,'mm','in')
        self.YAbsButton = Button(self.ControlXYZ,text='Move',command=lambda: self.XYZMoveAbsolute('Y'))
        self.ZAbsLabel = Label(self.ControlXYZ,text='Z Absolute Move:')
        self.ZAbsEntry = Entry(self.ControlXYZ)
        self.ZAbsEntry.insert(0,'7.5')
        self.ZAbsDropVar = StringVar()
        self.ZAbsDropVar.set('mm')
        self.ZAbsDropDown = OptionMenu(self.ControlXYZ,self.ZAbsDropVar,'mm','in')
        self.ZAbsButton = Button(self.ControlXYZ,text='Move',command=lambda: self.XYZMoveAbsolute('Z'))
        
        #Toss on the screen
        self.XMoveLabel.grid(row=0,column=0,columnspan=3)
        self.XZeroButton.grid(row=0,column=3)
        self.YMoveLabel.grid(row=0,column=4,columnspan=3)
        self.YZeroButton.grid(row=0,column=7)
        self.ZMoveLabel.grid(row=0,column=8,columnspan=3)
        self.ZZeroButton.grid(row=0,column=11)
        self.MotorRangeLabel.grid(row=0,column=12,columnspan=4)
        self.XRelLabel.grid(row=1,column=0)
        self.XRelEntry.grid(row=1,column=1)
        self.XRelDropDown.grid(row=1,column=2)
        self.XRelButton.grid(row=1,column=3)
        self.YRelLabel.grid(row=1,column=4)
        self.YRelEntry.grid(row=1,column=5)
        self.YRelDropDown.grid(row=1,column=6)
        self.YRelButton.grid(row=1,column=7)
        self.ZRelLabel.grid(row=1,column=8)
        self.ZRelEntry.grid(row=1,column=9)
        self.ZRelDropDown.grid(row=1,column=10)
        self.ZRelButton.grid(row=1,column=11)
        self.SpeedLabel.grid(row=1,column=12)
        self.StageDropDown.grid(row=1,column=13)
        self.SpeedEntry.grid(row=1,column=14)
        self.SpeedButton.grid(row=1,column=15)
        self.XAbsLabel.grid(row=2,column=0)
        self.XAbsEntry.grid(row=2,column=1)
        self.XAbsDropDown.grid(row=2,column=2)
        self.XAbsButton.grid(row=2,column=3)
        self.YAbsLabel.grid(row=2,column=4)
        self.YAbsEntry.grid(row=2,column=5)
        self.YAbsDropDown.grid(row=2,column=6)
        self.YAbsButton.grid(row=2,column=7)
        self.ZAbsLabel.grid(row=2,column=8)
        self.ZAbsEntry.grid(row=2,column=9)
        self.ZAbsDropDown.grid(row=2,column=10)
        self.ZAbsButton.grid(row=2,column=11)

        #Right when we press the showxyz check if the stage is connected
        if self.XYZConnected == True:
            #if it is connect, get the x,y,z positions and toss them on the screen
            self.XYZ.getresp()
            self.XmmEntry.delete(0,END)
            self.XinEntry.delete(0,END)
            self.YmmEntry.delete(0,END)
            self.YinEntry.delete(0,END)
            self.ZmmEntry.delete(0,END)
            self.ZinEntry.delete(0,END)
            self.XmmEntry.insert(0,str(self.XYZ.getPosition('X')))
            self.XinEntry.insert(0,str(self.XYZ.getPosition('X',english_units=True)))
            self.YmmEntry.insert(0,str(self.XYZ.getPosition('Y')))
            self.YinEntry.insert(0,str(self.XYZ.getPosition('Y',english_units=True)))
            self.ZmmEntry.insert(0,str(self.XYZ.getPosition('Z')))
            self.ZinEntry.insert(0,str(self.XYZ.getPosition('Z',english_units=True)))
            #make the button green as well
            self.XYZConnectButton.grid_forget()
            self.XYZConnectButton = Button(self.InitiateXYZ,text='Connected',fg='white',bg='green',padx=51,pady=5,command=self.ConnectXYZ)
            self.XYZConnectButton.grid(row=1,column=0,columnspan=2)

    def ConnectXYZ(self):
        """self.XYZ = XYZMotion.VXM(self.XYZPortEntry.get(),9600,0.1)
        self.XYZConnected = True
        #Do things to make sure it actually connected
        self.XYZConnectButton.grid_forget()
        self.XYZConnectButton = Button(self.InitiateXYZ,text='Connected',fg='white',bg='green',padx=51,pady=5,command=self.ConnectXYZ)
        self.XYZConnectButton.grid(row=1,column=0)
        #Undo a Disconnect
        self.XYZDisconnectButton.grid_forget()
        self.XYZDisconnectButton = Button(self.InitiateXYZ,text='Disconnect',padx=49,pady=5,command=self.DisconnectXYZ)
        self.XYZDisconnectButton.grid(row=3,column=1)"""
        self.XYZUsed = True
        try:
            self.XYZ = XYZMotion_Station.VXM(self.XYZPortEntry.get(),9600,0.1)
        except:
            self.GeneralMessage('XYZ Stage Did not connect, check connection')
        
        else:
            self.XYZConnected = True
            #Display the current positions
            self.XYZ.getresp()
            self.XmmEntry.delete(0,END)
            self.XinEntry.delete(0,END)
            self.YmmEntry.delete(0,END)
            self.YinEntry.delete(0,END)
            self.ZmmEntry.delete(0,END)
            self.ZinEntry.delete(0,END)
            self.XmmEntry.insert(0,str(self.XYZ.getPosition('X')))
            self.XinEntry.insert(0,str(self.XYZ.getPosition('X',english_units=True)))
            self.YmmEntry.insert(0,str(self.XYZ.getPosition('Y')))
            self.YinEntry.insert(0,str(self.XYZ.getPosition('Y',english_units=True)))
            self.ZmmEntry.insert(0,str(-1*self.XYZ.getPosition('Z')))
            self.ZinEntry.insert(0,str(-1*self.XYZ.getPosition('Z',english_units=True)))
            
            #Do things to make sure it actually connected
            self.XYZConnectButton.grid_forget()
            self.XYZConnectButton = Button(self.InitiateXYZ,text='Connected',fg='white',bg='green',padx=51,pady=5,command=self.ConnectXYZ)
            self.XYZConnectButton.grid(row=1,column=0,columnspan=2)
            #Undo a Disconnect
            self.XYZDisconnectButton.grid_forget()
            self.XYZDisconnectButton = Button(self.InitiateXYZ,text='Disconnect',padx=49,pady=5,command=self.DisconnectXYZ)
            self.XYZDisconnectButton.grid(row=3,column=2)


    def HomeXYZ(self):
        if self.XYZConnected == True:
            self.XYZ.home()
            self.XmmEntry.delete(0,END)
            self.XinEntry.delete(0,END)
            self.YmmEntry.delete(0,END)
            self.YinEntry.delete(0,END)
            self.ZmmEntry.delete(0,END)
            self.ZinEntry.delete(0,END)
            self.XmmEntry.insert(0,str(self.XYZ.getPosition('X')))
            self.XinEntry.insert(0,str(self.XYZ.getPosition('X',english_units=True)))
            self.YmmEntry.insert(0,str(self.XYZ.getPosition('Y')))
            self.YinEntry.insert(0,str(self.XYZ.getPosition('Y',english_units=True)))
            self.ZmmEntry.insert(0,str(self.XYZ.getPosition('Z')))
            self.ZinEntry.insert(0,str(self.XYZ.getPosition('Z',english_units=True)))
            self.XYZHomeButton.grid_forget()
            self.XYZHomeButton = Button(self.InitiateXYZ,text='Homed',bg='green',fg='white',padx=57,pady=5,command=self.HomeXYZ)
            self.XYZHomeButton.grid(row=1,column=2)
            self.XYZGoToExperimental.grid_forget()
            self.XYZGoToExperimental = Button(self.InitiateXYZ,text='Go To Experimental Positions',padx=2,pady=5,command=self.ExperimentalPositions)
            self.XYZGoToExperimental.grid(row=2,column=2)
        else:
            self.GeneralMessage('XYZ Stage was not connected, please connect before pressing home')

    def SetExperimentals(self):
        self.XNewExperimental = self.XYZ.getPosition('X')
        self.YNewExperimental = self.XYZ.getPosition('Y')
        self.ZNewExperimental = self.XYZ.getPosition('Z')
        self.XSetEntry.delete(0,END)
        self.XSetEntry.insert(0,str(self.XNewExperimental))
        self.YSetEntry.delete(0,END)
        self.YSetEntry.insert(0,str(self.YNewExperimental))
        self.ZSetEntry.delete(0,END)
        self.ZSetEntry.insert(0,str(self.ZNewExperimental))
        #Need to add the thing to change the current sets in the status frame

    def ExperimentalPositions(self):
        #Have the function get the current set points from status
        if self.XYZConnected == True:
            XExp = float(self.XSetEntry.get())
            YExp = float(self.YSetEntry.get())
            ZExp = float(self.ZSetEntry.get())
            MoveCheck = self.XYZ.ExperimentalPositions(XExp,YExp,ZExp)
            if MoveCheck !=None:
                self.GeneralMessage(MoveCheck)
            self.XmmEntry.delete(0,END)
            self.XinEntry.delete(0,END)
            self.YmmEntry.delete(0,END)
            self.YinEntry.delete(0,END)
            self.ZmmEntry.delete(0,END)
            self.ZinEntry.delete(0,END)
            self.XmmEntry.insert(0,str(self.XYZ.getPosition('X')))
            self.XinEntry.insert(0,str(self.XYZ.getPosition('X',english_units=True)))
            self.YmmEntry.insert(0,str(self.XYZ.getPosition('Y')))
            self.YinEntry.insert(0,str(self.XYZ.getPosition('Y',english_units=True)))
            self.ZmmEntry.insert(0,str(-1*self.XYZ.getPosition('Z')))
            self.ZinEntry.insert(0,str(-1*self.XYZ.getPosition('Z',english_units=True)))
            #Reset the Home Button
            self.XYZHomeButton.grid_forget()
            self.XYZGoToExperimental.grid_forget()
            self.XYZHomeButton = Button(self.InitiateXYZ,text='Home',padx=62,pady=5,command=self.HomeXYZ)
            self.XYZGoToExperimental = Button(self.InitiateXYZ,text='At Experimental Positions',padx=10,pady=5,command=self.ExperimentalPositions)
            self.XYZHomeButton.grid(row=1,column=2)
            self.XYZGoToExperimental.grid(row=2,column=2)
        else:
            self.GeneralMessage('XYZ Stage was not connected, please connect before moving')
    
    def HideXYZ(self):
        self.XYZFrame.destroy()
        self.XYZFrame = LabelFrame(root, text='Manual Control of XYZ')
        self.XYZFrame.grid(row=1,column=0)
        self.ShowXYZButton = Button(self.XYZFrame,text='Show Control Of XYZ Stage',wraplength=60,padx=50,pady=10,command=self.ShowXYZ)
        self.ShowXYZButton.grid(row=0,column=0,columnspan=3)
        #self.XYZConnected = False

    def DisconnectXYZ(self):
        self.XYZ.__del__()
        self.XYZConnected = False
        #Change the colors of buttons and all that
        self.XYZConnectButton.grid_forget()
        self.XYZConnectButton = Button(self.InitiateXYZ,text='Connect',padx=58,pady=5,command=self.ConnectXYZ)
        self.XYZConnectButton.grid(row=1,column=0,columspan=2)
        #Undo a Disconnect
        self.XYZDisconnectButton.grid_forget()
        self.XYZDisconnectButton = Button(self.InitiateXYZ,text='Disconnected',bg='red',padx=44,pady=5,command=self.DisconnectXYZ)
        self.XYZDisconnectButton.grid(row=3,column=2)

    #Control XYZ Functions
    def ZeroStage(self,Stage):
        if self.XYZConnected == True:
            self.XYZ.moveToZero(Stage)
            if Stage == 'X':
                self.XmmEntry.delete(0,END)
                self.XmmEntry.insert(0,str(self.XYZ.getPosition('X')))
                self.XinEntry.delete(0,END)
                self.XinEntry.insert(0,str(self.XYZ.getPosition('X',english_units=True)))
            elif Stage =='Y':
                self.YmmEntry.delete(0,END)
                self.YmmEntry.insert(0,str(self.XYZ.getPosition('Y')))
                self.YinEntry.delete(0,END)
                self.YinEntry.insert(0,str(self.XYZ.getPosition('Y',english_units=True)))
            elif Stage =='Z':
                self.ZmmEntry.delete(0,END)
                self.ZmmEntry.insert(0,str(self.XYZ.getPosition('Z')))
                self.ZinEntry.delete(0,END)
                self.ZinEntry.insert(0,str(self.XYZ.getPosition('Z',english_units=True)))
            self.XYZGoToExperimental.grid_forget()
            self.XYZGoToExperimental = Button(self.InitiateXYZ,text='Go To Experimental Positions',padx=2,pady=5,command=self.ExperimentalPositions)
            self.XYZGoToExperimental.grid(row=2,column=2)
        else:
            self.GeneralMessage('XYZ Stage was not connected, please connect before moving')

    def XYZMoveRelative(self,Stage):
        if self.XYZConnected == True:
            if Stage == 'X':
                MoveUnits = self.XRelDropVar.get()
                MoveDistance = float(self.XRelEntry.get())
                if MoveUnits == 'mm':
                    MoveCheck = self.XYZ.move_mm('X',MoveDistance)
                    self.XmmEntry.delete(0,END)
                    self.XinEntry.delete(0,END)
                    self.XmmEntry.insert(0,str(self.XYZ.getPosition('X')))
                    self.XinEntry.insert(0,str(self.XYZ.getPosition('X',english_units=True)))
                if MoveUnits == 'in':
                    MoveCheck = self.XYZ.move_in('X',MoveDistance)
                    self.XmmEntry.delete(0,END)
                    self.XinEntry.delete(0,END)
                    self.XmmEntry.insert(0,str(self.XYZ.getPosition('X')))
                    self.XinEntry.insert(0,str(self.XYZ.getPosition('X',english_units=True)))
            elif Stage == 'Y':
                MoveUnits = self.YRelDropVar.get()
                MoveDistance = float(self.YRelEntry.get())
                if MoveUnits == 'mm':
                    MoveCheck = self.XYZ.move_mm('Y',MoveDistance)
                    self.YmmEntry.delete(0,END)
                    self.YinEntry.delete(0,END)
                    self.YmmEntry.insert(0,str(self.XYZ.getPosition('Y')))
                    self.YinEntry.insert(0,str(self.XYZ.getPosition('Y',english_units=True)))
                if MoveUnits == 'in':
                    MoveCheck = self.XYZ.move_in('Y',MoveDistance)
                    self.YmmEntry.delete(0,END)
                    self.YinEntry.delete(0,END)
                    self.YmmEntry.insert(0,str(self.XYZ.getPosition('Y')))
                    self.YinEntry.insert(0,str(self.XYZ.getPosition('Y',english_units=True)))
            elif Stage == 'Z':
                MoveUnits = self.ZRelDropVar.get()
                 #I have added a *-1 so that the stage moves upwards on positive
                MoveDistance = float(self.ZRelEntry.get())*-1
                if MoveUnits == 'mm':
                    MoveCheck = self.XYZ.move_mm('Z',MoveDistance)
                    self.ZmmEntry.delete(0,END)
                    self.ZinEntry.delete(0,END)
                    self.ZmmEntry.insert(0,str(-1*self.XYZ.getPosition('Z')))
                    self.ZinEntry.insert(0,str(-1*self.XYZ.getPosition('Z',english_units=True)))
                if MoveUnits == 'in':
                    MoveCheck = self.XYZ.move_in('Z',MoveDistance)
                    self.ZmmEntry.delete(0,END)
                    self.ZinEntry.delete(0,END)
                    self.ZmmEntry.insert(0,str(-1*self.XYZ.getPosition('Z')))
                    self.ZinEntry.insert(0,str(-1*self.XYZ.getPosition('Z',english_units=True)))
            if MoveCheck != None:
                self.GeneralMessage(MoveCheck)
            #Now Reset the Home and Experimental Positions Buttons
            self.XYZHomeButton.grid_forget()
            self.XYZGoToExperimental.grid_forget()
            self.XYZHomeButton = Button(self.InitiateXYZ,text='Home',padx=62,pady=5,command=self.HomeXYZ)
            self.XYZGoToExperimental = Button(self.InitiateXYZ,text='Go To Experimental Positions',padx=2,pady=5,command=self.ExperimentalPositions)
            self.XYZHomeButton.grid(row=1,column=2)
            self.XYZGoToExperimental.grid(row=2,column=2)
        else:
            self.GeneralMessage('XYZ Stage was not connected, please connect before moving')

    def XYZMoveAbsolute(self,Stage):
        if self.XYZConnected == True:
            if Stage == 'X':
                MoveUnits = self.XAbsDropVar.get()
                MoveTo = float(self.XAbsEntry.get())
                if MoveUnits == 'mm':
                    MoveCheck = self.XYZ.abs_move_mm('X',MoveTo)
                    self.XmmEntry.delete(0,END)
                    self.XinEntry.delete(0,END)
                    self.XmmEntry.insert(0,str(self.XYZ.getPosition('X')))
                    self.XinEntry.insert(0,str(self.XYZ.getPosition('X',english_units=True)))
                if MoveUnits == 'in':
                    MoveCheck = self.XYZ.abs_move_in('X',MoveTo)
                    self.XmmEntry.delete(0,END)
                    self.XinEntry.delete(0,END)
                    self.XmmEntry.insert(0,str(self.XYZ.getPosition('X')))
                    self.XinEntry.insert(0,str(self.XYZ.getPosition('X',english_units=True)))
            elif Stage == 'Y':
                MoveUnits = self.YAbsDropVar.get()
                MoveTo = float(self.YAbsEntry.get())
                if MoveUnits == 'mm':
                    MoveCheck = self.XYZ.abs_move_mm('Y',MoveTo)
                    self.YmmEntry.delete(0,END)
                    self.YinEntry.delete(0,END)
                    self.YmmEntry.insert(0,str(self.XYZ.getPosition('Y')))
                    self.YinEntry.insert(0,str(self.XYZ.getPosition('Y',english_units=True)))
                if MoveUnits == 'in':
                    MoveCheck = self.XYZ.abs_move_in('Y',MoveTo)
                    self.YmmEntry.delete(0,END)
                    self.YinEntry.delete(0,END)
                    self.YmmEntry.insert(0,str(self.XYZ.getPosition('Y')))
                    self.YinEntry.insert(0,str(self.XYZ.getPosition('Y',english_units=True)))
            elif Stage == 'Z':
                MoveUnits = self.ZAbsDropVar.get()
                 #I have added a *-1 so that the stage moves upwards on positive
                MoveTo = float(self.ZAbsEntry.get())*-1
                if MoveUnits == 'mm':
                    MoveCheck = self.XYZ.abs_move_mm('Z',MoveTo)
                    self.ZmmEntry.delete(0,END)
                    self.ZinEntry.delete(0,END)
                    self.ZmmEntry.insert(0,str(-1*self.XYZ.getPosition('Z')))
                    self.ZinEntry.insert(0,str(-1*self.XYZ.getPosition('Z',english_units=True)))
                if MoveUnits == 'in':
                    MoveCheck = self.XYZ.abs_move_in('Z',MoveTo)
                    self.ZmmEntry.delete(0,END)
                    self.ZinEntry.delete(0,END)
                    self.ZmmEntry.insert(0,str(-1*self.XYZ.getPosition('Z')))
                    self.ZinEntry.insert(0,str(-1*self.XYZ.getPosition('Z',english_units=True)))
            if MoveCheck !=None:
                self.GeneralMessage(MoveCheck)
            self.XYZHomeButton.grid_forget()
            self.XYZGoToExperimental.grid_forget()
            self.XYZHomeButton = Button(self.InitiateXYZ,text='Home',padx=62,pady=5,command=self.HomeXYZ)
            self.XYZGoToExperimental = Button(self.InitiateXYZ,text='Go To Experimental Positions',padx=2,pady=5,command=self.ExperimentalPositions)
            self.XYZHomeButton.grid(row=1,column=2)
            self.XYZGoToExperimental.grid(row=2,column=2)
        else:
            self.GeneralMessage('XYZ Stage was not connected, please connect before moving')

    def XYZSetSpeed(self):
        if self.XYZConnected == True:
            Stage = self.StageVar.get()
            Speed = int(self.SpeedEntry.get())
            if Stage =='X':
                self.XYZ.setVelocity('X',Speed)
                self.XSetEntry.delete(0,END)
                self.XSetEntry.insert(0,Speed)
            elif Stage =='Y':
                self.XYZ.setVelocity('Y',Speed)
                self.YSetEntry.delete(0,END)
                self.YSetEntry.insert(0,Speed)
            elif Stage =='Z':
                self.XYZ.setVelocity('Z',Speed)
                self.ZSetEntry.delete(0,END)
                self.ZSetEntry.insert(0,Speed)
        else:
            self.GeneralMessage('XYZ Stage was not connected, please connect before setting speed')

    



root = Tk()
The_GUI = TomographyClass(root)
root.mainloop()        