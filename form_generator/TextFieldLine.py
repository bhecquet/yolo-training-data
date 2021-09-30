'''
Created on 30 sept. 2021

@author: S047432
'''
from form_generator.Box import Box
from form_generator.tools import get_class_id

class TextFieldLine:
    
    def __init__(self, width, height, border_color, label_outside, label_outside_color, label_inside, font, label_outside_width=None):
        """
        :param font_size: between 0 and 1. percentage of the field height
        :param label_outside_width: width of the label zone in pixels. If not given, label_size will be the size of the label
        """
        
        self.width = width
        self.height = height
        self.border_color = border_color
        self.label_outside = label_outside
        self.label_outside_color = label_outside_color
        self.label_inside = label_inside
        self.font = font
        self.label_outside_width = label_outside_width

        
    def draw(self, x, y, img, image_draw):
        """
        :param x: the x position of the element
        :param y: the y position of the element
        :param img: The image element we are drawing on
        :param image_draw: the PIL ImageDraw object
        """
        # compute size of the field
        label_width, label_height = image_draw.textsize(self.label_outside, self.font)
        if self.label_outside_width is None:
            self.label_outside_width = label_width
            
        self.overall_width = self.label_outside_width + 20 + self.width
        self.overall_height = self.height
    
        field_x = x + self.label_outside_width + 20

        image_draw.line([(field_x, y + self.height), (field_x + self.width, y + self.height)], fill=self.border_color, width=2)
  
        if self.label_outside:
            image_draw.text((x, y + (self.height - label_height) / 2), self.label_outside, font=self.font, fill=self.label_outside_color)
           
        if self.label_inside:
            image_draw.text((field_x + 5, y + (self.height - label_height) / 2), self.label_inside, font=self.font, fill=(150, 150, 150))

        return [Box(get_class_id('field_line'), field_x, y, self.width, self.height + 1), 
                Box(get_class_id('field_line_with_label'), x - 1, y - 1, self.overall_width + 2, self.overall_height + 3)]
    
    def get_width(self):
        return self.overall_width