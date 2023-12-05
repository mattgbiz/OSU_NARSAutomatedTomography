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
                    self.setVelocity('Y',defaultVelocity)
                    self.setVelocity('Z',defaultVelocity)
                    self.getresp()
            else:
                initialized = True
                print('Stage did not connect, try again')
                
        

    def home(self):
        #Move all of the stages to 0 starting with Z to avoid running into things
        self.moveToZero('Z')
        time.sleep(1)
        self.moveToZero('Y')
        time.sleep(1)
        self.moveToZero('X')
        self.getAllPositions()

    def ExperimentalPositions(self,XPosition,YPosition,ZPosition,english_units=False):
        #This function sends the stage to the set experimental locations
        #if XPosition != 0 or XPosition != -0 or YPosition != 0 or YPosition !=-0 or ZPosition!=0 or ZPosition!=-0
        if english_units == True:
            XSteps = XPosition*inTomm*mmToSteps
            YSteps = YPosition*inTomm*mmToSteps
            ZSteps = ZPosition*inTomm*mmToSteps
        else:
            XSteps = XPosition*mmToSteps
            YSteps = YPosition*mmToSteps
            ZSteps = ZPosition*mmToSteps
        #Now that the steps have been found, check that we wont be passing a zero
        XSteps = self.CheckZero(XSteps)
        YSteps = self.CheckZero(YSteps)
        ZSteps = self.CheckZero(ZSteps)
        ErrorX = self.CheckLimits('X',XSteps)
        ErrorY = self.CheckLimits('Y',YSteps)
        ErrorZ = self.CheckLimits('Z',ZSteps)
        if ErrorX or ErrorY or ErrorZ != None:
            return 'One of the stages would gone beyond the limit'
        else:
            #Now send the move
            #need the move to be x direction first then y then z 
            #MoveMessage = 'F,C,(,IA3M' + str(ZSteps) + ',IA2M' + str(YSteps) + ',),IA1M' + str(XSteps) + ',R'
            #self.sendcmd(MoveMessage)
            if english_units == True:
                self.abs_move_in('X',XPosition)
                self.abs_move_in('Y',YPosition)
                self.abs_move_in('Z',ZPosition)
            else:
                self.abs_move_mm('X',XPosition)
                self.abs_move_mm('Y',YPosition)
                self.abs_move_mm('Z',ZPosition)
            
            self.waitReady()
        
    def SetupPositions(self,XPosition,YPosition,ZPosition,english_units=False):
            #This function sends the stage to the set experimental locations
            #if XPosition != 0 or XPosition != -0 or YPosition != 0 or YPosition !=-0 or ZPosition!=0 or ZPosition!=-0
            if english_units == True:
                XSteps = XPosition*inTomm*mmToSteps
                YSteps = YPosition*inTomm*mmToSteps
                ZSteps = ZPosition*inTomm*mmToSteps
            else:
                XSteps = XPosition*mmToSteps
                YSteps = YPosition*mmToSteps
                ZSteps = ZPosition*mmToSteps
            #Now that the steps have been found, check that we wont be passing a zero
            XSteps = self.CheckZero(XSteps)
            YSteps = self.CheckZero(YSteps)
            ZSteps = self.CheckZero(ZSteps)
            ErrorX = self.CheckLimits('X',XSteps)
            ErrorY = self.CheckLimits('Y',YSteps)
            ErrorZ = self.CheckLimits('Z',ZSteps)
            if ErrorX or ErrorY or ErrorZ != None:
                return 'One of the stages would gone beyond the limit'
            else:
                #Now send the move
                #need the move to be y direction first then x then z 
                #MoveMessage = 'F,C,(,IA3M' + str(ZSteps) + ',IA2M' + str(YSteps) + ',),IA1M' + str(XSteps) + ',R'
                #self.sendcmd(MoveMessage)
                if english_units == True:
                    self.abs_move_in('Y',YPosition)
                    self.abs_move_in('X',XPosition)
                    self.abs_move_in('Z',ZPosition)
                else:
                    self.abs_move_mm('Y',YPosition)
                    self.abs_move_mm('X',XPosition)
                    self.abs_move_mm('Z',ZPosition)
                
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
        assert Stage == 'X' or Stage == 'Y' or Stage == 'Z'
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
            elif Stage == 'Y':
                print('Y Position: {} steps'.format(stageNum))
            elif Stage == 'Z':
                print('Z Position: {} steps'.format(stageNum))
            return stageNum     
        if english_units == True:
            if Stage == 'X':
                print('X Position: %fin' %(stagein))
            elif Stage == 'Y':
                print('Y Position: %fin' %(stagein))
            elif Stage == 'Z':
                print('Z Position: %fin' %(stagein))
            return stagein        
        if metric_units == True:
            if Stage == 'X':
                print('X Position: %fmm' %(stagemm))
            elif Stage == 'Y':
                print('Y Position: %fmm' %(stagemm))
            elif Stage == 'Z':
                print('Z Position: %fmm' %(stagemm)) 
            return stagemm


    #Function to get the X,Y,Z positions at same time
    def getAllPositions(self, metric_units = True, english_units = False):
        self.sendcmd('X',silent=False)       #gets X position
        Xresp = str(self.getresp(silent=False))          
        self.sendcmd('Y',silent=False)       #get Y position
        Yresp = str(self.getresp(silent=False))
        self.sendcmd('Z',silent=False)       #get Z position   
        Zresp = str(self.getresp(silent=False))
        #get values from the strings
        #The first part of response is the axis, second is + or - and last 7 are the positions
        def getNumber(Axisresp):
            Axisnum = int(Axisresp[2:9])    #turns the string of 7 digits into an integer  
            if Axisresp[1] == '-':          #see if second value is + or -
                Axisnum = Axisnum*(-1)      #if negative, make it a negative value
            return Axisnum
        
        Xnum = getNumber(Xresp) #turns the string of 7 digits into an integer
        Ynum = getNumber(Yresp)
        Znum = getNumber(Zresp)
        #Conversions 1 step is 0.0050mm
        Xmm = float(stepsTomm*Xnum)           #make these values float since they were integers
        Ymm = float(stepsTomm*Ynum)
        Zmm = float(stepsTomm*Znum)
        #conversion 25.4 mm is 1 in
        Xin = Xmm/25.4
        Yin = Ymm/24.4
        Zin = Zmm/25.4
        #time.sleep(1)
        #print('Stage Positions- {} {} {}'.format(Xresp,Yresp,Zresp)) #it doesnt like this print for some reason
        #by default, metric units is true, so if we want english units to be displayed, specifcy english_units = True in the function call
        if english_units == True:
            print('Stage Positions: X=%fin Y=%fin Z=%fin' %(Xin,Yin,Zin))
            return Xin, Yin, Zin
        if metric_units == True:
            print('Stage Positions: X=%fmm Y=%fmm Z=%fmm' %(Xmm,Ymm,Zmm))
            return Xmm, Ymm, Zmm

    def setVelocity(self, Stage, Speed):
        #make sure someone is only trying to input velocity for one of the 3 axes
        assert Stage == 'X' or Stage == 'Y' or Stage == 'Z'
        assert Speed > 0 and Speed <= 6000 #the motor speed must be in range 1-6000  
        if Stage == 'X':
            Velocity = 'E,C,S1M' + str(Speed) + ',R'
            self.sendcmd(Velocity)
            print('Velocity of Stage %s set to %s' %(Stage,Speed))
        elif Stage == 'Y':
            Velocity = 'E,C,S2M' + str(Speed) + ',R'
            self.sendcmd(Velocity)
            print('Velocity of Stage %s set to %s' %(Stage,Speed))
        elif Stage == 'Z':
            Velocity = 'E,C,S3M' + str(Speed) + ',R'
            self.sendcmd(Velocity)
            print('Velocity of Stage %s set to %s' %(Stage,Speed))
        else:
            print('Did not set a speed to a stage') 
            
    def moveToZero(self,Stage):
        assert Stage == 'X' or Stage == 'Y' or Stage == 'Z'
        #make the command to move to zero
        if Stage == 'X':
            Zero = 'E,C,IA1M0,R'
        elif Stage == 'Y':
            Zero = 'E,C,IA2M0,R'
        elif Stage == 'Z':
            Zero = 'E,C,IA3M0,R'
        self.sendcmd(Zero)
        #now we have sent the command to move the stage back to zero
        #need to wait for the stage to finish getting to zero
        self.waitReady()
    
    def move_mm(self,Stage,dist_mm):
        assert Stage == 'X' or Stage == 'Y' or Stage == 'Z'
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
            elif Stage == 'Y':
                movemm = 'E,C,I2M' + str(dist_step) +',R'
            elif Stage == 'Z':
                movemm = 'E,C,I3M' + str(dist_step) +',R'
            self.sendcmd(movemm)
            #now we have sent the command to move the stage back to zero
            #need to wait for the stage to finish getting to zero
            self.waitReady()
        
    
    def move_in(self,Stage,dist_in):
        assert Stage == 'X' or Stage == 'Y' or Stage == 'Z'
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
            elif Stage == 'Y':
                movein = 'E,C,I2M' + str(dist_step) +',R'
            elif Stage == 'Z':
                movein = 'E,C,I3M' + str(dist_step) +',R'
            self.sendcmd(movein)
            #now we have sent the command to move the stage back to zero
            #need to wait for the stage to finish getting to zero
            self.waitReady()
        
    def abs_move_mm(self,Stage,Position_mm):
        assert Stage == 'X' or Stage == 'Y' or Stage == 'Z'
        Pos_Step = Position_mm*mmToSteps
        Pos_Step = self.CheckZero(Pos_Step)
        Error = self.CheckLimits(Stage,Pos_Step)
        if Error != None:
            return Error
        else:
            #Make the command to move the stage
            if Stage == 'X':
                absmovemm = 'E,C,IA1M' + str(Pos_Step) + ',R'
            elif Stage == 'Y':
                absmovemm = 'E,C,IA2M' + str(Pos_Step) + ',R'
            elif Stage == 'Z':
                absmovemm = 'E,C,IA3M' + str(Pos_Step) + ',R'
            self.sendcmd(absmovemm)
            #Now that the command has been sent to move wait for it to finish
            self.waitReady()
        
    
    def abs_move_in(self,Stage,Position_in):
        assert Stage == 'X' or Stage == 'Y' or Stage == 'Z'
        Pos_Step = Position_in*inTomm*mmToSteps
        Pos_Step = self.CheckZero(Pos_Step)
        Error = self.CheckLimits(Stage, Pos_Step)
        if Error != None:
            return Error
        else:
            #Make the command to move the stage
            if Stage == 'X':
                absmovein = 'E,C,IA1M' + str(Pos_Step) + ',R'
            elif Stage == 'Y':
                absmovein = 'E,C,IA2M' + str(Pos_Step) + ',R'
            elif Stage == 'Z':
                absmovein = 'E,C,IA3M' + str(Pos_Step) + ',R'
            self.sendcmd(absmovein)
            #Now that the command has been sent to move, wait for it to finish
            self.waitReady()
        

    def FindZero(self,Stage):
        assert Stage == 'X' or Stage == 'Y' or Stage == 'Z'
        if Stage == 'X':
            #First Send the Stage to Negative Limit
            self.sendcmd('F,C,I1M-0,R')
            self.waitReady()
            #set this as the zero as we want zero to be neg limit
            self.sendcmd('F,C,IA1M-0,R')
            self.waitReady()
            NegLimit = self.getPosition('X',step_units=True)
            #Next get the positive limit
            self.sendcmd('F,C,I1M0,R')
            self.waitReady()
            #Calculate the limits we now have an display this
            PosLimit = self.getPosition('X',step_units=True)
            PosLimitmm = self.getPosition('X')
            PosLimitin = self.getPosition('X', english_units=True)
            print('X stage limit 0 to {}steps {}mm {}in'.format(PosLimit,PosLimitmm,PosLimitin))
            self.waitReady()
            #Now Go back to Zero
            self.moveToZero('X')
            self.getPosition('X',step_units=True)
        elif Stage == 'Y':
            #First send X stage to Positive limit to ensure we don't hit rotation stage if attached
            self.sendcmd('F,C,I1M0,R')
            self.waitReady()
            #First Send the Stage to Positive Limit
            self.sendcmd('F,C,I2M0,R')
            self.waitReady()
            #Now Set this value as the 0
            self.sendcmd('F,C,IA2M-0,R')
            PosLimit = self.getPosition('Y',step_units=True)
            #Next get the negative limit
            self.sendcmd('F,C,I2M-0,R')
            self.waitReady()
            #get these limits and display to screen
            NegLimit = self.getPosition('Y',step_units=True)
            NegLimitmm = self.getPosition('Y')
            NegLimitin = self.getPosition('Y', english_units=True)
            print('Y stage limit 0 to {}steps {}mm {}in'.format(NegLimit,NegLimitmm,NegLimitin))
            self.waitReady()
            #Now go back to zero
            self.moveToZero('Y')
            self.getPosition('Y',step_units=True)
            #Send the x stage to zero as well
            self.moveToZero('X')
            self.getPosition('X')
        elif Stage == 'Z':
            #First first send the x stage to positive limit so we don't hit things
            self.sendcmd('F,C,I1M0,R')
            self.waitReady()
            #First Send the Stage to the Positive Limit
            self.sendcmd('F,C,I3M0,R')
            self.waitReady()
            #Now set this vale as the 0 point
            self.sendcmd('F,C,IA3M-0,R')
            self.waitReady()
            PosLimit = self.getPosition('Z',step_units=True)

            #Next send the stage to the negative limit
            self.sendcmd('F,C,I3M-0,R')
            self.waitReady()
            NegLimit = self.getPosition('Z',step_units=True)
            NegLimitmm = self.getPosition('Z')
            NegLimitin = self.getPosition('Z',english_units=True)
            print('Z stage limit 0 to {}steps {} mm {} in'.format(NegLimit,NegLimitmm, NegLimitin))
            #Next Move the stage back to zero
            self.moveToZero('Z')
            self.getPosition('Z',step_units=True)
            #Next move X back to zero
            self.moveToZero('X')
            self.getPosition('X')

    """This is the original find zero when things were centered def FindZero(self,Stage):
        assert Stage == 'X' or Stage == 'Y' or Stage == 'Z'
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
            Average = -1*(PosLimit-NegLimit)/2
            MoveCommand = 'F,C,I1M' + str(Average) + ',R'
            self.sendcmd(MoveCommand)
            self.waitReady()
            #Now Set this value as the 0
            self.sendcmd('F,C,IA1M-0,R')
            self.getPosition('X',step_units=True)
        elif Stage == 'Y':
            #First Send the Stage to Negative Limit
            self.sendcmd('F,C,I2M-0,R')
            self.waitReady()
            NegLimit = self.getPosition('Y',step_units=True)
            #Next get the positive limit
            self.sendcmd('F,C,I2M0,R')
            self.waitReady()
            PosLimit = self.getPosition('Y',step_units=True)
            #Next calculate the average between the two and go to that position
            Average = -1*(PosLimit-NegLimit)/2
            MoveCommand = 'F,C,I2M' + str(Average) + ',R'
            self.sendcmd(MoveCommand)
            self.waitReady()
            #Now Set this value as the 0
            self.sendcmd('F,C,IA2M-0,R')
            self.getPosition('Y',step_units=True)
        elif Stage == 'Z':
            #First Send the Stage to the Negative Limit
            self.sendcmd('F,C,I3M-0,R')
            self.waitReady()
            NegLimit = self.getPosition('Z',step_units=True)
            NegLimitmm = self.getPosition('Z')
            print('Negative limit {} mm and {} steps'.format(NegLimitmm, NegLimit))
            #Next Move the Stage Down some amount to get close to damper
            self.waitReady()
            #self.move_mm('Z',110.0)
            #self.sendcmd('F,C,I3M44000,R')
            #we no longer will be hitting the damper, so make the stage move to positive limit
            self.sendcmd('F,C,I3M0,R')
            self.waitReady()
            PosLimit = self.getPosition('Z',step_units=True)
            PosLimitmm = self.getPosition('Z')
            print('Positive limit {} mm and {} steps'.format(PosLimitmm,PosLimit))
            #Next acl the average
            Average = -1*(PosLimit-NegLimit)/2
            print(Average)
            #time.sleep(30)
            MoveCommand = 'F,C,I3M' + str(Average) + ',R'
            #print(MoveCommand)
            #time.sleep(30)
            self.sendcmd(MoveCommand)
            self.waitReady()
            #Now set this vale as the 0 point
            self.sendcmd('F,C,IA3M-0,R')
            self.getPosition('Z',step_units=True)"""

    def CheckLimits(self,Stage,EndPosition):
        Error = None
        assert Stage == 'X' or Stage == 'Y' or Stage == 'Z'
        if Stage == 'X':
            #if the Y stage is between -6800 and 0 steps then we are good for full X range
            YLimitedCheck = self.getPosition('Y', step_units=True)
            if YLimitedCheck >= -6800:
                if EndPosition > 50540 or EndPosition < 0:
                    Error = 'The X limit would be hit with this move'
                    return Error
                else:
                    #Error here is nothing so the check is passed
                    return Error
            else:
                #otherwise the stage is limited by the box itself.
                if EndPosition > 50540 or EndPosition < 31000:
                    Error = 'The X Stage would run into the box'
                    return Error
                else:
                    #Error here is nothing so the check is passed
                    return Error

        elif Stage == 'Y':
            #If the X stage is more than 34000 steps, then we are good for full Y range
            XLimitedCheck = self.getPosition('X', step_units=True)
            if XLimitedCheck >= 24000: #we have to be careful I switched this for MTF test
                if EndPosition > 0 or EndPosition < -50946:
                    Error = 'The Y limit would be hit with this move'
                    return Error
                else:
                    return Error
            else:
                #X is not far enough forward so Y cannot move very far
                if EndPosition >0 or EndPosition < -6800:
                    Error = 'The Y move would cause stage to hit the box'
                    return Error
                else:
                    return Error
        elif Stage == 'Z':
            #limit was -50935 (-127.3375mm) before but I need to force it to not be able to hit the rotation stage
            if EndPosition > 0 or EndPosition < -36000:
                Error = 'The Z limit would be hit with this move'
                return Error
            else:
                return Error
    
    def __del__(self):
        self._port.close()


#Zlimit not restricted
#Zlimit = 22050
#Zlimit if restricted
#Zlimit = (44.28/0.0025)
#XYZ = VXM('COM5',9600,0.1)
#XYZ.home()
#XYZ.getAllPositions()
#XYZ.move_mm('Z',33.4)
#XYZ.move_mm('Z',-40)
#XYZ.FindZero('Z')
#XYZ.getAllPositions()

