#!/usr/bin/python3
# coding=utf8

import ColorTrackingClass 

ctc = ColorTrackingClass.ColorTracking()

def percetion ():
    imag = ctc.find_color_block()

    processedImg = ctc.process_image(imag)

    world_x,world_y = ctc.photo_2_realWorld(processedImg)

    ctc.display_info(processedImg)

    return processedImg
    

Frame = percetion()





