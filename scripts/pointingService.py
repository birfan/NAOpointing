#!/usr/local/bin/python
"""
/*******************************************************************************
*   Copyright (c) 2016-present, Bahar Irfan. All rights reserved.              *
*                                                                              *
*   This file is the pointing service for NAO robot to point at Chilitags or a *
*   world or tablet coordinate.                                                *
*                                                                              *
*   Please cite the following work if using this work:                         *
*                                                                              *
*     Robust Pointing with NAO Robot. B. Irfan. University of Plymouth, UK.    *
*     https://github.com/birfan/NAOpointing. 2016.                             *
*                                                                              *
*     Chilitags for NAO Robot. B. Irfan and S. Lemaignan. University of        *
*     Plymouth, UK. https://github.com/birfan/chilitags. 2016.                 *
*                                                                              *
*     Chilitags 2: Robust Fiducial Markers for Augmented Reality. Q. Bonnard,  *
*     S. Lemaignan, G.  Zufferey, A. Mazzei, S. Cuendet, N. Li, P. Dillenbourg.*
*     CHILI, EPFL, Switzerland. http://chili.epfl.ch/software. 2013.           *
*                                                                              *
*   Chilitags is free software: you can redistribute it and/or modify          *
*   it under the terms of the Lesser GNU General Public License as             *
*   published by the Free Software Foundation, either version 3 of the         *
*   License, or (at your option) any later version.                            *
*                                                                              *
*   Chilitags is distributed in the hope that it will be useful,               *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of             *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              *
*   GNU Lesser General Public License for more details.                        *
*                                                                              *
*   PointingService is released under GNU Lesser General Public License v3.0   *
*   (LGPL3) in accordance with Chilitags (Bonnard et al., 2013). You should    *
*   have received a copy of the GNU Lesser General Public License along with   *
*   Chilitags.  If not, see <http://www.gnu.org/licenses/>.                    *
*******************************************************************************/
"""

__version__ = '0.0.1'

__copyright__ = 'Copyright (c) 2016-present, Bahar Irfan. All rights reserved.'
__author__ = 'Bahar Irfan'
__email__ = 'bahar.irfan@plymouth.ac.uk'


import qi

import stk.runner
import stk.events
import stk.services
import stk.logging

import time
import math

import numpy as np
# import thread

from threading import Thread

