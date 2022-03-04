#This script is used to calculated the few view positions for an experiment 
#The given data will be generated from inputs in the tomography code

import math, bisect
import numpy as np

class FewView:
    def __init__(self,DegreeList,StartDeg,MaxDeg):
        #Take in the Degree List and create the cardinal directions
        #Make the final list
        self.result = []
        self.InputDeg = DegreeList
        self.InputInc = float(DegreeList[1] - DegreeList[0])
        #Check if the maximum is above 180.0
        self.HighMax = False
        if MaxDeg > 180.0:
            self.HighMax = True
            #Make the numbers over 180 negative
            self.HighMaxList = DegreeList
            for i in range(0,len(DegreeList)):
                if self.InputDeg[i] <= 180.0:
                    self.HighMaxList[i] = self.InputDeg[i]
                elif self.InputDeg[i] > 180.0:
                    #skip the value if it is 360 itself and we are going by 1s
                    if self.InputDeg[i] == 360 or self.InputDeg[i] == 360.0 and self.InputInc == 1.0:
                        del self.HighMaxList[i] #delete the 360.0 we dont need it
                    else:
                        self.HighMaxList[i] = self.InputDeg[i] - 360.0
            #Add a -180.0 if the max is 360 so everything works out. This means we will repeat -180 and 180 but thats fine
            self.Max360 = False
            if MaxDeg == 360.0 or MaxDeg == 360:
                self.HighMaxList.append(-180.0)
                self.Max360 = True
            self.InputDeg = self.HighMaxList
            #Sort them from -max to max instead
            self.InputDeg.sort()
            #find the lenght of list
            self.end = len(self.InputDeg)-1

        #If the Max is 360 have the cardinals be -180 -135 -90 -45 0 45 90 135 180
        if MaxDeg == 360.0 or MaxDeg == 360:
            self.CardinalIncrements = MaxDeg/8
            self.Cardinals = np.arange(self.InputDeg[0], (self.InputDeg[self.end]+self.CardinalIncrements), self.CardinalIncrements).tolist()
        else:
            #Chose 5 as good starting knowing we want start and end then have 3 in middle 0 45 90 135 180
            self.CardinalIncrements = MaxDeg/4     
            if self.HighMax == True:
                self.Cardinals = np.arange(self.InputDeg[0], (self.InputDeg[self.end]+self.CardinalIncrements), self.CardinalIncrements).tolist()
            else:
                self.Cardinals = np.arange(StartDeg, (MaxDeg+self.CardinalIncrements), self.CardinalIncrements).tolist()
        #print('The Cardinal Directions: {}'.format(self.Cardinals))
        whileinc = 0
        if MaxDeg == 360.0 or MaxDeg == 360:
            while len(self.result) != 9:
                if self.Cardinals[whileinc] in DegreeList:
                    self.result.append(self.Cardinals[whileinc])
                else:
                    abs_dif_func = lambda list_value: abs(list_value - self.Cardinals[whileinc]) 
                    closeVal = float(min(self.InputDeg, key=abs_dif_func))
                    self.result.append(closeVal)
                whileinc +=1
        else:
            while len(self.result) != 5:
                if self.Cardinals[whileinc] in DegreeList:
                    self.result.append(self.Cardinals[whileinc])
                else:
                    abs_dif_func = lambda list_value: abs(list_value - self.Cardinals[whileinc]) 
                    closeVal = float(min(self.InputDeg, key=abs_dif_func))
                    self.result.append(closeVal)
                whileinc +=1
        #Repeat for the decades and check again if high max 
        #Make sure the incrementer is smaller than 10
        if self.InputInc <= 10.0:   
            if self.HighMax == True:
                self.Decades = np.arange(self.InputDeg[0], (self.InputDeg[self.end]+10.0), 10.0).tolist()
            else:
                self.Decades = np.arange(StartDeg, (MaxDeg+10.0), 10.0).tolist()

            #print('The Cardinal Directions: {}'.format(self.Cardinals))
            whileinc = 0
            whileend = ((MaxDeg-StartDeg)/10.0)+1
            while len(self.result) != whileend:
                #first check that the decade number is not in the list already
                if self.Decades[whileinc] in self.result:
                    pass
                else:
                    #as long as it isnt already in the list, check if decade is in input list if it is, add it.
                    if self.Decades[whileinc] in DegreeList:
                        self.result.append(self.Decades[whileinc])
                    else:
                        #if it wasnt in the list, find the closest value to it to add
                        abs_dif_func = lambda list_value: abs(list_value - self.Decades[whileinc]) 
                        closeVal = float(min(self.InputDeg, key=abs_dif_func))
                        #Here again, only add the item to the list if it wasn't in the list previously
                        if closeVal in self.result:
                            pass
                        else:
                            self.result.append(closeVal)
                whileinc +=1

        #Do the same thing that we did for the 10s with 5s
        if self.InputInc <=5.0:
            if self.HighMax == True:
                self.Fives = np.arange(self.InputDeg[0], (self.InputDeg[self.end]+5.0), 5.0).tolist()
            else:
                self.Fives = np.arange(StartDeg, (MaxDeg+5.0),5.0).tolist()
            whileinc = 0
            whileend = ((MaxDeg-StartDeg)/5.0)+1
            while len(self.result) != whileend:
                #check that the 5s number isnt in the list alread
                if self.Fives[whileinc] in self.result:
                    pass
                else:
                    #as long as it isnt already in the list, check if 5s is in the input list if it is, add it
                    if self.Fives[whileinc] in DegreeList:
                        self.result.append(self.Fives[whileinc])
                    else:
                        #if it wasnt in the list, find the closest value to it to add
                        abs_dif_func = lambda list_value: abs(list_value - self.Fives[whileinc])
                        closeVal = float(min(self.InputDeg, key=abs_dif_func))
                        #Here again, only add the item to the list if it wasn't in the list previously
                        if closeVal in self.result:
                            pass
                        else:
                            self.result.append(closeVal)
                whileinc +=1
        print(self.result)
        #I am lazy and don't feel like changing several things  so here this is for MakeFewView
        self.MaxDegree = MaxDeg
        self.StartDegree = StartDeg
    
    def MakeFewView(self):
        #find lenght of the input list and list coming from initialize function
        """if self.Max360 == True:
            FullLength = len(self.InputDeg)"""
        MaxDeg = self.MaxDegree
        StartDeg = self.StartDegree
        DegreeList = self.InputDeg
        FullLength = len(self.InputDeg)
        StartingList = self.Cardinals
        MidList = StartingList
        print('This is the full length we are waiting for {}'.format(FullLength))
        #print('Starting Few View Creation, Full Lenght is {}'.format(FullLength))
        #Do the same thing we did with 5 but with 2s
        if self.InputInc <=2.0:
            if self.HighMax == True:
                self.Twos = np.arange(self.InputDeg[0], (self.InputDeg[self.end]+2.0), 2.0).tolist()
            else:
                self.Twos = np.arange(StartDeg, (MaxDeg+2.0),2.0).tolist()
            whileinc = 0
            whileend = ((MaxDeg-StartDeg)/2.0)+1
            while len(self.result) != whileend:
                #check that the 5s number isnt in the list alread
                if self.Twos[whileinc] in self.result:
                    pass
                else:
                    #as long as it isnt already in the list, check if 5s is in the input list if it is, add it
                    if self.Twos[whileinc] in DegreeList:
                        self.result.append(self.Twos[whileinc])
                    else:
                        #if it wasnt in the list, find the closest value to it to add
                        abs_dif_func = lambda list_value: abs(list_value - self.Twos[whileinc])
                        closeVal = float(min(self.InputDeg, key=abs_dif_func))
                        #Here again, only add the item to the list if it wasn't in the list previously
                        if closeVal in self.result:
                            pass
                        else:
                            self.result.append(closeVal)
                whileinc +=1
        
        #Do the same thing with 1s the reason I am doing this before we do the weird average thing is because I think the average thing is WRONG
        if self.InputInc <=1.0:
            if self.HighMax == True:
                self.Ones = np.arange(self.InputDeg[0], (self.InputDeg[self.end]+1.0), 1.0).tolist()
            else:
                self.Ones = np.arange(StartDeg, (MaxDeg+1.0),1.0).tolist()
            whileinc = 0
            whileend = ((MaxDeg-StartDeg)/1.0)+1
            while len(self.result) != whileend:
                #check that the 1s number isnt in the list alread
                if self.Ones[whileinc] in self.result:
                    pass
                else:
                    #as long as it isnt already in the list, check if 5s is in the input list if it is, add it
                    if self.Ones[whileinc] in DegreeList:
                        self.result.append(self.Ones[whileinc])
                    else:
                        #if it wasnt in the list, find the closest value to it to add
                        abs_dif_func = lambda list_value: abs(list_value - self.Ones[whileinc])
                        closeVal = float(min(self.InputDeg, key=abs_dif_func))
                        #Here again, only add the item to the list if it wasn't in the list previously
                        if closeVal in self.result:
                            pass
                        else:
                            self.result.append(closeVal)
                whileinc +=1
        
        if self.InputInc <=0.5:
            if self.HighMax == True:
                self.Halves = np.arange(self.InputDeg[0], (self.InputDeg[self.end]+0.5), 0.5).tolist()
            else:
                self.Halves = np.arange(StartDeg, (MaxDeg)+0.5,0.5).tolist()
            whileinc = 0
            whileend = ((MaxDeg-StartDeg)/0.5)+1
            while len(self.result) != whileend:
                #check that the halves number isnt in the list already
                if self.Halves[whileinc] in self.result:
                    pass
                else:
                    #if it wasnt in the list, find the closest value to it to add
                    abs_dif_func = lambda list_value: abs(list_value - self.Halves[whileinc])
                    closeVal = float(min(self.InputDeg, key=abs_dif_func))
                    #Here again, only add the item to the lift if it wasn't in the in the list previously
                    if closeVal in self.result:
                        pass
                    else:
                        self.result.append(closeVal)
                whileinc +=1

        if self.InputInc <=0.1:
            if self.HighMax == True:
                self.Tenths= np.arange(self.InputDeg[0], (self.InputDeg[self.end]+0.1), 0.1).tolist()
            else:
                self.Tenths = np.arange(StartDeg, (MaxDeg)+0.1,0.1).tolist()
            whileinc = 0
            whileend = ((MaxDeg-StartDeg)/0.1)+1
            while len(self.result) != whileend:
                #check that the tenths number isnt in the list already
                if self.Tenths[whileinc] in self.result:
                    pass
                else:
                    abs_dif_func = lambda list_value: abs(list_value - self.Tenths[whileinc])
                    closeVal = float(min(self.InputDeg, key=abs_dif_func))
                    if closeVal in self.result:
                        pass
                    else:
                        self.result.append(closeVal)
                whileinc +=1

        #Now clean up the rest by making a list with the incrementer in it
        if self.HighMax == True:
            self.Incs = np.arange(self.InputDeg[0], (self.InputDeg[self.end]+self.InputInc), self.InputInc).tolist()
        else:
            self.Incs = np.arange(StartDeg, (MaxDeg+self.InputInc),self.InputInc).tolist()
        whileinc = 0
        whileend = ((MaxDeg-StartDeg)/self.InputInc)+1
        while len(self.result) != whileend:
            #check that the 1s number isnt in the list alread
            if self.Incs[whileinc] in self.result:
                pass
            else:
                #as long as it isnt already in the list, check if 5s is in the input list if it is, add it
                if self.Incs[whileinc] in DegreeList:
                    self.result.append(self.Incs[whileinc])
                else:
                    #if it wasnt in the list, find the closest value to it to add
                    abs_dif_func = lambda list_value: abs(list_value - self.Incs[whileinc])
                    closeVal = float(min(self.InputDeg, key=abs_dif_func))
                    self.result.append(closeVal)
            whileinc +=1
        print('Length of List Going into Stupid List {} '.format(len(self.result)))
        while len(self.result) != FullLength:
            #Until the result list is the same size, we will iterate
            increment = 1
            StartingLength = len(StartingList)
            #Cardinals = MiddleManList
            print('Before while loop, cardinal length {}'.format(StartingLength))
            print(self.result)
            while increment < StartingLength:
                #get the average value in cardinals
                print('Values being averaged: {} and {}'.format(StartingList[increment],StartingList[increment-1]))
                print(StartingLength)
                average = (StartingList[increment]+StartingList[increment-1])/2
                #print('At top of inner while inc={}, average={}'.format(increment,average))
                #check if this value is already in the results list
                
                if average in self.result:
                    #all we do if this value is already in the results is pass
                    pass
                    #print('passing on {}'.format(average))
                else: # average not in self.result:
                    #if it isn't in there, we need to get the closest value and then add it to results
                    #finds closest value in the input list to the current average
                    abs_dif_func = lambda list_value: abs(list_value - average) 
                    closeVal = float(min(self.InputDeg, key=abs_dif_func))
                    if closeVal in self.result:
                        pass
                    else:
                        self.result.append(closeVal)
                
                increment +=1
                MidList.append(average)
            MidList.sort()
            #And then make the starting list become the midlist
            StartingList = MidList
            
        return self.result
# Below code can be uncommented to test the code
#FewViewList = np.arange(0, (360+0.5), 0.5).tolist()
#print(len(FewViewList))
#FewViewTest = FewView(FewViewList,0,360)
#print(FewViewTest)
#print(len(FewViewList))
#print('Going into MakeFewView')
#MadeList = FewViewTest.MakeFewView()
#print(MadeList)
#print('adn now i sort it')
#newlist = sorted(MadeList)
#print(newlist)
#print(len(newlist))
#print('Finished Making List it is {} long'.format(len(MadeList)))