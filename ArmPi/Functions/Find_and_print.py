#!/usr/bin/python3
# coding=utf8

import ColorTrackingClass 
import Perception_Class

ctc = ColorTrackingClass.ColorTracking()
#ctc =Perception_Class.ColorTracking()
imag = ctc.find_color_block()

ctc.display_info(imag)
    

### movement 

ctc.pick_up_block()
    





