'''
Created on 30 sept. 2021

@author: S047432
'''
import random
from PIL import ImageDraw
from form_generator.Box import Box
from form_generator.tools import get_class_id
class TextField:
    
    def __init__(self, width, height, arc_radius, border_color, label_outside, label_outside_color, label_inside, font, background_color, label_outside_width=None, label_position='left'):
        """
        :param font_size: between 0 and 1. percentage of the field height
        :param label_outside_width: width of the label zone in pixels. If not given, label_size will be the size of the label
        """
        
        self.width = width
        self.height = height
        self.arc_radius = arc_radius
        self.label_outside = label_outside
        self.label_outside_color = label_outside_color
        self.label_inside = label_inside
        self.border_color = border_color
        self.background_color = background_color
        self.label_outside_width = label_outside_width
        self.font = font
        self.label_position = label_position

        
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
        
        space_between_label_and_field = random.randint(10, 25)
        self.overall_width = self.width
        self.overall_height = self.height

        # box containing arc must be twice the size of the radius
        arc_size_for_corner = self.arc_radius * 2 
        
        field_x = x
        field_y = y
        label_x = x
        label_y = y
        
        if self.label_outside:
            if self.label_position == 'left':
                self.overall_width = self.label_outside_width + space_between_label_and_field + self.width
                field_x = x + self.label_outside_width + space_between_label_and_field
                image_draw.text((label_x, label_y + (self.height - label_height) / 2), self.label_outside, font=self.font, fill=self.label_outside_color)
                
            elif self.label_position == 'top':
                self.overall_height = self.height + label_height
                field_y = y + label_height + 2
                image_draw.text((label_x, label_y), self.label_outside, font=self.font, fill=self.label_outside_color)
            

        if self.arc_radius > 0:
            image_draw.arc((field_x, field_y, field_x + arc_size_for_corner, field_y + arc_size_for_corner), 180, 270, fill=self.border_color)  # top-left
            image_draw.arc((field_x, field_y + self.height - arc_size_for_corner, field_x + arc_size_for_corner, field_y + self.height), 90, 180, fill=self.border_color) # bottom-left
            image_draw.arc((field_x + self.width - arc_size_for_corner, field_y, field_x + self.width, field_y + arc_size_for_corner), -90, 0, fill=self.border_color) # top-right
            image_draw.arc((field_x + self.width - arc_size_for_corner, field_y + self.height - arc_size_for_corner, field_x + self.width, field_y + self.height), 0, 90, fill=self.border_color) # bottom -right
            
        image_draw.line([(field_x + self.arc_radius, field_y), (field_x + self.width - self.arc_radius, field_y)], fill=self.border_color) # top line
        image_draw.line([(field_x + self.width, field_y + self.arc_radius), (field_x + self.width, field_y + self.height - self.arc_radius)], fill=self.border_color) # right line
        image_draw.line([(field_x + self.arc_radius, field_y + self.height), (field_x + self.width - self.arc_radius, field_y + self.height)], fill=self.border_color) # bottom line
        image_draw.line([(field_x, field_y + self.arc_radius), (field_x, field_y + self.height - self.arc_radius)], fill=self.border_color) # left line
        
        
        ImageDraw.floodfill(img, ((2 * field_x + self.width) / 2, (2 * field_y + self.height) / 2), value=self.background_color)
        image_draw = ImageDraw.Draw(img)
        
        # add text inside field
        if self.label_inside:
            image_draw.text((field_x + 5, field_y + (self.height - label_height) / 2), self.label_inside, font=self.font, fill=(150, 150, 150))

        return [Box(get_class_id('field'), field_x - 1, field_y - 1, self.width + 2, self.height + 2), 
                Box(get_class_id('field_with_label'), label_x - 2, label_y - 2, self.overall_width + 4, self.overall_height + 4)]
    
    def get_width(self):
        return self.overall_width