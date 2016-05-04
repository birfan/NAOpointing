"""
A sample showing how to have a NAOqi service as a Python app.
"""

__version__ = "0.0.3"

__copyright__ = "Copyright 2015, Aldebaran Robotics"
__author__ = 'ekroeger'
__email__ = 'ekroeger@aldebaran.com'


import qi

import stk.runner
import stk.events
import stk.services
import stk.logging

import time
import math
# import thread

from threading import Thread

class PointingService(object):
    "NAOqi service example (set/get on a simple value)."
    APP_ID = "com.aldebaran.PointingService"
    def __init__(self, qiapp):
        # generic activity boilerplate
        self.qiapp = qiapp
        
        self.events = stk.events.EventHelper(qiapp.session) 
        self.s = stk.services.ServiceCache(qiapp.session) 
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)
        # Internal variables
        self.level = 0
        #TODO: PUT THE FOLLOWING IN CONFIG FILE 
        self.tabletX = 20.0/100         # X coordinate of the tablet center with respect to FRAME_WORLD (in M)
        self.tabletY = 0.0/100          # Y coordinate of the tablet center with respect to FRAME_WORLD (in M)
        self.tabletZ = 0.0/100          # Z coordinate of tablet with respect to FRAME_WORLD (in M)
        self.tabletWidth = 29.21/100    # Width of tablet in M (Microsoft surface pro 4)
        self.tabletLength = 20.142/100  # Length of tablet in M (Microsoft surface pro 4)
        self.tabletResolutionX = 2736   # Tablet resolution in X
        self.tabletResolutionY = 1824   # Tablet resolution in Y
        self.robotPosition = "Top"  # robotPosition relative to the tablet. "Top" if the robot is facing the top edge of the tablet
        # "Bottom" if the robot is facing the bottom edge of the tablet, "Left" if the robot is facing the left side of the tablet,
        # "Right" if the robot is facing the right side of the tablet.
