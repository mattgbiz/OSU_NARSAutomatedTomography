### XYZ Stage from Velmex Controlled by VXM Controller ###
"""
**********************************************************
*     Developed By: Ohio State University NARS Lab       *
*                 Developer: Matt Bisbee                 *
*               Very Early Version of code               * 
**********************************************************
"""

from serial import Serial
import time
#port is from my computer and baud rate is from his specs
#port = 'COM3'
#baud = 9600
#maxWaitTime = 0.1 #this is in seconds and I will play around with it
#XYZ = serial.Serial(port='COM4',baudrate=9600,timeout=5)

#get some constants/defaults
defaultVelocity = 2000
stepsTomm = 0.0025
mmToSteps = (1/0.0025)
mmToin = (1/25.4)
inTomm = 25.4


#Make a Class for the VXM Stage
class VXM(object):
    #initialize our stage
    def __init__(self, port, baud, maxWaitTime):
        self._port = Serial(port=port,baudrate=baud,timeout=maxWaitTime)
        print('Initializing Stage on port: %s' %(port))
        startTime = time.time()
        initialized = False
        while initialized == False:
            if time.time() - startTime < 10.0:
                #I'm going to want a try statement here but I cant remember the exception
                self.sendcmd('F',silent=False)
                self.sendcmd('V',silent=False)
                status = self.getresp(silent=False)
                if status == 'R':
                    initialized = True
                    print('stage is connected')
                    #set default motor speeds: The manual says 2000 steps/second is good
                    self.setVelocity('X',defaultVelocity)
                    self.getresp()
            else:
                initialized = True
                print('Stage did not connect, try again')
                
        

    def home(self):
        #Move all of the stages to 0 starting with Z to avoid running into things
        self.moveToZero('X')
        time.sleep(0.2)
        self.getAllPositions()

    def ExperimentalPositions(self,XPosition,english_units=False):
        #This function sends the stage to the set experimental locations
        #if XPosition != 0 or XPosition != -0 or YPosition != 0 or YPosition !=-0 or ZPosition!=0 or ZPosition!=-0
        if english_units == True:
            XSteps = XPosition*inTomm*mmToSteps
        else:
            XSteps = XPosition*mmToSteps
        #Now that the steps have been found, check that we wont be passing a zero
        XSteps = self.CheckZero(XSteps)
        ErrorX = self.CheckLimits('X',XSteps)
        if ErrorX != None:
            return 'One of the stages would gone beyond the limit'
        else:
            #Now send the move
            MoveMessage = 'F,C,IA1M' + str(XSteps) + ',R'
            self.sendcmd(MoveMessage)
            self.waitReady()
        

    def CheckZero(self,Position):
        #assert Stage == 'X' or Stage == 'Y' or Stage == 'Z'
        if Position == 0:
            #move the step to be 1 so it does not go to 0 
            Position = 1
            return Position
        elif Position == -0:
            Position = 1
            return Position    
        else:
            Position = Position
            return Position

    #provide function for sending commands
    def sendcmd(self, commandString, silent=True):
        #add the return variable \r and convert to bytes
        stringToSend = (commandString + '\r').encode()
        #flush the input buffer
        self._port.flushInput()
        self._port.write(stringToSend)
        if silent == False:
            print('Sent Stage Command: %s' %(commandString))

    #Function for getting response from stage
    def getresp(self, silent=True):
        resp = self._port.readline().decode() #the decode makes it be a string not a byte string aka 'string' not b'string'
        if silent == False:
            print(resp)
        #flush the output buffer
        self._port.flushOutput()    
        return resp  

    def waitReady(self, silent=True):
        #I want this command to go into all moves and things that take time
        #When one sends V to the stage, it returns B if busy, R if ready, J if in jog/slew mode, b if Jog/Slewing
        #need to wait for it to return R
        status = 'S'        #calling it S for start
        while status != 'R':
            if silent == False:
                print('Sending command V')
            self.sendcmd('V')
            #now get a response
            status=self.getresp()
            if silent == False:
                print('Got a response: %s' %(status))
            time.sleep(0.1) #sleep for a tenth of a second
        
            
    
    #Function to get individual stage position
    def getPosition(self, Stage, metric_units=True, english_units=False, step_units=False):
        assert Stage == 'X'
        self.sendcmd(Stage)
        stageResp = str(self.getresp())
        #pull the number out of string
        stageNum = int(stageResp[1:8])    #turns the string of 7 digits into an integer  
        #print(stageResp)
        #print(stageNum)
        if stageResp[0] == '-':          #see if second value is + or -
            stageNum = stageNum*(-1)      #if negative, make it a negative value
        #Convert from steps to mm 0.0050 is in manual
        stagemm = float(stepsTomm*stageNum)
        stagein = stagemm/25.4 
        #print it out
        #by default, metric units is true, so if we want english units to be displayed, specifcy english_units = True in the function call
        if step_units == True:
            if Stage == 'X':
                print('X Position: {} steps'.format(stageNum))
            return stageNum     
        if english_units == True:
            if Stage == 'X':
                print('X Position: %fin' %(stagein))
            return stagein        
        if metric_units == True:
            if Stage == 'X':
                print('X Position: %fmm' %(stagemm)) 
            return stagemm


    #Function to get the X,Y,Z positions at same time
    def getAllPositions(self, metric_units = True, english_units = False):
        self.sendcmd('X',silent=False)       #gets X position
        Xresp = str(self.getresp(silent=False))          
        #get values from the strings
        #The first part of response is the axis, second is + or - and last 7 are the positions
        def getNumber(Axisresp):
            Axisnum = int(Axisresp[2:9])    #turns the string of 7 digits into an integer  
            if Axisresp[1] == '-':          #see if second value is + or -
                Axisnum = Axisnum*(-1)      #if negative, make it a negative value
            return Axisnum
        Xnum = getNumber(Xresp) #turns the string of 7 digits into an integer
        #Conversions 1 step is 0.0050mm
        Xmm = float(stepsTomm*Xnum)           #make these values float since they were integers

        #conversion 25.4 mm is 1 in
        Xin = Xmm/25.4
        #time.sleep(1)
        #print('Stage Positions- {} {} {}'.format(Xresp,Yresp,Zresp)) #it doesnt like this print for some reason
        #by default, metric units is true, so if we want english units to be displayed, specifcy english_units = True in the function call
        if english_units == True:
            print('Stage Positions: X=%fin' %(Xin))
            return Xin
        if metric_units == True:
            print('Stage Positions: X=%fmm' %(Xmm))
            return Xmm

    def setVelocity(self, Stage, Speed):
        #make sure someone is only trying to input velocity for one of the 3 axes
        assert Stage == 'X'
        assert Speed > 0 and Speed <= 6000 #the motor speed must be in range 1-6000  
        if Stage == 'X':
            Velocity = 'E,C,S1M' + str(Speed) + ',R'
            self.sendcmd(Velocity)
            print('Velocity of Stage %s set to %s' %(Stage,Speed))
        else:
            print('Did not set a speed to a stage') 
            
    def moveToZero(self,Stage):
        assert Stage == 'X' or Stage == 'Y' or Stage == 'Z'
        #make the command to move to zero
        if Stage == 'X':
            Zero = 'E,C,IA1M0,R'
        self.sendcmd(Zero)
        #now we have sent the command to move the stage back to zero
        #need to wait for the stage to finish getting to zero
        self.waitReady()
    
    def move_mm(self,Stage,dist_mm):
        assert Stage == 'X' 
        #get the distance in mm to be in steps not mm
        dist_step = dist_mm*mmToSteps
        dist_step = self.CheckZero(dist_step)
        dist_end = self.getPosition(Stage,step_units=True) + dist_step
        Error = self.CheckLimits(Stage,dist_end)
        if Error != None:
            return Error
        else:
            #make the command to move the stage
            if Stage == 'X':
                movemm = 'E,C,I1M' + str(dist_step) +',R'
            self.sendcmd(movemm)
            #now we have sent the command to move the stage back to zero
            #need to wait for the stage to finish getting to zero
            self.waitReady()
        
    
    def move_in(self,Stage,dist_in):
        assert Stage == 'X'
        #get the distance in mm to be in steps not mm
        dist_step = dist_in*inTomm*mmToSteps
        dist_step = self.CheckZero(dist_step)
        dist_end = self.getPosition(Stage, step_units=True) + dist_step
        Error = self.CheckLimits(Stage,dist_end)
        if Error != None:
            return Error
        else:
            #make the command to move the stage
            if Stage == 'X':
                movein = 'E,C,I1M' + str(dist_step) +',R'
            self.sendcmd(movein)
            #now we have sent the command to move the stage back to zero
            #need to wait for the stage to finish getting to zero
            self.waitReady()
        
    def abs_move_mm(self,Stage,Position_mm):
        assert Stage == 'X'
        Pos_Step = Position_mm*mmToSteps
        Pos_Step = self.CheckZero(Pos_Step)
        Error = self.CheckLimits(Stage,Pos_Step)
        if Error != None:
            return Error
        else:
            #Make the command to move the stage
            if Stage == 'X':
                absmovemm = 'E,C,IA1M' + str(Pos_Step) + ',R'
            self.sendcmd(absmovemm)
            #Now that the command has been sent to move wait for it to finish
            self.waitReady()
        
    
    def abs_move_in(self,Stage,Position_in):
        assert Stage == 'X'
        Pos_Step = Position_in*inTomm*mmToSteps
        Pos_Step = self.CheckZero(Pos_Step)
        Error = self.CheckLimits(Stage, Pos_Step)
        if Error != None:
            return Error
        else:
            #Make the command to move the stage
            if Stage == 'X':
                absmovein = 'E,C,IA1M' + str(Pos_Step) + ',R'
            self.sendcmd(absmovein)
            #Now that the command has been sent to move, wait for it to finish
            self.waitReady()
        

    def FindZero(self,Stage):
        assert Stage == 'X'
        if Stage == 'X':
            #First Send the Stage to Negative Limit
            self.sendcmd('F,C,I1M-0,R')
            self.waitReady()
            NegLimit = self.getPosition('X',step_units=True)
            #Next get the positive limit
            self.sendcmd('F,C,I1M0,R')
            self.waitReady()
            PosLimit = self.getPosition('X',step_units=True)
            #Next calculate the average between the two and go to that position
            Average = -1*(NegLimit + PosLimit)/2
            MoveCommand = 'F,C,I1M' + str(Average) + ',R'
            self.sendcmd(MoveCommand)
            self.waitReady()
            #Now Set this value as the 0
            self.sendcmd('F,C,IA1M-0,R')
            self.getPosition('X',step_units=True)           
            

    def CheckLimits(self,Stage,EndPosition):
        Error = None
        assert Stage == 'X'
        if Stage == 'X':
            if EndPosition > 24958 or EndPosition < -24958:
                Error = 'The X limit would be hit with this move'
                return Error
            else:
                return Error
    
    def __del__(self):
        self._port.close()

Xslide = VXM('COM6',9600,0.1)
Xslide.move_mm('X',-10.0)

"""
XYZ = VXM('COM3',9600,0.1)
#XYZ.home()
XYZ.getAllPositions()
#XYZ.move_mm('Z',-40)
XYZ.FindZero('Z')
XYZ.getAllPositions()
"""
