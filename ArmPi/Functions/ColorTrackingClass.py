#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import Camera
import threading
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *
# import numpy as np

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)


class ColorTracking(): 
    
    def __init__(self):
        self.__target_color = ('red', 'green', 'blue')
        #self.__target_color = ('red')
        self.my_camera = Camera.Camera()
        self.my_camera.camera_open()
        self.range_rgb = {
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),  
}
        self.coordinate = {
        'red':   (-15 + 0.5, 12 - 0.5, 1.5),
        'green': (-15 + 0.5, 6 - 0.5,  1.5),
        'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
    }
        self.rect = None
        self.size = (640, 480)
        self.rotation_angle = 0
        self.unreachable = False
        self.world_X, self.world_Y = 0, 0
        self.world_x, self.world_y = 0, 0
        self.count = 0
        self.track = False
        self._stop = False
        self.get_roi = False
        self.center_list = []
        self.first_move = True
        self.__isRunning = False
        self.detect_color = 'None'
        self.action_finish = True
        self.start_pick_up = False
        self.start_count_t1 = True
        self.color = 0

        self.AK = ArmIK()
        self.servo1 = 500
        self.coordinate = {
        'red':   (-15 + 0.5, 12 - 0.5, 1.5),
        'green': (-15 + 0.5, 6 - 0.5,  1.5),
        'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
    }


        
        # global roi
        # global rect
        # global unreachable
        # global last_x, last_y
        # global world_X, world_Y
        # global world_x, world_y
        # global start_count_t1, t1
        # global start_pick_up, first_move
    
    def set_RGB_val(self):
        if color == "red":
            Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
            Board.RGB.show()
        elif color == "green":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
            Board.RGB.show()
        elif color == "blue":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
            Board.RGB.show()
        else:
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
            Board.RGB.show()

    def getAreaMaxContour(contours):
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None

        for c in contours:  # Go through all the contours
            contour_area_temp = math.fabs(cv2.contourArea(c))  # Calculate contour area
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 300:  # Only when the area is greater than 300, 
                    #the countour of the largest area is valid to filter out interference
                    area_max_contour = c

        return area_max_contour, contour_area_max  # Return the largest contour

   
