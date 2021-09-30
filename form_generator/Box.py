'''
Created on 30 sept. 2021

@author: S047432
'''
DEBUG = False

class Box:
    
    def __init__(self, class_id, x, y, w, h):
        self.class_id = class_id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        
    def debug(self, image_draw):
        if (DEBUG):
            color = (255, 0, 0)
            image_draw.line([(self.x, self.y), (self.x + self.w, self.y)], fill=color) # top line
            image_draw.line([(self.x + self.w, self.y), (self.x + self.w, self.y + self.h)], fill=color) # right line
            image_draw.line([(self.x, self.y + self.h), (self.x + self.w, self.y + self.h)], fill=color) # bottom line
            image_draw.line([(self.x, self.y), (self.x, self.y + self.h)], fill=color) # left line