#         self.robotOffsetFromFloor = 70.0/100 # Height of the table that the robot is on (in M)
        self.frame = 2              # 0 is "FRAME_TORSO", 1 is "FRAME_WORLD", 2 is "FRAME_ROBOT"
        self.effector = "RArm"      # Could be "Arms", "LArm", "RArm"
        self.hand = "RHand"         # Could be "LHand" or "RHand" (set by the effector)
        self.useWholeBody = False   # Do not use whole body for looking at a target
        self.initArmSpeed = 0.3
        self.initHeadSpeed = 0.1
        self.timeIncrement = 0.15
        
        self.coorX = 0.01
        self.coorY = 0.0
        self.coorZ = self.tabletZ
        self.speed = 0.2
        self.sleepTime = 2.0

    @qi.bind(returnType=qi.Void, paramsType=[qi.Int8])
    @stk.logging.log_exceptions
    def set(self, level):        
        "Set level"
        
        self.s.ALTextToSpeech.say("Hello" + str(level))
        self.level = level

    @qi.bind(returnType=qi.Int8, paramsType=[])
    def get(self):
        "Get level"
        
        return self.level

    @qi.bind(returnType=qi.Void, paramsType=[])
    def reset(self):
        "Reset level to default value"
        
        return self.set(0)

    @qi.bind(returnType=qi.Void, paramsType=[])
    def stop(self):
        "Stop the service."
        
        self.logger.info("PointingService stopped by user request.")
        self.qiapp.stop()

    @qi.nobind
    def on_stop(self):
        "Cleanup (add yours if needed)"
        
        self.logger.info("PointingService finished.")
    
    def StiffnessOn(self):
        "Turn stiffness on for all joints"
        
        self.pNames = "Body"
        self.pStiffnessLists = 1.0
        self.pTimeLists = 1.0
        self.s.ALMotion.stiffnessInterpolation(self.pNames, self.pStiffnessLists, self.pTimeLists)
    
    @qi.bind(returnType=qi.Void, paramsType=[])
    @stk.logging.log_exceptions
    def StartMotion(self):
        "Start initial motion"
        
        self.StiffnessOn()
        self.s.ALRobotPosture.goToPosture("StandInit", 0.5)
        self.s.ALMotion.wbEnable(False)      
        
    @qi.bind(returnType=qi.Void, paramsType=[])
    def StartAutonomousLife(self):
        "Stop autonomous life"
        
        self.s.ALMotion.setBreathConfig([["Bpm", 6], ["Amplitude", 0.9]])
        self.s.ALMotion.setBreathEnabled("Arms", True)
        self.s.ALMotion.setBreathEnabled("Legs", True)
        self.s.ALBasicAwareness.setEngagementMode("SemiEngaged")
        self.s.ALBasicAwareness.setTrackingMode("Head")
        self.s.ALBasicAwareness.setStimulusDetectionEnabled("Sound",True)
        self.s.ALBasicAwareness.setStimulusDetectionEnabled("Movement",True)
        self.s.ALBasicAwareness.setStimulusDetectionEnabled("People",True)
        self.s.ALBasicAwareness.setStimulusDetectionEnabled("Touch",False)
        self.s.ALAutonomousLife.setState("solitary")
    
    @qi.bind(returnType=qi.Void, paramsType=[])
    def StopAutonomousLife(self):
        "Stop autonomous life"

        self.s.ALBasicAwareness.stopAwareness()
        self.s.ALAutonomousLife.setState("disabled")
        
    @qi.bind(returnType=qi.Void, paramsType=[])
    def StopAwareness(self):
        "Stop autonomous life"
        
        self.s.ALBasicAwareness.stopAwareness()
        
    @qi.bind(returnType=qi.Void, paramsType=[])
    def StartAwareness(self):
        "Stop autonomous life"
        
        self.s.ALBasicAwareness.startAwareness()
        
    @qi.bind(returnType=qi.Void, paramsType=[])
    @stk.logging.log_exceptions
    def StartLife(self):
        "Start autonomous life"
        
        self.StartAutonomousLife()
        
    @qi.bind(returnType=qi.Void, paramsType=[])
    def StopLife(self):
        "Stop autonomous life"
        
        self.StopAutonomousLife()
        self.s.ALMotion.rest() #Crouch
    
    @qi.bind(returnType=qi.Void, paramsType=[])
    def PointAtArm(self, armAngles):
        
        self.armAngles = armAngles
        self.timeNumLoop = int(round(self.sleepTime/ self.timeIncrement))

        for x in range(0, self.timeNumLoop):
            self.s.ALTracker.pointAt(self.effector, [self.coorX, self.coorY, self.coorZ], self.frame, self.speed)
            time.sleep(self.timeIncrement)
#         self.distBtwHandMidFinger = 0.012
#         self.alfa = math.atan2(math.fabs(self.coorY), self.coorX)
#         self.coorX -= math.sin(self.alfa)*self.distBtwHandMidFinger
#         self.coorY -= math.cos(self.alfa)*self.distBtwHandMidFinger #if self.effector = "RArm"
#          
#         if self.effector == "LArm":
#             self.coorY += math.cos(self.alfa)*self.distBtwHandMidFinger #if self.effector = "LArm"
         
