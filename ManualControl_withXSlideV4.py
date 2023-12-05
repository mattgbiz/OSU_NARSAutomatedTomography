from tkinter import *
import XYZMotion_Station, SMC100Final, NewCameraControl, XSlide #, CameraControl #Commented this out as we have the new file
import time, pytz, subprocess, os.path, os,sys
from datetime import datetime
import numpy as np
from PIL import Image, ImageTk, ImageEnhance

currentPath = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
#print(currentPath)
IconPath = os.path.abspath(os.path.join(currentPath, 'OSU_NRL.ico'))
PNGPath = os.path.abspath(os.path.join(currentPath, 'OSU_NRL.png'))
#print(IconPath)
#print(PNGPath)

class ManualControl:
    def __init__(self,root):
        #Setup the root for the class
        self.root = root
        root.title('Manual Control of XYZ Stage, Rotation Stage, and Camera')
        root.iconbitmap(IconPath)

        tz = pytz.timezone('US/Eastern')
        Columbus_Current_Datetime = str(datetime.now(tz))
        Columbus_Current_Datetime = Columbus_Current_Datetime[0:9] + '_' + Columbus_Current_Datetime[11:12] + '.' + Columbus_Current_Datetime[14:15] + '.' + Columbus_Current_Datetime[17:18] 
        self.StartTime = time.time()
        self.LogName = currentPath + '/ManualControl_'+ str(Columbus_Current_Datetime) + '.txt'
        self.Log = open(self.LogName,'w+')
        self.Log.write('Manual Control started at: {}\r\n'.format(datetime.now(tz)))

        #There are 4 master Frames
        self.CameraFrame = LabelFrame(root, text='Camera Control',padx=160,pady=2)
        self.RotationFrame = LabelFrame(root,text='Rotation Stage Control',padx=10,pady=2)     #original padx was 255
        self.XSlideFrame = LabelFrame(root,text='X Slide Stage Control',padx=10,pady=2) #this was added for controlling the x slide
        self.XYZFrame = LabelFrame(root,text='XYZ Stage Control',padx=10,pady=2)
        self.GeneralFrame = LabelFrame(root, text='General Frame',padx=486,pady=2)
        #Put them on the screen
        self.CameraFrame.grid(row=0,column=0,columnspan=2,padx=2)
        self.RotationFrame.grid(row=1,column=0,padx=2)
        self.XSlideFrame.grid(row=1,column=1,padx=2)
        self.XYZFrame.grid(row=2,column=0,columnspan=2,padx=2)
        self.GeneralFrame.grid(row=3,column=0,columnspan=2,padx=2)

        #***********************************************************************888
        #Camera Control Frame Stuffs
        self.CameraUsed=False
        self.MicroManagerLabel = Label(self.CameraFrame, text='Make sure Micro-Manager is open and configured before starting this file')
        #self.MicroManagerEntry = Entry(self.CameraFrame,width=50)
        #self.MicroManagerEntry.insert(0,'C:/Program Files/Micro-Manager-2.0gamma/ImageJ.exe')
        #self.MicroManagerButton = Button(self.CameraFrame,text='Open MicroManager',command=self.OpenMM)
        self.InitCameraLabel = Label(self.CameraFrame,text='Enter Camera Port:')
        self.InitCameraEntry = Entry(self.CameraFrame,width=50)
        self.InitCameraEntry.insert(0,'COM1')
        self.InitCameraButton = Button(self.CameraFrame, text='Initialize Camera',padx=15,command=self.InitializeCamera)
        self.FileNameLabel = Label(self.CameraFrame,text='Enter the name for the image:')
        self.FileNameEntry = Entry(self.CameraFrame,width=25)
        self.FileNameEntry.insert(0,'TestImage')
        self.FileSuffixLabel = Label(self.CameraFrame,text='Enter Suffix for Name:')
        self.FileSuffixEntry = Entry(self.CameraFrame,width=10)
        self.FileSuffixEntry.insert(0,'1')
        self.FileLocationLabel = Label(self.CameraFrame,text='Enter the filepath to save to:')
        self.FileLocationEntry = Entry(self.CameraFrame,width=50)
        self.FileLocationEntry.insert(0,currentPath)
        self.ExposureTimeLabel = Label(self.CameraFrame,text='Enter the exposure time (s):')
        self.ExposureTimeEntry = Entry(self.CameraFrame,width=25)
        self.ExposureTimeEntry.insert(0,'0.2')
        self.EMGainLabel = Label(self.CameraFrame,text='Enter EM Gain:')
        self.EMGainEntry = Entry(self.CameraFrame,width=10)
        self.EMGainEntry.insert(0,'3')
        self.SaveSnapVar = IntVar()
        self.SaveSnapVar.set(1)
        self.SaveSnapCheck = Checkbutton(self.CameraFrame,text='If checked, the program will save the snap',variable=self.SaveSnapVar)
        self.TakeImageButton = Button(self.CameraFrame,text='Take Image',padx=30,command=self.TakeImage)
        #self.ImageLabel = Label(self.CameraFrame,text='hi')
        #self.BrightLabel = Label(self.CameraFrame,text='Brightness Increased By: ')
        #self.BrightEntry = Entry(self.CameraFrame,width=10)
        #self.BrightEntry.insert(0,'50')
        self.ImageLabel2 = Label(self.CameraFrame,text='bye')
        self.ContrastLabel = Label(self.CameraFrame, text='Contrast Increased By:')
        self.ContrastEntry = Entry(self.CameraFrame,width=10)
        self.ContrastEntry.insert(0,'50')
        #self.ShowImage('C:/Users/mattg_000/Documents/Research/PythonScripts/OSU_NRL.png')
        #self.ShowImage(PNGPath)
        self.ShowContrast(PNGPath)
        #The camera increment button will tell the user how many pictures were taken during the experiment
        self.CameraIncrement = 1

        #Put them on the screen
        self.MicroManagerLabel.grid(row=0,column=0,columnspan=4)
        #self.MicroManagerEntry.grid(row=0,column=1,columnspan=2,sticky='w')
        #self.MicroManagerButton.grid(row=0,column=3,sticky='w')
        self.InitCameraLabel.grid(row=1,column=0)
        self.InitCameraEntry.grid(row=1,column=1,columnspan=2,sticky='w')
        self.InitCameraButton.grid(row=1,column=3,sticky='w')
        self.FileNameLabel.grid(row=2,column=0)
        self.FileNameEntry.grid(row=2,column=1,sticky='w')
        self.FileSuffixLabel.grid(row=2,column=2,sticky='w')
        self.FileSuffixEntry.grid(row=2,column=3,sticky='w')
        self.FileLocationLabel.grid(row=3,column=0)
        self.FileLocationEntry.grid(row=3,column=1,columnspan=2,sticky='w')
        self.ExposureTimeLabel.grid(row=4,column=0)
        self.ExposureTimeEntry.grid(row=4,column=1,sticky='w')
        self.EMGainLabel.grid(row=4,column=2,sticky='w')
        self.EMGainEntry.grid(row=4,column=3,sticky='w')
        self.SaveSnapCheck.grid(row=5,column=0,columnspan=2)
        self.TakeImageButton.grid(row=5,column=3)
        #self.BrightLabel.grid(row=7,column=4)
        #self.BrightEntry.grid(row=7,column=5)
        self.ContrastLabel.grid(row=7,column=6)
        self.ContrastEntry.grid(row=7,column=7)

        #***********************************************************************************************
        #New control of slide for camera stage
        self.SlidePortLabel = Label(self.XSlideFrame, text='Xslide Port:')
        self.SlidePortEntry = Entry(self.XSlideFrame,width=10)
        self.SlidePortEntry.insert(0,'COM8')
        self.SlideConnectButton = Button(self.XSlideFrame, text='Connect XSlide',command=self.XSlideConnect)
        self.SlideCurrentLabel = Label(self.XSlideFrame,text='Current Pos (mm):')
        self.SlideCurrentEntry = Entry(self.XSlideFrame,width=10)
        self.SlideHomeButton = Button(self.XSlideFrame,text='Home',command=self.XSlideHome)
        self.SlideMoveLabel = Label(self.XSlideFrame,text='Relative Move (mm):')
        self.SlideMoveEntry = Entry(self.XSlideFrame,width=10)
        self.SlideMoveButton = Button(self.XSlideFrame, text='Move',command=self.XSlideMoveRel)
        self.SlideInfoLabel = Label(self.XSlideFrame, text='X Slide can extend -69.85 mm back from 0')

        #Put these bad bois on stage
        self.SlidePortLabel.grid(row=0,column=0)
        self.SlidePortEntry.grid(row=0,column=1)
        self.SlideConnectButton.grid(row=0,column=2)
        self.SlideCurrentLabel.grid(row=1,column=0)
        self.SlideCurrentEntry.grid(row=1,column=1)
        self.SlideHomeButton.grid(row=1,column=2)
        self.SlideMoveLabel.grid(row=2,column=0)
        self.SlideMoveEntry.grid(row=2,column=1)
        self.SlideMoveButton.grid(row=2,column=2)
        self.SlideInfoLabel.grid(row=3,column=0,columnspan=3)
        #***********************************************************************************************
        #Now Time for Rotation Stage Control
        self.SMCFirstTest = True
        self.SMCPortLabel = Label(self.RotationFrame,text='Input Port for SMC Controller:')
        self.SMCPortEntry = Entry(self.RotationFrame,width=10)
        self.SMCPortEntry.insert(0,'COM4')
        self.InitializeSMCButton = Button(self.RotationFrame,text='Initialize',padx=60,pady=5,command=self.InitializeSMC)
        self.HomeSMCButton = Button(self.RotationFrame,text='Home Stage',padx=49,pady=5,command=self.HomeSMC)
        self.DisconnectSMCButton = Button(self.RotationFrame,text='Disconnect',padx=52,pady=5,command=self.DisconnectSMC)
        self.CurrentLabel = Label(self.RotationFrame,text='Current Stage Settings')
        self.CurrentPositionLabel = Label(self.RotationFrame,text='Current Position:')
        self.CurrentPositionEntry = Entry(self.RotationFrame,width=30)
        self.CurrentSpeedLabel = Label(self.RotationFrame,text='Current Speed: ')
        self.CurrentSpeedEntry = Entry(self.RotationFrame,width=30)
        self.SMCRangeLabel = Label(self.RotationFrame,text='Position Range: -180 to 180; Speed Range: 1-30')
        self.ControlLabel = Label(self.RotationFrame,text='Stage Control')
        self.SMCRelativeLabel = Label(self.RotationFrame,text='Relative Move (deg):')
        self.SMCRelativeEntry = Entry(self.RotationFrame,width=30)
        self.SMCRelativeEntry.insert(0,'5.0')
        self.SMCRelativeButton = Button(self.RotationFrame,text='Move',command=self.SMCMoveRelative)
        self.SMCAbsoluteLabel = Label(self.RotationFrame,text='Absolute Move (deg):')
        self.SMCAbsoluteEntry = Entry(self.RotationFrame,width=30)
        self.SMCAbsoluteEntry.insert(0,'45.0')
        self.SMCAbsoluteButton = Button(self.RotationFrame,text='Move',command=self.SMCAbsoluteMove)
        self.SMCSpeedLabel = Label(self.RotationFrame,text='Set Speed (deg/s):')
        self.SMCSpeedEntry = Entry(self.RotationFrame,width=30)
        self.SMCSpeedEntry.insert(0,'15')
        self.SMCSpeedButton = Button(self.RotationFrame,text='Set',padx=10,command=self.SMCSetSpeed)
        #Put these on the screen
        self.SMCPortLabel.grid(row=0,column=0)
        self.SMCPortEntry.grid(row=0,column=1)
        self.CurrentLabel.grid(row=0,column=2,columnspan=2)
        self.ControlLabel.grid(row=0,column=4,columnspan=3)
        self.InitializeSMCButton.grid(row=1,column=0,columnspan=2)
        self.CurrentPositionLabel.grid(row=1,column=2)
        self.CurrentPositionEntry.grid(row=1,column=3)
        self.SMCRelativeLabel.grid(row=1,column=4)
        self.SMCRelativeEntry.grid(row=1,column=5)
        self.SMCRelativeButton.grid(row=1,column=6)
        self.HomeSMCButton.grid(row=2,column=0,columnspan=2)
        self.CurrentSpeedLabel.grid(row=2,column=2)
        self.CurrentSpeedEntry.grid(row=2,column=3)
        self.SMCAbsoluteLabel.grid(row=2,column=4)
        self.SMCAbsoluteEntry.grid(row=2,column=5)
        self.SMCAbsoluteButton.grid(row=2,column=6)
        self.DisconnectSMCButton.grid(row=3,column=0,columnspan=2)
        self.SMCRangeLabel.grid(row=3,column=2,columnspan=2)
        self.SMCSpeedLabel.grid(row=3,column=4)
        self.SMCSpeedEntry.grid(row=3,column=5)
        self.SMCSpeedButton.grid(row=3,column=6)

        #*********************************************************************************************************
        #XYZ Stuffs
        self.InitiateXYZ = LabelFrame(self.XYZFrame,text='Initialize XYZ')
        self.StatusXYZ = LabelFrame(self.XYZFrame, text='Status of XYZ')
        self.ControlXYZ = LabelFrame(self.XYZFrame, text='Control XYZ Stage')
        self.XYZUsed = False
        #Toss these baddies
        self.InitiateXYZ.grid(row=0,column=0)
        self.StatusXYZ.grid(row=0,column=1)
        self.ControlXYZ.grid(row=1,column=0,columnspan=2)
        #Initiaze Frame Contents
        self.XYZPortLabel = Label(self.InitiateXYZ, text='Enter Port for XYZ:')
        self.XYZPortEntry = Entry(self.InitiateXYZ,width=10)
        self.XYZPortEntry.insert(0,'COM5')
        #Make a CheckButton for the stage if it is connected with the damper being blocked by something or not
        #This will change the range in z direction
        #self.LimitZVar = IntVar()
        #self.LimitZVar.set(0)
        #self.LimitZCheck = Checkbutton(self.InitiateXYZ,text='Select if Z Direction is Restricted',variable=self.LimitZVar)
        self.XYZConnectButton = Button(self.InitiateXYZ,text='Connect',padx=(58+28),pady=5,command=self.ConnectXYZ)
        self.XYZHomeButton = Button(self.InitiateXYZ,text='Home',padx=(62+28),pady=5,command=self.HomeXYZ)
        self.XYZSetExperimental = Button(self.InitiateXYZ,text='Set Positions as Experimentals',padx=30,pady=5,command=self.SetExperimentals)
        self.XYZGoToExperimental = Button(self.InitiateXYZ,text='Go To Experimental Positions',padx=29,pady=5,command=self.ExperimentalPositions)
        self.XYZGoToSetup = Button(self.InitiateXYZ, text='Go To Setup Positions',padx=40,pady=5,command=self.SetupPositions)
        #self.XYZResetX = Button(self.InitiateXYZ,text='Reset X Zero',pady=5,command=lambda: self.ResetZeroXYZ('X'))
        #self.XYZResetY = Button(self.InitiateXYZ,text='Reset Y Zero',pady=5,command =lambda: self.ResetZeroXYZ('Y'))
        #self.XYZResetZ = Button(self.InitiateXYZ,text='Reset Z Zero',pady=5,command=lambda: self.ResetZeroXYZ('Z'))
        self.XYZDisconnectButton = Button(self.InitiateXYZ,text='Disconnect',padx=(49+28),pady=5,command=self.DisconnectXYZ)
        #Put on screen
        self.XYZPortLabel.grid(row=0,column=0)
        self.XYZPortEntry.grid(row=0,column=1)
        #self.LimitZCheck.grid(row=0,column=2)
        self.XYZConnectButton.grid(row=1,column=0,columnspan=2)
        self.XYZHomeButton.grid(row=1,column=2)
        self.XYZSetExperimental.grid(row=2,column=0,columnspan=2)
        self.XYZGoToExperimental.grid(row=2,column=2)
        #These are intentionally not put on the screen because I don't want people pressing this button by mistake
        #self.XYZResetX.grid(row=3,column=0)
        #self.XYZResetY.grid(row=3,column=1)
        #self.XYZResetZ.grid(row=3,column=2)
        self.XYZGoToSetup.grid(row=3,column=0,columnspan=2)
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
        self.XSetEntry.insert(0,'90.0')
        self.YSetLabel = Label(self.StatusXYZ,text='Y Exp Position (mm):')
        self.YSetEntry = Entry(self.StatusXYZ,width=15)
        self.YSetEntry.insert(0,'124.01')
        self.ZSetLabel = Label(self.StatusXYZ,text='Z Exp Position (mm):')
        self.ZSetEntry = Entry(self.StatusXYZ,width=15)
        self.ZSetEntry.insert(0,'16.0025.0')
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
        #self.XMoveLabel = Label(self.ControlXYZ,text='X Movements: Range +/-63.206mm (2.4884in)')
        self.XMoveLabel = Label(self.ControlXYZ,text='X Movements: Range 0-126.41mm (4.9768in)')
        self.XZeroButton = Button(self.ControlXYZ,text='X Zero',command=lambda: self.ZeroStage('X'))
        #self.YMoveLabel = Label(self.ControlXYZ,text='Y Movements: Range +/-63.632mm (2.5052in)')
        self.YMoveLabel = Label(self.ControlXYZ,text='Y Movements: Range 0-127.260mm (5.0104in)')
        self.YZeroButton = Button(self.ControlXYZ,text='Y Zero',command=lambda: self.ZeroStage('Y'))
        self.ZMoveLabel = Label(self.ControlXYZ,text='Z Movements: Range 0-90mm (3.543in)')
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
        #**********************************************************************************************************
        #General Frame Stuffs
        self.CloseApplicationButton = Button(self.GeneralFrame,text='Close',bg='red',fg='white',padx=40,pady=15, command=self.Stop)
        self.GeneralMessageLabel = Label(self.GeneralFrame,text='General Messages Will Print Here')
        self.MoveMessageLabel = Label(self.GeneralFrame, text='Messages about Stage Movements Will Print Here')
        self.SaveMessageLabel = Label(self.GeneralFrame,text='Message about Save Files Will Print Here')
        self.CloseApplicationButton.grid(row=0,rowspan=3,column=0)
        self.GeneralMessageLabel.grid(row=0,column=1)
        self.MoveMessageLabel.grid(row=1,column=1)
        self.SaveMessageLabel.grid(row=2,column=1)
    
    #************************************************************************************************************************
    #Camera Functions
        
    def InitializeCamera(self):
        """self.Camera = CameraControl.CameraControl()
        print(self.Camera)
        if self.Camera != None:
                self.InitCameraButton.grid_forget()
                self.InitCameraButton = Button(self.CameraFrame,text='Camera Ready',command=self.InitializeCamera)
                self.InitCameraButton.grid(row=1,column=3)"""
        self.CameraUsed = True
        try:
            self.Camera = NewCameraControl.CameraControl(self.InitCameraEntry.get())    #The value that is written in the init camera area
        except:
            self.GeneralMessage('Camera did not connect, check that MicroManager is running and that Camera is connected to proper port')
        else:
            #Change the button to green when it "connects" well
            if self.Camera != None:
                self.InitCameraButton.grid_forget()
                self.InitCameraButton = Button(self.CameraFrame,text='Camera Ready',command=self.InitializeCamera)
                self.InitCameraButton.grid(row=1,column=3)

    def TakeImage(self):
        #Snap an image
        self.ExposureTime = float(self.ExposureTimeEntry.get())*1000    #gets the input time in ms
        #Get the EMGainEntry
        self.EMGain = int(self.EMGainEntry.get())
        #get the suffix
        self.FileSuffix = int(self.FileSuffixEntry.get())
        #self.BrightnessVal = float(self.BrightEntry.get())
        self.ContrastVal = float(self.ContrastEntry.get())
        """
        #work for when I don't have the camera
        self.Image = self.Camera.TakeImage(self.ExposureTime,self.FileLocationEntry.get(),self.FileNameEntry.get(),self.FileSuffix)
        self.ShowImage(self.FileLocationEntry.get()+'/ReSizedJPGs/'+self.FileNameEntry.get()+'_brightened'+str(self.FileSuffix)+'.jpeg')
        self.ShowContrast(self.FileLocationEntry.get()+'/ReSizedJPGs/'+self.FileNameEntry.get()+'_contrast'+str(self.FileSuffix)+'.jpeg')
    
        #Increment the file suffix on the GUI so we are less likely to save over other stuffs
        self.FileSuffixEntry.delete(0,END)
        self.FileSuffix +=1
        self.FileSuffixEntry.insert(0,str(self.FileSuffix))"""
        #if the folder doesn't exist, make it
        self.Folder = self.FileLocationEntry.get()
        if os.path.exists(self.Folder) == False:
            os.mkdir(self.Folder)
            self.GeneralMessage('Created a new folder as input did not exist')

        try:
            self.Image = self.Camera.TakeImage(self.ExposureTime,self.FileLocationEntry.get(),self.FileNameEntry.get(),self.FileSuffix,self.ContrastVal,self.EMGain)
        except:
            self.GeneralMessage('Image was not taken, check that MicroManager is running and camera is connected')
        else:
            #self.ShowImage(self.FileLocationEntry.get()+'/ReSizedJPGs/'+self.FileNameEntry.get()+str(self.FileSuffix)+'_brightened.jpeg')
            self.ShowContrast(self.FileLocationEntry.get()+'/ResizedJPGs/'+self.FileNameEntry.get()+str(self.FileSuffix)+'_contrast.jpeg')
            #Increment the file suffix on the GUI so we are less likely to save over other stuffs
            self.FileSuffixEntry.delete(0,END)
            self.FileSuffix +=1
            self.FileSuffixEntry.insert(0,str(self.FileSuffix))
            if self.SaveSnapVar.get() == 0:     #If the button is not checked, delete these images
                os.remove(self.FileLocationEntry.get()+'/ReSizedJPGs/'+self.FileNameEntry.get()+str(self.CameraIncrement)+'.jpeg')
                #os.remove(self.FileLocationEntry.get()+'/ReSizedJPGs/'+self.FileNameEntry.get()+str(self.CameraIncrement)+'_brightened.jpeg')
                os.remove(self.FileLocationEntry.get()+'/ReSizedJPGs/'+self.FileNameEntry.get()+str(self.CameraIncrement)+'_contrast.jpeg')
                os.remove(self.FileLocationEntry.get()+'/'+self.FileNameEntry.get()+str(self.CameraIncrement)+'.tif')
                os.remove(self.FileLocationEntry.get()+'/'+self.FileNameEntry.get()+str(self.CameraIncrement)+'_contrast.tif')
            else:
                self.SaveMessage('File was saved as {} in location {}'.format(self.FileNameEntry.get(),self.FileLocationEntry.get()))
                self.Log.write('An image named {} was taken with Exp time {}s and EM Gain {}\r\n'.format(self.FileNameEntry.get(),(self.ExposureTime/1000),self.EMGain))

    """def ShowImage(self,ImagePath):
        self.ImageToShow = Image.open(ImagePath)
        self.ImageToShow = self.ImageToShow.resize((225,225),Image.ANTIALIAS)
        self.ReferencedImage = ImageTk.PhotoImage(self.ImageToShow)
        self.ImageLabel.grid_forget()
        self.ImageLabel = Label(self.CameraFrame,image=self.ReferencedImage)
        self.ImageLabel.image=self.ReferencedImage
        self.ImageLabel.grid(row=0,rowspan=6,column=4,columnspan=2)"""

    def ShowContrast(self,ImagePath2):
        self.ImageToShow2 = Image.open(ImagePath2)
        self.ImageToShow2 = self.ImageToShow2.resize((225,225),Image.ANTIALIAS)
        self.ReferencedImage2 = ImageTk.PhotoImage(self.ImageToShow2)
        self.ImageLabel2.grid_forget()
        self.ImageLabel2 = Label(self.CameraFrame, image=self.ReferencedImage2)
        self.ImageLabel2.image=self.ReferencedImage2
        self.ImageLabel2.grid(row=0,rowspan=6,column=6,columnspan=2)

    #********************************************************************************
    #Rotation Stage Functions
    def InitializeSMC(self):
        print('Connecting to SMC')
        if self.SMCFirstTest == True:
            try:
                SMCTest = SMC100Final.test_general(self.SMCPortEntry.get())
            except:
                self.GeneralMessage('Rotataion stage failed to connect, check COM input or connections')
            else:
                if SMCTest == 1:
                    self.SMC = SMC100Final.SMC100(1,self.SMCPortEntry.get())
                    self.InitializeSMCButton.grid_forget()
                    self.InitializeSMCButton = Button(self.RotationFrame,text='Connected',bg='green',fg='white',padx=52,pady=5,command=self.InitializeSMC)
                    self.InitializeSMCButton.grid(row=1,column=0,columnspan=2)
                    self.DisconnectSMCButton.grid_forget()
                    self.DisconnectSMCButton = Button(self.RotationFrame,text='Disconnect',padx=52,pady=5,command=self.DisconnectSMC)
                    self.DisconnectSMCButton.grid(row=3,column=0,columnspan=2)
                    self.SMCFirstTest = False
                else:
                    self.GeneralMessage('Rotation stage failed test, retry test by hitting connect again')
        else:
            try:
                self.SMC = SMC100Final.SMC100(1,self.SMCPortEntry.get())
            except:
                self.GeneralMessage('Rotation could not reconnect, check prints for reasons why')
            else:
                self.InitializeSMCButton.grid_forget()
                self.InitializeSMCButton = Button(self.RotationFrame,text='Connected',bg='green',fg='white',padx=52,pady=5,command=self.InitializeSMC)
                self.InitializeSMCButton.grid(row=1,column=0,columnspan=2)
                self.DisconnectSMCButton.grid_forget()
                self.DisconnectSMCButton = Button(self.RotationFrame,text='Disconnect',padx=52,pady=5,command=self.DisconnectSMC)
                self.DisconnectSMCButton.grid(row=3,column=0,columnspan=2)
    def HomeSMC(self):
        print('Homing SMC')
        try:
            self.SMC.home()
        except:
            self.GeneralMessage('Rotation stage did not respond, check connection')
        else:
            if round(self.SMC.get_position_mm(),1) == 0:
                self.MoveMessage('Rotation stage was just homed')
                self.Log.write('Rotation stage was homed\r\n')
                self.HomeSMCButton.grid_forget()
                self.HomeSMCButton = Button(self.RotationFrame,text='Homed',bg='green',fg='white',padx=61,pady=5,command=self.HomeSMC)
                self.HomeSMCButton.grid(row=2,column=0,columnspan=2)
                self.CurrentPositionEntry.delete(0,END)
                self.CurrentPositionEntry.insert(0,str(self.SMC.get_position_mm()))
            else:
                print('Did not home')
                self.GeneralMessage('SMC failed to get close enough to 0 deg, check connection or try again')
    
    def DisconnectSMC(self):
        try: 
            self.SMC.close()
        except:
            self.GeneralMessage('Rotation stage was not disconnected')
        else:
            time.sleep(1)
            del self.SMC
            self.DisconnectSMCButton.grid_forget()
            self.DisconnectSMCButton = Button(self.RotationFrame,text='Disconnected',bg='red',fg='white',padx=46,pady=5,command=self.DisconnectSMC)
            self.DisconnectSMCButton.grid(row=3,column=0,columnspan=2)
            self.InitializeSMCButton.grid_forget()
            self.InitializeSMCButton = Button(self.RotationFrame,text='Initialize',padx=60,pady=5,command=self.InitializeSMC)
            self.InitializeSMCButton.grid(row=1,column=0,columnspan=2)
            print('Disconnecting from SMC')
   
    def SMCMoveRelative(self):
        print('Relative Move')
        try:
            self.SMC.improved_move(float(self.SMCRelativeEntry.get()),int(self.SMCSpeedEntry.get()))
        except:
            self.GeneralMessage('Move failed, check connections')
        else:    
            self.MoveMessage('Rotation stage performed move relative {}'.format(self.SMCRelativeEntry.get()))
            self.HomeSMCButton.grid_forget()
            self.HomeSMCButton = Button(self.RotationFrame,text='Home Stage',padx=49,pady=5,command=self.HomeSMC)
            self.HomeSMCButton.grid(row=2,column=0,columnspan=2)
            self.CurrentPositionEntry.delete(0,END)
            self.CurrentPositionEntry.insert(0,str(self.SMC.get_position_mm()))
            self.MoveMessage('Last move was a relative move of {} deg by rotation stage'.format(self.SMCRelativeEntry.get()))
            self.Log.write('Last move was a relative move of {} deg by rotation stage'.format(self.SMCRelativeEntry.get()))
    
    def SMCAbsoluteMove(self):
        print('Absolute Move')
        try:
            self.SMC.improved_move_abs(float(self.SMCAbsoluteEntry.get()),int(self.SMCSpeedEntry.get()))
        except:
            self.GeneralMessage('Move failed, check connections')
        else:
            self.MoveMessage('Rotation stage performed move absolute {}'.format(self.SMCAbsoluteEntry.get()))
            self.HomeSMCButton.grid_forget()
            self.HomeSMCButton = Button(self.RotationFrame,text='Home Stage',padx=49,pady=5,command=self.HomeSMC)
            self.HomeSMCButton.grid(row=2,column=0,columnspan=2)
            self.CurrentPositionEntry.delete(0,END)
            self.CurrentPositionEntry.insert(0,str(self.SMC.get_position_mm()))
            self.MoveMessage('Last move was an absolute of {} deg by rotation stage'.format(self.SMCAbsoluteEntry.get()))
            self.Log.write('Last move was a absolute move to {} deg by rotation stage'.format(self.SMCAbsoluteEntry.get()))
    def SMCSetSpeed(self):
        try:
            self.SMC.set_velocity(float(self.SMCSpeedEntry.get()))
        except:
            self.GeneralMessage('Setting velocity failed, check connection')
        else:
            self.CurrentSpeedEntry.delete(0,END)
            self.CurrentSpeedEntry.insert(0,str(self.SMC.get_velocity()))
        print('Set Speed')
    #*********************************************************************************
    #XYZ Frame Functions
    def ConnectXYZ(self):
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
            self.YmmEntry.insert(0,str(-1*self.XYZ.getPosition('Y')))
            self.YinEntry.insert(0,str(-1*self.XYZ.getPosition('Y',english_units=True)))
            self.ZmmEntry.insert(0,str(-1*self.XYZ.getPosition('Z')))
            self.ZinEntry.insert(0,str(-1*self.XYZ.getPosition('Z',english_units=True)))

            #Do things to make sure it actually connected
            self.XYZConnectButton.grid_forget()
            self.XYZConnectButton = Button(self.InitiateXYZ,text='Connected',fg='white',bg='green',padx=(51+28),pady=5,command=self.ConnectXYZ)
            self.XYZConnectButton.grid(row=1,column=0,columnspan=2)
            #Undo a Disconnect
            self.XYZDisconnectButton.grid_forget()
            self.XYZDisconnectButton = Button(self.InitiateXYZ,text='Disconnect',padx=(49+28),pady=5,command=self.DisconnectXYZ)
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
            self.XYZHomeButton = Button(self.InitiateXYZ,text='Homed',bg='green',fg='white',padx=(57+28),pady=5,command=self.HomeXYZ)
            self.XYZHomeButton.grid(row=1,column=2)
            self.XYZGoToExperimental.grid_forget()
            self.XYZGoToExperimental = Button(self.InitiateXYZ,text='Go To Experimental Positions',padx=29,pady=5,command=self.ExperimentalPositions)
            self.XYZGoToExperimental.grid(row=2,column=2)
        else:
            self.GeneralMessage('XYZ Stage was not connected, please connect before pressing home')

    def SetExperimentals(self):
        try:
            self.XNewExperimental = self.XYZ.getPosition('X')
            self.YNewExperimental = (-1*self.XYZ.getPosition('Y'))
            self.ZNewExperimental = (-1*self.XYZ.getPosition('Z'))
        except:
            self.GeneralMessage('XYZ Stage not connected, check connection')
        else:
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
            YExp = float(self.YSetEntry.get())*-1       #Have the -1 here as y convention is flipped
            ZExp = float(self.ZSetEntry.get())*-1       #Have the -1 here as z convention is flipped
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
            self.YmmEntry.insert(0,str(-1*self.XYZ.getPosition('Y')))
            self.YinEntry.insert(0,str(-1*self.XYZ.getPosition('Y',english_units=True)))
            self.ZmmEntry.insert(0,str(-1*self.XYZ.getPosition('Z')))
            self.ZinEntry.insert(0,str(-1*self.XYZ.getPosition('Z',english_units=True)))
            #Reset the Home Button
            self.XYZHomeButton.grid_forget()
            self.XYZGoToExperimental.grid_forget()
            self.XYZHomeButton = Button(self.InitiateXYZ,text='Home',padx=(62+28),pady=5,command=self.HomeXYZ)
            self.XYZGoToExperimental = Button(self.InitiateXYZ,text='At Experimental Positions',padx=(10+28),pady=5,command=self.ExperimentalPositions)
            self.XYZHomeButton.grid(row=1,column=2)
            self.XYZGoToExperimental.grid(row=2,column=2)
        else:
            self.GeneralMessage('XYZ Stage was not connected, please connect before moving')

    def SetupPositions(self):
            #Have the function get the current set points from status
            if self.XYZConnected == True:
                XSetup = float('0.001')
                YSetup = float('-0.001')
                ZSetup = float('-0.001')  #using -5.0 as I have z orientation flipped for convenience
                MoveCheck = self.XYZ.SetupPositions(XSetup,YSetup,ZSetup)
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
                self.YmmEntry.insert(0,str(-1*self.XYZ.getPosition('Y')))                       #y and z conventions flipped
                self.YinEntry.insert(0,str(-1*self.XYZ.getPosition('Y',english_units=True)))
                self.ZmmEntry.insert(0,str(-1*self.XYZ.getPosition('Z')))
                self.ZinEntry.insert(0,str(-1*self.XYZ.getPosition('Z',english_units=True)))
                #Reset the Home Button
                self.XYZHomeButton.grid_forget()
                self.XYZGoToExperimental.grid_forget()
                self.XYZHomeButton = Button(self.InitiateXYZ,text='Home',padx=(62+28),pady=5,command=self.HomeXYZ)
                #self.XYZGoToExperimental = Button(self.InitiateXYZ,text='At Experimental Positions',padx=(10+28),pady=5,command=self.ExperimentalPositions)
                self.XYZGoToExperimental = Button(self.InitiateXYZ,text='Go To Experimental Positions',padx=29,pady=5,command=self.ExperimentalPositions)
                self.XYZHomeButton.grid(row=1,column=2)
                self.XYZGoToExperimental.grid(row=2,column=2)
            else:
                self.GeneralMessage('XYZ Stage was not connected, please connect before moving')

    #Function to zero the stages if need be
    def ResetZeroXYZ(self,Stage):
        try:
            self.XYZ.FindZero(Stage)
        except:
            self.GeneralMessage('XYZ Stage was not connected or lost connection')
        else:
            if Stage == 'X':
                self.XmmEntry.delete(0,END)
                self.XinEntry.delete(0,END)
                self.XmmEntry.insert(0,str(self.XYZ.getPosition('X')))
                self.XinEntry.insert(0,str(self.XYZ.getPosition('X',english_units=True)))
            elif Stage =='Y':
                self.YmmEntry.delete(0,END)
                self.YinEntry.delete(0,END)
                self.YmmEntry.insert(0,str(self.XYZ.getPosition('Y')))
                self.YinEntry.insert(0,str(self.XYZ.getPosition('Y',english_units=True)))
            elif Stage =='Z':
                self.ZmmEntry.delete(0,END)
                self.ZinEntry.delete(0,END)          
                self.ZmmEntry.insert(0,str(self.XYZ.getPosition('Z')))
                self.ZinEntry.insert(0,str(self.XYZ.getPosition('Z',english_units=True)))

    def DisconnectXYZ(self):
        try:
            self.XYZ.__del__()
        except:
            self.GeneralMessage('XYZ Stage was not connected or lost connection')
        else:
            self.XYZConnected = False
            #Change the colors of buttons and all that
            self.XYZConnectButton.grid_forget()
            self.XYZConnectButton = Button(self.InitiateXYZ,text='Connect',padx=(58+28),pady=5,command=self.ConnectXYZ)
            self.XYZConnectButton.grid(row=1,column=0,columnspan=2)
            #Undo a Disconnect
            self.XYZDisconnectButton.grid_forget()
            self.XYZDisconnectButton = Button(self.InitiateXYZ,text='Disconnected',bg='red',padx=(44+28),pady=5,command=self.DisconnectXYZ)
            self.XYZDisconnectButton.grid(row=3,column=2)

    #Control XYZ Functions
    def ZeroStage(self,Stage):
        if self.XYZConnected == True:
            if Stage == 'X':
                #check to make sure X wont hit the box if pressing zero button
                YLimitCheck = self.XYZ.getPosition('Y',step_units=True)
                print(YLimitCheck>=-6800)
                if YLimitCheck >=-6800:
                    self.XYZ.moveToZero(Stage)
                else:
                    self.GeneralMessage('Did not zero X stage as it would hit box, move Y towards 0')
            elif Stage == 'Y' or Stage == 'Z':
                self.XYZ.moveToZero(Stage)

            #self.XYZ.moveToZero(Stage)
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
                MoveDistance = float(self.YRelEntry.get())*-1       #y convention flipped
                if MoveUnits == 'mm':
                    MoveCheck = self.XYZ.move_mm('Y',MoveDistance)
                    self.YmmEntry.delete(0,END)
                    self.YinEntry.delete(0,END)
                    self.YmmEntry.insert(0,str(-1*self.XYZ.getPosition('Y')))
                    self.YinEntry.insert(0,str(-1*self.XYZ.getPosition('Y',english_units=True)))
                if MoveUnits == 'in':
                    MoveCheck = self.XYZ.move_in('Y',MoveDistance)
                    self.YmmEntry.delete(0,END)
                    self.YinEntry.delete(0,END)
                    self.YmmEntry.insert(0,str(-1*self.XYZ.getPosition('Y')))
                    self.YinEntry.insert(0,str(-1*self.XYZ.getPosition('Y',english_units=True)))
            elif Stage == 'Z':
                MoveUnits = self.ZRelDropVar.get()
                #I have added the *-1 to the move so that the stage moves upwards with positive input
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
            if Stage == 'X':
                self.MoveMessage('XYZ stage performed move relative {}{} on stage {}'.format(str(MoveDistance),MoveUnits,Stage))
            else: 
                self.MoveMessage('XYZ stage performed move relative {}{} on stage {}'.format(str(-1*MoveDistance),MoveUnits,Stage))
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
                MoveTo = float(self.YAbsEntry.get())*-1         #y convention flipped
                if MoveUnits == 'mm':
                    MoveCheck = self.XYZ.abs_move_mm('Y',MoveTo)
                    self.YmmEntry.delete(0,END)
                    self.YinEntry.delete(0,END)
                    self.YmmEntry.insert(0,str(-1*self.XYZ.getPosition('Y')))
                    self.YinEntry.insert(0,str(-1*self.XYZ.getPosition('Y',english_units=True)))
                if MoveUnits == 'in':
                    MoveCheck = self.XYZ.abs_move_in('Y',MoveTo)
                    self.YmmEntry.delete(0,END)
                    self.YinEntry.delete(0,END)
                    self.YmmEntry.insert(0,str(-1*self.XYZ.getPosition('Y')))
                    self.YinEntry.insert(0,str(-1*self.XYZ.getPosition('Y',english_units=True)))
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
            if Stage == 'X':
                self.MoveMessage('XYZ stage performed move absolute to {}{} on stage {}'.format(str(MoveTo),MoveUnits,Stage))
            else:
                self.MoveMessage('XYZ stage performed move absolute to {}{} on stage {}'.format(str(-1*MoveTo),MoveUnits,Stage))
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
                self.XSpeedEntry.delete(0,END)
                self.XSpeedEntry.insert(0,Speed)
                #self.XSetEntry.delete(0,END)
                #self.XSetEntry.insert(0,Speed)
            elif Stage =='Y':
                self.XYZ.setVelocity('Y',Speed)
                self.YSpeedEntry.delete(0,END)
                self.YSpeedEntry.insert(0,Speed)
                #self.YSetEntry.delete(0,END)
                #self.YSetEntry.insert(0,Speed)
            elif Stage =='Z':
                self.XYZ.setVelocity('Z',Speed)
                self.ZSpeedEntry.delete(0,END)
                self.ZSpeedEntry.insert(0,Speed)
                #self.ZSetEntry.delete(0,END)
                #self.ZSetEntry.insert(0,Speed)
        else:
            self.GeneralMessage('XYZ Stage was not connected, please connect before setting speed')

    #Xslide Frame Functions
    def XSlideConnect(self):
        #self.XYZUsed = True
        try:
            self.XSlide = XSlide.VXM(self.SlidePortEntry.get(),9600,0.1)
        except:
            self.GeneralMessage('XSlide Did not connect, check connection')
        else:
            self.XSlideConnected = True
            #Display the current positions
            self.XSlide.getresp()
            self.SlideCurrentEntry.delete(0,END)
            self.SlideCurrentEntry.insert(0,str(self.XSlide.getPosition('X')))
            
            #Do things to make sure it actually connected
            self.SlideConnectButton.grid_forget()
            self.SlideConnectButton = Button(self.XSlideFrame,text='Connected',fg='white',bg='green',padx=(2),pady=5,command=self.XSlideConnect)
            self.SlideConnectButton.grid(row=0,column=2)

    def XSlideHome(self):
            if self.XSlideConnected == True:
                self.XSlide.home()
                self.XSlide.getresp()
                self.SlideCurrentEntry.delete(0,END)
                self.SlideCurrentEntry.insert(0,str(self.XSlide.getPosition('X')))
                self.SlideHomeButton.grid_forget()
                self.SlideHomeButton = Button(self.XSlideFrame,text='Homed',bg='green',fg='white',padx=1,pady=5,command=self.XSlideHome)
                self.SlideHomeButton.grid(row=1,column=2)
            else:
                self.GeneralMessage('X Slide was not connected, please connect before pressing home')

    def XSlideMoveRel(self):
        if self.XSlideConnected == True:
            MoveDistance = float(self.SlideMoveEntry.get())
            print('Move distance was {}'.format(MoveDistance))
            MoveCheck = self.XSlide.move_mm('X',MoveDistance)
            self.SlideCurrentEntry.delete(0,END)
            self.SlideCurrentEntry.insert(0,str(self.XSlide.getPosition('X')))
            if MoveCheck != None:
                self.GeneralMessage(MoveCheck)
            else: 
                self.MoveMessage('XSlide performed move relative {}'.format(str(MoveDistance)))
                #Now Reset the Home and Experimental Positions Buttons
                self.SlideHomeButton.grid_forget()
                self.SlideHomeButton = Button(self.XSlideFrame,text='Home',padx=1,pady=5,command=self.XSlideHome)
                self.SlideHomeButton.grid(row=1,column=2)
        else:
            self.GeneralMessage('X Slide was not connected, please connect before moving')

    #********************************************************************************
    #general Frame functions
    def Stop(self):
        print('Closing out')
        #Attempt to close out both the XYZ and rotation stage only if they were used
        if self.XYZUsed == True:
            try:
                self.XYZ = XYZMotion_Station.VXM(self.XYZPortEntry.get(),9600,0.1,22050)
            except:
                try:
                    self.XYZ.home()
                    self.XYZ.__del__()
                except:
                    self.GeneralMessage('Error in closing, XYZ stage would not home')
                    self.XYZClose = False
                else:
                    self.XYZClose = True
            else:
                self.XYZ.home()
                self.XYZ.__del__()
                self.XYZClose = True
        else:
            self.XYZClose = True
        #Close the SMC stage out only if it had previously been opened
        if self.SMCFirstTest == False:
            try:
                self.SMC = SMC100Final.SMC100(1,self.SMCPortEntry.get())
            except:
                try:
                    self.SMC.home()
                    self.SMC.close()
                
                except:
                    self.MoveMessage('Error in closing, rotation stage would not home')
                    self.SMCClose = False
                else:
                    self.SMCClose = True
            else:
                self.SMC.home()
                self.SMC.close()
                self.SMCClose = True
        else:
            self.SMCClose = True
        #close the camera out if it was used
        if self.CameraUsed == True:
            try:
                self.Camera.CloseCamera()
            except:
                self.SaveMessage('Camera did not close out')
                self.CameraClose = False
            else:
                self.CameraClose = True
        else:
            self.CameraClose = True
        if self.XYZClose == True and self.SMCClose == True and self.CameraClose ==True:
            #only close if both get homed
            root.destroy()

    def GeneralMessage(self,Message):
        self.GeneralMessageLabel.grid_forget()
        self.GeneralMessageLabel = Label(self.GeneralFrame,text=str(Message))
        self.GeneralMessageLabel.grid(row=0,column=1)
    
    def MoveMessage(self,Message):
        self.MoveMessageLabel.grid_forget()
        self.MoveMessageLabel = Label(self.GeneralFrame, text=str(Message))
        self.MoveMessageLabel.grid(row=1,column=1)

    def SaveMessage(self,Message):
        self.SaveMessageLabel.grid_forget()
        self.SaveMessageLabel = Label(self.GeneralFrame,text=str(Message))
        self.SaveMessageLabel.grid(row=2,column=1)

root = Tk()
The_GUI = ManualControl(root)
root.mainloop()  