class PointingService(object):
    "NAOqi service."
    APP_ID = "com.aldebaran.PointingService"
    def __init__(self, qiapp):
        # generic activity boilerplate
        self.qiapp = qiapp
        
        self.events = stk.events.EventHelper(qiapp.session) 
        self.s = stk.services.ServiceCache(qiapp.session) 
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)
        
        self.tabletWidth = 29.21/100    # Width of tablet in M in X (Microsoft surface pro 4)
        self.tabletLength = 20.142/100  # Length of tablet in M in Y (Microsoft surface pro 4)
        self.tabletResolutionX = 2736   # Tablet resolution in X
        self.tabletResolutionY = 1824   # Tablet resolution in Y
        
        self.frame = 0              # 0 is "FRAME_TORSO", 1 is "FRAME_WORLD", 2 is "FRAME_ROBOT"
        self.effector = "RArm"      # Could be "Arms", "LArm", "RArm"
        self.hand = "RHand"         # Could be "LHand" or "RHand" (set by the effector)
        self.useWholeBody = False   # Do not use whole body for looking at a target
        self.initArmSpeed = 0.3
        self.initHeadSpeed = 0.1
        self.timeIncrement = 0.15
        
        self.coorX = 0.01
        self.coorY = 0.0
        self.coorZ = 0.0
        self.speed = 0.2
        self.sleepTime = 2.0
        self.staySpeed = 1.0
        
        self.cameraName = "CameraBottom"

        self.isLocalized = False
        self.localizationTag = 8
        self.fixedFrame = 0
        
    @qi.bind(returnType=qi.Void, paramsType=[])
    def stop(self):
        "Stop the service."
        
        self.logger.info("PointingService stopped by user request.")
        self.unsubscribeCamera()
        self.qiapp.stop()

    @qi.nobind
    def on_stop(self):
        "Cleanup (add yours if needed)"
        
        self.logger.info("PointingService finished.")
    
    def stiffnessOn(self):
        "Turn stiffness on for all joints"
        
        self.pNames = "Body"
        self.pStiffnessLists = 1.0
        self.pTimeLists = 1.0
        self.s.ALMotion.stiffnessInterpolation(self.pNames, self.pStiffnessLists, self.pTimeLists)
        
    def stiffnessOff(self):
        "Turn stiffness off for all joints and go to crouch position"
        
        self.s.ALMotion.rest() #Crouch
    
    @qi.bind(returnType=qi.Void, paramsType=[])
    @stk.logging.log_exceptions
    def startMotion(self):
        "Start initial motion"
        
        self.stiffnessOn()
        self.s.ALRobotPosture.goToPosture("StandInit", 0.5)
        self.s.ALMotion.wbEnable(False)      
        
    @qi.bind(returnType=qi.Void, paramsType=[])
    def startAutonomousLife(self):
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
    def stopAutonomousLife(self):
        "Stop autonomous life"

        self.s.ALBasicAwareness.stopAwareness()
        self.s.ALAutonomousLife.setState("disabled")
        
    @qi.bind(returnType=qi.Void, paramsType=[])
    def stopAwareness(self):
        "Stop autonomous life"
        
        self.s.ALBasicAwareness.stopAwareness()
        
    @qi.bind(returnType=qi.Void, paramsType=[])
    def startAwareness(self):
        "Stop autonomous life"
        
        self.s.ALBasicAwareness.startAwareness()
        
    @qi.bind(returnType=qi.Void, paramsType=[])
    @stk.logging.log_exceptions
    def startLife(self):
        "Start autonomous life"
        
        self.startAutonomousLife()
        
    @qi.bind(returnType=qi.Void, paramsType=[])
    def stopLife(self):
        "Stop autonomous life"
        
        self.stopAutonomousLife()
        self.s.ALMotion.rest() #Crouch
                 
    @qi.bind(returnType=qi.Void, paramsType=[qi.Int16])
    def subscribeCamera(self, camIndex):
        "Subscribes the given camera (0 for top, 1 for bottom)"
                
        self.s.ChilitagsModule.setCameraResolution640x480() # comment this line to set the camera resolution to default (320x240)

        self.s.ChilitagsModule.subscribeCameraLocal(camIndex)
        
        if camIndex == 0:
            self.cameraName = "CameraTop"
        else:
            self.cameraName = "CameraBottom"
    
    @qi.bind(returnType=qi.Void, paramsType=[])
    def resetTagSettings(self):
        "Reset tag settings: tag size is 30 mm and no configuration file is used"
        
        self.s.ChilitagsModule.resetTagSettings()
    
    @qi.bind(returnType=qi.Void, paramsType=[qi.Float])
    def setDefaultTagSize(self, tagSize):
        "Set the default tag size (in mm) for Chilitags. Default is 30 mm. Call this method (if you need to) before calling estimate functions."
        
        self.s.ChilitagsModule.setDefaultTagSize(tagSize)
        
    @qi.bind(returnType=qi.Void, paramsType=[qi.Int16])
    def setLocalizationTag(self, localizationTag):
        "Set the localization tag number. Default is 8"
        
        self.localizationTag = localizationTag
        
    @qi.bind(returnType=qi.Void, paramsType=[qi.String])
    def readTagConfiguration(self, configFile):
        "Read the configuration of Chilitags from a YAML file. See 'tag_configuration_sample.yml' for an example."
        
        self.s.ChilitagsModule.readTagConfiguration(configFile)

    @qi.bind(returnType=qi.Void, paramsType=[qi.Float, qi.Float, qi.Float, qi.Float])
    def setTabletResolutionSize(self, resX, resY, tabletWidth, tabletLength):
        "Set the tablet resolution: number of pixels in X (width), number of pixels in Y (length), tablet width (in metre), tablet length (in metre)."
        
        self.tabletResolutionX = resX;
        self.tabletResolutionY = resY;
        self.tabletWidth = tabletWidth;
        self.tabletLength = tabletLength;
        
    @qi.bind(returnType=qi.Void, paramsType=[])
    def unsubscribeCamera(self):
        "Unsubscribes the camera (necessary before subscribing again)"
        
        self.s.ChilitagsModule.unsubscribeCamera()
        
    @qi.bind(returnType=qi.Void, paramsType=(qi.Float, qi.Float, qi.Int16))
    def detectChilitags(self, tabletX, tabletY, tagNumber):
        "Detect chilitags, and create transformations"

        givenTag = self.s.ChilitagsModule.estimatePosGivenTag(str(tagNumber)) # estimate the position of a given tag
        givenTag[0].pop(0) #remove tag name
        givenTagNp = np.array(givenTag)
    
        self.transformChilitagsOptical= np.reshape(givenTagNp, (-1, 4))
        
        # transformation matrix from optical to camera (from URDF file of NAO)
        self.transformOpticalCamera = np.array([[0,0,1,0],[-1,0,0,0],[0,-1,0,0],[0,0,0,1]])

        self.transformChilitagsCamera = np.dot(self.transformOpticalCamera,self.transformChilitagsOptical)
                  
        self.transformTabletChilitags = np.array([[1, 0, 0, -1*tabletX], [0, 1, 0, -1*tabletY], [0, 0, 1, 0], [0, 0, 0, 1]])
          
        self.transformTabletCamera = np.dot(self.transformChilitagsCamera, self.transformTabletChilitags)
        
    @qi.bind(returnType=qi.Void, paramsType=(qi.Float, qi.Float))
    def transformPixelToRobotCoor(self, tabletX, tabletY, targetFrame):
        "Transform tablet pixel to robot coordinates"

        useSensorValues  = True
        result = np.asarray(self.s.ALMotion.getTransform(self.cameraName, targetFrame, useSensorValues))
        self.transformCameraRobot = np.reshape(result, (-1, 4)) # 1D numpy array to 2D numpy array
            
        self.transformTabletRobot = np.dot(self.transformCameraRobot, self.transformTabletCamera)
        
        self.tabletPosX = self.transformTabletRobot[0][3]
        self.tabletPosY = self.transformTabletRobot[1][3]
        self.tabletPosZ = self.transformTabletRobot[2][3]
        
        coor = np.dot(self.transformTabletRobot, np.array([tabletX, tabletY,0,1]))

        self.coorX= float(coor[0])
        self.coorY = float(coor[1])
        self.coorZ = float(coor[2])
        
    @qi.bind(returnType=qi.Void, paramsType=[])
    def pointAtArm(self, armAngles):
        "Point at a coordinate with robot (position robot arm towards that direction)"
        
        self.armAngles = armAngles
        self.timeNumLoop = int(round(self.sleepTime/ self.timeIncrement))

        self.s.ALTracker.pointAt(self.effector, [self.coorX, self.coorY, self.coorZ], self.frame, self.speed)
        
        for x in range(0, self.timeNumLoop):
            self.s.ALTracker.pointAt(self.effector, [self.coorX, self.coorY, self.coorZ], self.frame, self.staySpeed)
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
    def lookAtHead(self, headAngles):
        "Look at a coordinate with robot (turn head towards that direction)"

        self.headAngles = headAngles
        self.timeNumLoop = int(round((self.sleepTime)/ self.timeIncrement))
        
        self.s.ALTracker.lookAt([self.coorX, self.coorY, self.coorZ], self.frame, self.speed, self.useWholeBody)
        
        for x in range(0, self.timeNumLoop):
            self.s.ALTracker.lookAt([self.coorX, self.coorY, self.coorZ], self.frame, self.staySpeed, self.useWholeBody)
            time.sleep(self.timeIncrement)

        self.s.ALMotion.setAngles("Head", self.headAngles, self.initHeadSpeed)
        
    @qi.bind(returnType=qi.Void, paramsType=(qi.Float, qi.Float, qi.Float, qi.Float, qi.Float, qi.Int16))
    @stk.logging.log_exceptions       
    def pointAtWorld(self, coorX, coorY, coorZ, speed, sleepTime, frame):
        "Point at specified target in 3D with a given arm speed, duration of pointing, and frame for robot"
         
        self.speed = speed     # Fraction of maximum speed
        self.sleepTime = 2*sleepTime/3 
        if frame == 3:         # frame 3 is "FRAME_TABLET"
            if self.isLocalized == False:
                print "Localization by a Chilitag on the tablet is necessary. Run localize method first."
            else:
                coor = np.dot(self.transformTabletRobot, np.array([coorX, coorY, 0, 1]))
                self.coorX= float(coor[0])
                self.coorY = float(coor[1])
                self.coorZ = float(coor[2])
                self.frame = self.fixedFrame
        else:
            self.coorX = coorX     # X coordinate of target wrt to frame of robot
            self.coorY = coorY     # Y coordinate of target wrt to frame of robot
            self.coorZ = coorZ     # Z coordinate of target wrt to frame of robot     
            self.frame = frame     # 0 is "FRAME_TORSO", 1 is "FRAME_WORLD", 2 is "FRAME_ROBOT"
            
        if self.coorY > 0.0:
            self.effector = "RArm"
            self.hand = "RHand"            
        elif self.coorY < 0.0:
            self.effector = "LArm"
            self.hand = "LHand"
        #else use whichever arm is used last time
    