#         print "coorX: %.2f\n" % self.coorX
#         print "coorY: %.2f\n" % self.coorY
        
        self.s.ALMotion.setAngles(self.hand, 0.01, self.initArmSpeed)
        self.s.ALMotion.setAngles(self.effector, self.armAngles, self.initArmSpeed)
        
    @qi.bind(returnType=qi.Void, paramsType=[])
    def LookAtHead(self, headAngles):
        
        self.headAngles = headAngles
        self.timeNumLoop = int(round((self.sleepTime)/ self.timeIncrement))
        for x in range(0, self.timeNumLoop):
            self.s.ALTracker.lookAt([self.coorX, self.coorY, self.coorZ], self.frame, self.speed, self.useWholeBody)
            time.sleep(self.timeIncrement)

        self.s.ALMotion.setAngles("Head", self.headAngles, self.initHeadSpeed)
        
    @qi.bind(returnType=qi.Void, paramsType=(qi.Float, qi.Float, qi.Float, qi.Float, qi.Float))
    @stk.logging.log_exceptions       
    def PointAtWorld(self, speed, coorX, coorY, coorZ, sleepTime):
        "Point at specified target in 3D"
         
        self.speed = speed     # Fraction of maximum speed
        self.coorX = coorX     # X coordinate of target wrt to FRAME_WORLD of robot
        self.coorY = coorY     # Y coordinate of target wrt to FRAME_WORLD of robot
        self.coorZ = coorZ     # Z coordinate of target wrt to FRAME_WORLD of robot
        self.sleepTime = sleepTime       

        if self.coorY > 0.0:
            self.effector = "RArm"
            self.hand = "RHand"            
        elif self.coorY < 0.0:
            self.effector = "LArm"
            self.hand = "LHand"
        #else use whichever arm is used last time
    
        self.StopAwareness()
        self.useSensors = False
        self.headAngles = self.s.ALMotion.getAngles("Head", self.useSensors)
        self.armAngles = self.s.ALMotion.getAngles(self.effector, self.useSensors)
        
        self.s.ALMotion.setAngles(self.hand, 1.0, self.initArmSpeed)
    
        headThread = Thread(target=self.LookAtHead, args=(self.headAngles, ))
        armThread = Thread(target=self.PointAtArm, args=(self.armAngles, ))

        headThread.start()
        time.sleep(0.5)
        armThread.start()
        
        headThread.join()
        armThread.join()
        time.sleep(2.0)    # Change this to the time necessary for both actions to be finished

        self.StartAwareness() 
                
    @qi.bind(returnType=qi.Void, paramsType=(qi.Float, qi.Float, qi.Float, qi.Float))
    @stk.logging.log_exceptions
    def PointAtTablet(self, speed, tabletPixelX, tabletPixelY, sleepTime):
        "Point at specified tablet Pixel X and Pixel Y"
         
        self.speed = speed     # Fraction of maximum speed
        self.tabletPixelX = tabletPixelX/self.tabletResolutionX   # Tablet pixel in X direction (width) wrt top-left corner of tablet (horizontal)
        self.tabletPixelY = tabletPixelY/self.tabletResolutionY    # Tablet pixel in Y direction (length) wrt top-left corner of tablet (vertical)
        self.sleepTime = sleepTime

        self.gamma = math.radians(180) # robot is vertical (is facing) to the tablet (rotation angle about Xtablet)
         
        # The following are for self.robotPosition == "Top":   
        self.theta =  math.radians(90) # rotation angle about Ztablet
        self.xTrans = self.tabletWidth/2 - self.tabletY # xTranslation from Xtablet to origin of robot FRAME_WORLD for self.robotPosition == "Top"
        self.yTrans = self.tabletX - self.tabletLength/2 # yTranslation from Ytablet to origin of robot FRAME_WORLD for self.robotPosition == "Top"
         
        if self.robotPosition == "Bottom":
            self.theta = math.radians(-90)
            self.yTrans = self.tabletX + self.tabletLength/2
        elif self.robotPosition == "Right":
            self.theta = math.radians(180)
            self.xTrans = self.tabletX - self.tabletWidth/2
            self.yTrans = self.tabletLength/2 - self.tabletY
        elif self.robotPosition == "Left":
            self.theta = math.radians(0)
            self.xTrans = self.tabletX + self.tabletWidth/2
            self.yTrans = self.tabletLength/2 - self.tabletY
             
        self.coorX = math.cos(self.theta)*self.tabletPixelX - math.cos(self.gamma)*math.sin(self.theta)*self.tabletPixelY + \
                    math.sin(self.gamma)*math.sin(self.theta) + self.xTrans*math.cos(self.theta) - self.yTrans*math.cos(self.gamma)*math.sin(self.theta)
        self.coorY = math.sin(self.theta)*self.tabletPixelX + math.cos(self.gamma)*math.cos(self.theta)*self.tabletPixelY + \
                    self.xTrans*math.sin(self.theta) - math.cos(self.theta)*math.sin(self.gamma) + self.yTrans*math.cos(self.gamma)*math.cos(self.theta)
        self.coorZ = self.tabletZ

        print "coorX: %.2f\n" % self.coorX
        print "coorY: %.2f\n" % self.coorY
        print "coorZ: %.2f\n" % self.coorZ
         
        self.PointAtWorld(self.speed, self.coorX, self.coorY, self.coorZ, self.sleepTime)
        
####################
# Setup and Run
####################

if __name__ == "__main__":
    stk.runner.run_service(PointingService)


