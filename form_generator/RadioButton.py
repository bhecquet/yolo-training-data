'''
Created on 30 sept. 2021

@author: S047432
'''
import random

from PIL import ImageDraw

from form_generator.Box import Box
from form_generator.tools import generate_darker_color, get_class_id

class RadioButton:
    
    def __init__(self, width, border_color, label, label_color, font, background_color, checked=False, check_color=(0, 0, 0), text_after=True):
        self.width = width
        self.height = width
        self.label = label
        self.label_color = label_color
        self.border_color = border_color
        self.background_color = background_color
        self.font = font
        self.checked = checked
        self.check_color = check_color
        self.text_after = text_after
        
            
    def get_dimensions(self, image_draw):
        label_width, label_height = image_draw.textsize(self.label, self.font)
        overall_width = label_width + 5 + self.width
        
        return label_width, label_height, overall_width
        
    def draw(self, x, y, img, image_draw):
        # compute size of the field
        label_width, label_height, self.overall_width = self.get_dimensions(image_draw)

        if self.text_after:
            field_x = self._draw_radio(image_draw, img, x, y, 0)
            self._write_text(image_draw, label_height, x + 5 + self.width, y)
        else:
            field_x = self._draw_radio(image_draw, img, x, y, label_width + 5)
            self._write_text(image_draw, label_height, x, y)
        
        if self.checked:
            circle_crop = random.choice([2, 3])
            image_draw.arc((field_x + circle_crop, y + circle_crop, field_x + self.width - circle_crop, y + self.height - circle_crop), 0, 360, fill=self.check_color) 
            ImageDraw.floodfill(img, ((2 * field_x + self.width) / 2, (2 * y + self.height) / 2), value=self.check_color)
            
        return [Box(get_class_id('radio'), field_x - 1, y - 1, self.width + 2, self.height + 2), 
                Box(get_class_id('radio_with_label'), x - 2, y - 2, self.overall_width + 2, max(label_height, self.height + 4))]
    
    def _draw_radio(self, image_draw, img, x, y, label_width):
        """
        Draw radion button
        @param x: position of the top-left point
        @param y: position of the top-left point
        @param label_width: length of the label that will be written before or after the radio button
        @return: x position of the final drawing
        """

        field_x = x + label_width

        image_draw.arc((field_x, y, field_x + self.width, y + self.height), 0, 360, fill=self.border_color) 
       
        ImageDraw.floodfill(img, ((2 * field_x + self.width) / 2, (2 * y + self.height) / 2), value=self.background_color)
        return field_x
    
    def _write_text(self, image_draw, label_height, x, y):
        image_draw.text((x, y + (self.height - label_height) / 2), self.label, font=self.font, fill=self.label_color)
        
    
    def get_width(self):
        return self.overall_width
    
class RadioButtonGroup:
    """
    Group of radio buttons
    """
    
    def __init__(self, width, border_color, labels, label_color, font, background_color, checked=False, vertical_layout=True):

        self.vertical_layout = vertical_layout
        
        self.width = width
        self.labels = labels
        self.label_color = label_color
        self.border_color = border_color
        self.background_color = background_color
        self.font = font
 
    def draw(self, form, row_id, y_offset):
        
        check_color = generate_darker_color(self.border_color, 50)
        if random.choice([True, False]):
            check_color = (0, 0, 0)
        
        x = 10
        coordinates = []
        for label in self.labels:
            
            radio = RadioButton(self.width, 
                                self.border_color, 
                                label, 
                                self.label_color, 
                                self.font, 
                                self.background_color,
                                check_color=check_color,
                                checked=random.choice([True, False]))
            
            label_width, label_height, overall_width = radio.get_dimensions(form.img_draw)
            
            if (x + overall_width < form.width):
                coordinates += form.draw(x, radio, row_id, y_offset)
                x += radio.get_width() + 20
            else:
                print("No space to draw radio")

            
        return coordinates