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

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)


class ColorTracking(): 
    
    def __init__(self):
        __target_color = ('red', 'green', 'blue')
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

    AK = ArmIK()
    global roi
    global rect
    global count
    global track
    global get_roi
    global center_list
    global __isRunning
    global unreachable
    global detect_color
    global action_finish
    global rotation_angle
    global last_x, last_y
    global world_X, world_Y
    global world_x, world_y
    global start_count_t1, t1
    global start_pick_up, first_move

    rect = None
    size = (640, 480)
    rotation_angle = 0
    unreachable = False
    world_X, world_Y = 0, 0
    world_x, world_y = 0, 0
    count = 0
    track = False
    _stop = False
    get_roi = False
    center_list = []
    first_move = True
    __isRunning = False
    detect_color = 'None'
    action_finish = True
    start_pick_up = False
    start_count_t1 = True

   
    
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

    def reset():
        global count
        global track
        global _stop
        global get_roi
        global first_move
        global center_list
        global __isRunning
        global detect_color
        global action_finish
        global start_pick_up
        global __target_color
        global start_count_t1
    
        
        count = 0
        _stop = False
        track = False
        get_roi = False
        center_list = []
        first_move = True
        __target_color = ()
        detect_color = 'None'
        action_finish = True
        start_pick_up = False
        start_count_t1 = True


# ### Motion functions -- week 3
#     def move_arm (self):
#         pass

#     def check_if_successful(self):
#         pass
    
#     def check_if_block_moved(self):
#         pass

    def open_claw(self):
        Board.setBusServoPulse(1, servo1 - 280, 500)  #Claws open
        # Calculate the angle the gripper needs to rotate
        servo2_angle = getAngle(world_X, world_Y, rotation_angle)
        Board.setBusServoPulse(2, servo2_angle, 500)
        time.sleep(0.8)

    def close_claw(self):
        Board.setBusServoPulse(1, servo1, 500)  # Gripper closed
        time.sleep(1)

#     def move_arm_up(self):
        Board.setBusServoPulse(2, 500, 500)
        AK.setPitchRangeMoving((world_X, world_Y, 12), -90, -90, 0, 1000)  # Robotic arm raised
        time.sleep(1)

    def block_placement(self):
        coordinate = self.coordinate
        result = AK.setPitchRangeMoving((coordinate[detect_color][0], coordinate[detect_color][1], 12), -90, -90, 0)   
        time.sleep(result[2]/1000)
        
        # if not __isRunning:
        #     continue
        servo2_angle = getAngle(coordinate[detect_color][0], coordinate[detect_color][1], -90)
        Board.setBusServoPulse(2, servo2_angle, 500)
        time.sleep(0.5)

        # if not __isRunning:
        #     continue
        AK.setPitchRangeMoving((coordinate[detect_color][0], coordinate[detect_color][1], coordinate[detect_color][2] + 3), -90, -90, 0, 500)
        time.sleep(0.5)
        
        # if not __isRunning:
        #     continue
        AK.setPitchRangeMoving((coordinate[detect_color]), -90, -90, 0, 1000)
        time.sleep(0.8)

    def home(self): 
        Board.setBusServoPulse(1, servo1 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

        time.sleep(1.5)

        detect_color = 'None'
        first_move = True
        get_roi = False
        action_finish = True
        start_pick_up = False
        #set_rgb(detect_color)

### Perception functions -- week 2

    def find_color_block(self,):
        while True:
            img = self.my_camera.frame
            if img is not None:
                frame = img.copy()
                Frame = run(frame)  ###### figure out what          
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

        return img

    def photo_2_realWorld(self,img,color,size):
        frame_resize = cv2.resize(img, size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        #f an object is detected in a certain area, the area will be detected until there is no object.
        if get_roi and start_pick_up:
            get_roi = False
            frame_gb = getMaskROI(frame_gb, roi, size)    
        
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  #Covert the image to LAB space
        
        area_max = 0
        areaMaxContour = 0
       
        detect_color = color
        frame_mask = cv2.inRange(frame_lab, color_range[detect_color][0], color_range[detect_color][1])  # Perform bitwise operations on the original image and mask
        opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # Open operation
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # Closed operation
        contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  #Find the outline
        areaMaxContour, area_max = self.getAreaMaxContour(contours)  #Find the maximum contour
        if area_max > 2500:  # The maximum area has been found
            rect = cv2.minAreaRect(areaMaxContour)
            self.box = np.int0(cv2.boxPoints(rect))

            roi = getROI(self.box) #get the ROI area
            get_roi = True

            img_centerx, img_centery = getCenter(rect, roi, size, square_length)  #Get the center coordinates of the wooden block
            world_x, world_y = convertCoordinate(img_centerx, img_centery, size) #Convert to real world coordinates
        return world_x, world_y

    def select 

    def draw_box(self,img):
        box = self.box
        cv2.drawContours(img, [box], -1, self.range_rgb[detect_color], 2)
        
    def display_info(self,img):
        box = self.box
        cv2.putText(img, '(' + str(world_x) + ',' + str(world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.range_rgb[detect_color], 1) #draw center point
        #distance = math.sqrt(pow(world_x - last_x, 2) + pow(world_y - last_y, 2)) #Compare the last coordinates to determine whether to move
        #last_x, last_y = world_x, world_y

   