#         self.stopAwareness()

        self.useSensors = False
        self.headAngles = self.s.ALMotion.getAngles("Head", self.useSensors)
        self.armAngles = self.s.ALMotion.getAngles(self.effector, self.useSensors)
        
        self.s.ALMotion.setAngles(self.hand, 1.0, self.initArmSpeed)
    
        headThread = Thread(target=self.lookAtHead, args=(self.headAngles, ))
        armThread = Thread(target=self.pointAtArm, args=(self.armAngles, ))

        headThread.start()
        time.sleep(0.5)
        armThread.start()
        
        headThread.join()
        armThread.join()
        time.sleep(2.0)    # Change this to the time necessary for both actions to be finished

#         self.startAwareness() 
                   
    @qi.bind(returnType=qi.Void, paramsType=(qi.Float, qi.Float, qi.Float, qi.Float))
    @stk.logging.log_exceptions
    def pointAtTablet(self, tabletPixelX, tabletPixelY, speed, sleepTime):
        "Point at specified tablet Pixel X and Pixel Y with a given arm speed and duration of pointing"
         
        self.speed = speed     # Fraction of maximum speed
        self.tabletX = (tabletPixelX/self.tabletResolutionX)*self.tabletWidth   # Tablet pixel in X direction (width) wrt top-left corner of tablet (horizontal)
        self.tabletY = (tabletPixelY/self.tabletResolutionY)*self.tabletLength    # Tablet pixel in Y direction (length) wrt top-left corner of tablet (vertical)
        self.sleepTime = sleepTime
        
        if self.isLocalized == False:
            self.localize(tabletPixelX, tabletPixelY)
        else:
            coor = np.dot(self.transformTabletRobot, np.array([self.tabletX, self.tabletY, 0, 1]))
            self.coorX= float(coor[0])
            self.coorY = float(coor[1])
            self.coorZ = float(coor[2])

        self.pointAtWorld(self.coorX, self.coorY, self.coorZ, self.speed, self.sleepTime, self.fixedFrame)

    @qi.bind(returnType=qi.Void, paramsType=(qi.Float, qi.Float))
    @stk.logging.log_exceptions
    def localize(self, tabletPixelX, tabletPixelY):
        "Localize wrt tablet coordinates and chilitags"
        
        self.isLocalized = False
        
        self.tabletX = (tabletPixelX/self.tabletResolutionX)*self.tabletWidth   # Tablet pixel in X direction (width) wrt top-left corner of tablet (horizontal)
        self.tabletY = (tabletPixelY/self.tabletResolutionY)*self.tabletLength    # Tablet pixel in Y direction (length) wrt top-left corner of tablet (vertical)
        
        self.detectChilitags(self.tabletX, self.tabletY, self.localizationTag)
        self.transformPixelToRobotCoor(self.tabletX, self.tabletY, self.fixedFrame)
        
        self.isLocalized = True
        
    @qi.bind(returnType=qi.Void, paramsType=(qi.Int16, qi.Float, qi.Float))
    @stk.logging.log_exceptions
    def pointAtTag(self, tagName, speed, sleepTime):
        "Point at specified tag with a given arm speed and duration of pointing"
        self.speed = speed     # Fraction of maximum speed 
        self.sleepTime = sleepTime
        self.detectChilitags(0, 0, tagName)
        self.transformPixelToRobotCoor(0, 0, self.fixedFrame)

        self.pointAtWorld(self.coorX, self.coorY, self.coorZ, self.speed, self.sleepTime, self.fixedFrame)
        
####################
# Setup and Run
####################

if __name__ == "__main__":
    stk.runner.run_service(PointingService)