### Perception functions -- week 2

    def find_color_block(self):
        while True:
            img = self.my_camera.frame
            if img is not None:
                frame = img.copy()
                Frame = self.process_image(frame)  ###### figure out what          
                cv2.imshow('Frame', Frame)
                key = cv2.waitKey(1)
                if key == 27:
                    break
        self.my_camera.camera_close()
        cv2.destroyAllWindows()

    def process_image(self,img):
        img_h, img_w = img.shape[:2]
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)
        color = self.color
        size = self.size
        frame_resize = cv2.resize(img, size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        #f an object is detected in a certain area, the area will be detected until there is no object.
        # if self.get_roi and self.start_pick_up:
        #     get_roi = False
            #frame_gb = getMaskROI(frame_gb, roi, size)  #################  
        
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  #Covert the image to LAB space
        self.pick_block_to_get(frame_lab) #Find the maximum contourFind the maximum contour

        if self.best_c_area > 2500:  # The maximum area has been found
            rect = cv2.minAreaRect(self.best_contour)
            self.box = np.int0(cv2.boxPoints(rect))

            roi = getROI(self.box) #get the ROI area
            get_roi = True

            img_centerx, img_centery = getCenter(rect, roi, size, square_length)  #Get the center coordinates of the wooden block
            self.world_x, self.world_y = convertCoordinate(img_centerx, img_centery, size) #Convert to real world coordinates
        #return self.world_x, self.world_y
            self.display_info (img)
            self.judgement(self.world_x,self.world_y,self.distance)
            
            #print('finished')
        return img
        
    def display_info(self,img):
        #draw box on the screen and display found color on screen 
        box = self.box
        detect_color = self.selected_color
        
        cv2.drawContours(img, [box], -1, self.range_rgb[detect_color], 2)
        cv2.putText(img, "Color: " + detect_color, (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, self.range_rgb[detect_color], 2)
        cv2.putText(img, '(' + str(self.world_x) + ',' + str(self.world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.range_rgb[detect_color], 1) #draw center point
        self.distance = math.sqrt(pow(self.world_x - last_x, 2) + pow(self.world_y - last_y, 2)) #Compare the last coordinates to determine whether to move
        self.last_x, self.last_y = self.world_x, self.world_y
    
    def pick_block_to_get (self,frame_lab ):
        self.best_contour = None
        self.best_c_area = 0
        self.selected_color = None

        for i in color_range:
            if i in self.__target_color:
                detect_color = i
                frame_mask = cv2.inRange(frame_lab, color_range[detect_color][0], color_range[detect_color][1])  # Perform bitwise operations on the original image and mask
                opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # Open operation
                closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # Closed operation
                contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  #Find the outline
                try: 
                    largestC = max(contours, key = cv2.contourArea)
                    largestArea = cv2.contourArea(largestC)
                    if largestArea > self.best_c_area:
                        self.best_contour = largestC
                        self.best_c_area = largestArea
                        self.selected_color = i
                except:
                    continue


    def judgement(self,world_x,world_y,distance):
        if distance < 0.5:
                    count += 1
                    center_list.extend((world_x, world_y))
                    if start_count_t1:
                        start_count_t1 = False
                        t1 = time.time()
                    if time.time() - t1 > 1:
                        self.rotation_angle = self.rect[2] 
                        start_count_t1 = True
                        self.world_X, self.world_Y = np.mean(np.array(center_list).reshape(count, 2), axis=0)
                        center_list = []
                        count = 0
                        self.start_pick_up = True
        else:
            t1 = time.time()
            start_count_t1 = True
            center_list = []
            count = 0 
   

### Movement functions -- week 3
    def pick_up_block(self):
        Board.setBusServoPulse(1, self.servo1 - 280, 500)  #Claws open
        print('claws open')
        # Calculate the angle the gripper needs to rotate
        servo2_angle = getAngle(self.world_X, self.world_Y, self.rotation_angle)
        print(servo2_angle)
        Board.setBusServoPulse(2, servo2_angle, 500)
        time.sleep(0.8)
        # if not __isRunning:
        #     continue
        self.AK.setPitchRangeMoving((self.world_X, self.world_Y, 2), -90, -90, 0, 1000)  #lower height
        time.sleep(2)
        # if not __isRunning:
        #     continue
        Board.setBusServoPulse(1, self.servo1, 500)  # Gripper closed
        time.sleep(1)
        # if not __isRunning:
        #     continue
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((self.world_X, self.world_Y, 12), -90, -90, 0, 1000)  # Robotic arm raised
        time.sleep(1)
    

    def find_where_block_goes (self):
        #result = self.AK.setPitchRangeMoving((self.coordinate[detect_color][0], self.coordinate[detect_color][1], 12), -90, -90, 0)
        result = self.AK.setPitchRangeMoving((self.coordinate[self.selected_color][0], self.coordinate[self.selected_color][1], 12), -90, -90, 0)   
        time.sleep(result[2]/1000)
        
        # if not __isRunning:
        #     continue
        #servo2_angle = getAngle(self.coordinate[detect_color][0], self.coordinate[detect_color][1], -90)
        servo2_angle = getAngle(self.coordinate[self.selected_color][0], self.coordinate[self.selected_color][1], -90)
        Board.setBusServoPulse(2, servo2_angle, 500)
        time.sleep(0.5)

        # if not __isRunning:
        #     continue
        #self.AK.setPitchRangeMoving((self.coordinate[detect_color][0], self.coordinate[detect_color][1], self.AKcoordinate[detect_color][2] + 3), -90, -90, 0, 500)
        self.AK.setPitchRangeMoving((self.coordinate[self.selected_color][0], self.coordinate[self.selected_color][1], self.AKcoordinate[self.selected_color][2] + 3), -90, -90, 0, 500)
        time.sleep(0.5)
        
        # if not __isRunning:
        #     continue
        #self.AK.setPitchRangeMoving((self.coordinate[detect_color]), -90, -90, 0, 1000)
        self.AK.setPitchRangeMoving((self.coordinate[self.selected_color]), -90, -90, 0, 1000)
        time.sleep(0.8)
        
        # if not __isRunning:
        #     continue
    def initMove(self):
        Board.setBusServoPulse(1, self.servo1 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)


    def put_down_block(self):
        Board.setBusServoPulse(1, self.servo1 - 200, 500)  #Open the claws and put the object down
        time.sleep(0.8)
        
        # if not __isRunning:
        #     continue                    
        #self.AK.setPitchRangeMoving((self.coordinate[detect_color][0], self.coordinate[detect_color][1], 12), -90, -90, 0, 800)
        self.AK.setPitchRangeMoving((self.coordinate[detect_color][0], self.coordinate[detect_color][1], 12), -90, -90, 0, 800)
        time.sleep(0.8)

        self.initMove()  # Return to intial position
        time.sleep(1.5)

        detect_color = 'None'
        first_move = True
        get_roi = False
        action_finish = True
        start_pick_up = False
        self.set_rgb(detect_color)
    
