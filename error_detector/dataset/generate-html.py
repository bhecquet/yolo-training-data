'''
Created on 31 mars 2020

@author: S047432

TODO: 
- label above field, not on the left
- no label at all (there must be content
- same color for form background and field background
- more contrasted color for field line
- field background different of grey
'''
import PIL
from PIL import Image, ImageDraw, ImageFont
import random
import sys
import os
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
import collections

DEBUG = False

classes = {}

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

        return [Box(classes['field'], field_x - 1, field_y - 1, self.width + 2, self.height + 2), 
                Box(classes['field_with_label'], label_x - 2, label_y - 2, self.overall_width + 4, self.overall_height + 4)]
    
    def get_width(self):
        return self.overall_width
        
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

        image_draw.line([(field_x, y + self.height), (field_x + self.width, y + self.height)], fill=self.border_color)
  
        if self.label_outside:
            image_draw.text((x, y + (self.height - label_height) / 2), self.label_outside, font=self.font, fill=self.label_outside_color)
           
        if self.label_inside:
            image_draw.text((field_x + 5, y + (self.height - label_height) / 2), self.label_inside, font=self.font, fill=(150, 150, 150))

        return [Box(classes['field_line'], field_x, y, self.width, self.height + 1), 
                Box(classes['field_line_with_label'], x - 1, y - 1, self.overall_width + 2, self.overall_height + 3)]
    
    def get_width(self):
        return self.overall_width
        
        
class Button:
    
    def __init__(self, width, height, arc_radius, form_background_color, label_inside, label_inside_color, font_size):
        self.width = width
        self.height = height
        self.arc_radius = arc_radius
        self.label_inside = label_inside
        self.label_inside_color = label_inside_color
        self.border_color = form_background_color
        self.background_color = form_background_color
        self.font_size = font_size
        
        self.overall_width = self.width
        
    def draw(self, x, y, img, image_draw):
        """
        :param x: the x position of the element
        :param y: the y position of the element
        :param img: The image element we are drawing on
        :param image_draw: the PIL ImageDraw object
        """
        font_size = int(self.height * self.font_size)
        font = ImageFont.truetype("arial.ttf", font_size)
        
        # box containing arc must be twice the size of the radius
        arc_size_for_corner = self.arc_radius * 2 
        text_width, text_height = image_draw.textsize(self.label_inside, font)
        
        # change width if its too low
        self.width = max(text_width + 10, self.width)

        if self.arc_radius > 0:
            image_draw.arc((x, y, x + arc_size_for_corner, y + arc_size_for_corner), 180, 270, fill=self.border_color)  # top-left
            image_draw.arc((x, y + self.height - arc_size_for_corner, x + arc_size_for_corner, y + self.height), 90, 180, fill=self.border_color) # bottom-left
            image_draw.arc((x + self.width - arc_size_for_corner, y, x + self.width, y + arc_size_for_corner), -90, 0, fill=self.border_color) # top-right
            image_draw.arc((x + self.width - arc_size_for_corner, y + self.height - arc_size_for_corner, x + self.width, y + self.height), 0, 90, fill=self.border_color) # bottom -right
            
        image_draw.line([(x + self.arc_radius, y), (x + self.width - self.arc_radius, y)], fill=self.border_color) # top line
        image_draw.line([(x + self.width, y + self.arc_radius), (x + self.width, y + self.height - self.arc_radius)], fill=self.border_color) # right line
        image_draw.line([(x + self.arc_radius, y + self.height), (x + self.width - self.arc_radius, y + self.height)], fill=self.border_color) # bottom line
        image_draw.line([(x, y + self.arc_radius), (x, y + self.height - self.arc_radius)], fill=self.border_color) # left line
        
        ImageDraw.floodfill(img, ((2 * x + self.width) / 2, (2 * y + self.height) / 2), value=self.background_color)
        image_draw = ImageDraw.Draw(img)

        image_draw.text((x + (self.width - text_width) / 2, y + (self.height - text_height) / 2), self.label_inside, font=font, fill=self.label_inside_color)
        
        return [Box(classes['button'], x - 1, y - 1, self.width + 2, self.height + 2)]
    
    def get_width(self):
        return self.overall_width
    
class Checkbox:
    
    def __init__(self, width, arc_radius, border_color, label, label_color, font, background_color, checked=False, check_color=(0, 0, 0), text_after=True):
        self.width = width
        self.height = width
        self.arc_radius = arc_radius
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
            field_x = self._draw_box(image_draw, img, x, y, 0)
            self._write_text(image_draw, label_height, x + 5 + self.width, y)
        else:
            field_x = self._draw_box(image_draw, img, x, y, label_width + 5)
            self._write_text(image_draw, label_height, x, y)
        
        if self.checked:
            start_point1 = (field_x + 1, y + self.height / 2)
            end_point1 = (field_x + self.width / 2, y + self.height - 2)
            end_point2 = (field_x + self.width - 1, y + 1)
            image_draw.line([start_point1, end_point1, end_point2], fill=self.check_color, width=2)
            
            
        return [Box(classes['checkbox'], field_x - 1, y - 1, self.width + 2, self.height + 2), 
                Box(classes['checkbox_with_label'], x - 2, y - 2, self.overall_width + 2, max(label_height, self.height + 4))]
    
    def _draw_box(self, image_draw, img, x, y, label_width):
        # box containing arc must be twice the size of the radius
        arc_size_for_corner = self.arc_radius * 2 
    
        field_x = x + label_width

        if self.arc_radius > 0:
            image_draw.arc((field_x, y, field_x + arc_size_for_corner, y + arc_size_for_corner), 180, 270, fill=self.border_color)  # top-left
            image_draw.arc((field_x, y + self.height - arc_size_for_corner, field_x + arc_size_for_corner, y + self.height), 90, 180, fill=self.border_color) # bottom-left
            image_draw.arc((field_x + self.width - arc_size_for_corner, y, field_x + self.width, y + arc_size_for_corner), -90, 0, fill=self.border_color) # top-right
            image_draw.arc((field_x + self.width - arc_size_for_corner, y + self.height - arc_size_for_corner, field_x + self.width, y + self.height), 0, 90, fill=self.border_color) # bottom -right
            
        image_draw.line([(field_x + self.arc_radius, y), (field_x + self.width - self.arc_radius, y)], fill=self.border_color) # top line
        image_draw.line([(field_x + self.width, y + self.arc_radius), (field_x + self.width, y + self.height - self.arc_radius)], fill=self.border_color) # right line
        image_draw.line([(field_x + self.arc_radius, y + self.height), (field_x + self.width - self.arc_radius, y + self.height)], fill=self.border_color) # bottom line
        image_draw.line([(field_x, y + self.arc_radius), (field_x, y + self.height - self.arc_radius)], fill=self.border_color) # left line
        
        
        ImageDraw.floodfill(img, ((2 * field_x + self.width) / 2, (2 * y + self.height) / 2), value=self.background_color)
        return field_x
    
    def _write_text(self, image_draw, label_height, x, y):
        image_draw.text((x, y + (self.height - label_height) / 2), self.label, font=self.font, fill=self.label_color)
        
    
    def get_width(self):
        return self.overall_width
        
class CheckboxGroup:
    """
    Group of check boxes
    """
    
    def __init__(self, width, arc_radius, border_color, labels, label_color, font, background_color, checked=False, vertical_layout=True):

        self.vertical_layout = vertical_layout
        
        self.width = width
        self.arc_radius = arc_radius
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
            
            checkbox = Checkbox(self.width, 
                                self.arc_radius, 
                                self.border_color, 
                                label, 
                                self.label_color, 
                                self.font, 
                                self.background_color,
                                check_color=check_color,
                                checked=random.choice([True, False]))
            label_width, label_height, overall_width = checkbox.get_dimensions(form.img_draw)
            
            if (x + overall_width < form.width):
                coordinates += form.draw(x, checkbox, row_id, y_offset)
                x += checkbox.get_width() + 20
            else:
                print("No space to draw checkbox")
            
        return coordinates
    
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
            
        return [Box(classes['radio'], field_x - 1, y - 1, self.width + 2, self.height + 2), 
                Box(classes['radio_with_label'], x - 2, y - 2, self.overall_width + 2, max(label_height, self.height + 4))]
    
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

    
class Form:
    
    def __init__(self, form_background_color, width, height, rows, row_height):
        """
        Draw a form with a color and size
        :param form_background_color: a RGB tuple or string
        :param width: background width
        :param height: background height
        :param rows: number of rows
        """
        
        supersample_factor = 1 # TODO: apply
        self.background_color = form_background_color
        self.width = width
        self.height = height
        self.rows = rows
        self.row_height = row_height
        self.margin_top = (self.height - self.rows * self.row_height) / 2
        
        self.img = Image.new('RGB', (width * supersample_factor, height * supersample_factor), form_background_color)
        self.img_draw = ImageDraw.Draw(self.img)
        
    def draw(self, x, element, row, y_offset=0):
        y = self.margin_top + row * self.row_height + y_offset
        boxes = element.draw(x, y, self.img, self.img_draw)

        # compute bounding box coordinates in yolo format (class_id, center_x, center_y, width, height). All coordinates are computed relative to picture size
        coordinates = [(boxes[0].class_id,
                (2 * boxes[0].x + boxes[0].w) / (2 * self.width),
                (2 * boxes[0].y + boxes[0].h) / (2 * self.height),
                boxes[0].w / self.width,
                boxes[0].h / self.height
                )]
        boxes[0].debug(self.img_draw)
        
        if len(boxes) > 1:
            coordinates.append(
                (boxes[1].class_id,
                (2 * boxes[1].x + boxes[1].w) / (2 * self.width),
                (2 * boxes[1].y + boxes[1].h) / (2 * self.height),
                boxes[1].w / self.width,
                boxes[1].h / self.height
                )
            )
            boxes[1].debug(self.img_draw)
            
        return coordinates
        
    def create_image(self, path, yolo_coordinates, image_quality):
        """
        creates the image file
        """
        self.img = self.img.resize((self.width, self.height), Image.ANTIALIAS)
        
        with open(path, 'wb') as output:
            self.img.save(output, format="JPEG", quality=image_quality)
            
        with open(path.replace('.jpg', '.txt'), 'w') as yolo:
            for yolo_coordinate in yolo_coordinates:
                yolo.write("{} {:6f} {:6f} {:6f} {:6f}\n".format(*yolo_coordinate))
            
def generate_light_color():
    min_sum = 550
    first_channel = 255
    second_channel = random.randint(190, 255)
    thrid_channel = random.randint(min_sum - first_channel - second_channel, 255)
    color = [first_channel, second_channel, thrid_channel]
    random.shuffle(color)
    return tuple(color) 
     
def generate_darker_color(origin_color, dark_index):
    return (max(origin_color[0] - dark_index, 0),
            max(origin_color[1] - dark_index, 0),
            max(origin_color[2] - dark_index, 0))
            
def generate_very_light_color():
    first_channel = random.randint(245, 255)
    second_channel = random.randint(245, 255)
    thrid_channel = random.randint(245, 255)
    color = [first_channel, second_channel, thrid_channel]
    random.shuffle(color)
    return tuple(color) 


def generate_dark_color():
    max_sum = 450
    first_channel = random.randint(0, 255)
    second_channel = random.randint(0, min(255, max_sum - first_channel))
    thrid_channel = random.randint(0, min(255, max_sum - first_channel - second_channel))
    color = [first_channel, second_channel, thrid_channel]
    random.shuffle(color)
    return tuple(color) 


def luminance(color):
    
    def factor(channel_value):
        channel_factor = channel_value / 255.
        if channel_factor <= 0.03928:
            channel_factor = channel_factor / 12.92;
        else:
            channel_factor = ((channel_factor + 0.055) / 1.055) ** 2.4
        return channel_factor

    return (factor(color[0]) * 0.2126 + factor(color[1]) * 0.7152 + factor(color[2]) * 0.0722) + 0.05; 

def compute_color_diff(color1, color2):
    
    lum1 = luminance(color1);
    lum2 = luminance(color2);
    brightest = max(lum1, lum2);
    darkest = min(lum1, lum2);
    return brightest / darkest;
    
#     color1_rgb = sRGBColor(color1[0] / 255., color1[1] / 255., color1[2] / 255.);
#     color2_rgb = sRGBColor(color2[0] / 255., color2[1] / 255., color2[2] / 255.); 
#     
#     color1_lab = convert_color(color1_rgb, LabColor);
#     color2_lab = convert_color(color2_rgb, LabColor);
#     
#     return delta_e_cie2000(color1_lab, color2_lab);  

def compute_class_id(class_file_path):
    """
    read the 'class_file' which references the classes allowed for computation
    """
    with open(class_file_path, 'r') as class_file:
        for i, line in enumerate(class_file):
            if line:
                classes[line.strip()] = i


if __name__ == '__main__':
    
    # name of the class file must be provided: give a xxx.names file path
    compute_class_id(sys.argv[1])
    
    min_width = 300
    max_width = 416
    max_height = 416
    min_rows = 4
    max_rows = 6
    min_field_height = 16
    max_field_height = 34 # may be 40 when field width is greater, due to font size
    min_checkbox_width = 8
    max_checkbox_width = 16
    number_of_images = 2000
    
    
    os.makedirs('out', exist_ok=True)
    
    labels = ['Name', 'Nom', 'Prenom', 'Login', 'Age', 'password', 'Birthdate', 'location', 'information', 'vehicule', 'Chat', 
              'naissance', 'Address', 'adresse', 'Ville', 'City', 'Rue', 'Street', 'email', 'Username', 'Contact', 'Phone', 'number', 
              'Age', 'Message', 'zip code', 'Code postal', 'Country', 'Pays', 'State', 'Company', 'Entreprise', 'URL']
    button_labels = ['OK', 'Validate', 'Cancel', 'Save', 'Hello', 'Enregistrer', 'continue', 'Stop', 'Ajouter', 'Add', 'Remove', 'Supprimer']
    
    i = 0
    for i in range(number_of_images):
        
        # size fields
        field_height = random.randint(min_field_height, max_field_height)
        button_height = random.randint(min_field_height, max_field_height)
        
        # font
        field_font_size = random.uniform(0.6, 0.8)
        field_font = ImageFont.truetype("arial.ttf", int(field_height * field_font_size))
        
        # whether to choose standard field (rectangle) or line field (text underlined
        text_field_class = random.choices(['TextField', 'TextFieldLine'])[0]
        field_label_position = random.choices(['top', 'left'])[0]
                
        
        
        # row spacing
        if field_label_position == 'top':
            
            form = Form((0,0,0), 100, 100, 1, 60)
            field_max_label_height = max([form.img_draw.textsize(n, field_font)[1] for n in labels])
            row_spacing = random.randint(min(field_max_label_height + 2, max_field_height), max_field_height) # spacing between each row
            y_offset_after_text_fields = field_max_label_height # with top labels, text fields is moved downwards and can overlap checkboxes
        else:
            row_spacing = random.randint(5, max_field_height) # spacing between each row
            y_offset_after_text_fields = 0
            
        # compute max number of rows to avoid having too much fields for the form
        max_rows = int(int(max_height - (button_height + row_spacing)) / (row_spacing + field_height))
        rows = random.randint(min_rows, max_rows)
          
        # form properties  
        form_height = random.randint(25 + (rows - 1) * (row_spacing + field_height) + button_height + row_spacing, max_height)
        form_width = random.randint(min_width, max_width)
        form_background_color = generate_light_color()
        form = Form(form_background_color, form_width, form_height, rows, row_spacing + field_height)
        print("form %dx%d" % (form_width, form_height))
        field_background_color = generate_very_light_color()
        button_font_size = random.uniform(0.6, 0.8)
        field_has_value = random.choices([True, False])[0]   # does the field has a value inside
        yolo_coordinates = []
        field_aligned = random.randint(0, 1)
        field_names = random.choices(labels, k=rows - 3)
        field_min_label_size = max([form.img_draw.textsize(n, field_font)[0] for n in field_names])
        field_fixed_size = random.randint(field_min_label_size + 10, field_min_label_size + 30)
        border_color = (form_background_color[0] - 15, form_background_color[1] - 15, form_background_color[2] - 15)
        
        form_color_diff = 0
        while form_color_diff < 4:
            label_color = generate_dark_color()
            form_color_diff = compute_color_diff(label_color, form_background_color)
            
        button_color_diff = 0
        while button_color_diff < 2:
            button_color = generate_dark_color()
            button_label_color = generate_light_color()
            button_color_diff = compute_color_diff(button_color, button_label_color)
        
        for row_id, field_name in enumerate(field_names):
            
            if field_aligned: # field aligned
                field_label_size = field_fixed_size
            else:
                field_label_size = form.img_draw.textsize(field_name, field_font)[0]
            
            # compute field size depending on form width and label size so that it does not go outside of image
            field_width = random.randint(form.img_draw.textsize(field_name, field_font)[0], form_width - field_label_size - 30) # (10 px of left margin + 20 px of space between text and field)
            
            if field_has_value:
                field_value = field_name
            else:
                field_value = ""
            
            if text_field_class == 'TextField':
                text_field = TextField(field_width, # field width 
                                       field_height,              # field height
                                       random.randint(0, 3),                # corners
                                       border_color , 
                                       field_name,                          # name of the text field
                                       label_color, 
                                       field_value, 
                                       field_font,
                                       field_background_color,
                                       field_label_size,
                                       field_label_position)
            else:
                text_field = TextFieldLine(field_width, # field width 
                                       field_height,              # field height
                                       generate_darker_color(border_color, 50), 
                                       field_name,                          # name of the text field
                                       label_color, 
                                       field_value, 
                                       field_font,
                                       field_label_size)
                
            yolo_coordinates += form.draw(10, text_field, row_id)
            
        # checkboxes
        row_id += 1
        checkbox_radio_width = field_height * 0.5
        checkbox_labels = random.choices(labels, k=random.randint(1, int(form_width / 100)))
        checkbox_group = CheckboxGroup(checkbox_radio_width, 
                                       random.randint(0, 3), 
                                       border_color, 
                                       checkbox_labels, 
                                       label_color, 
                                       field_font, 
                                       field_background_color, 
                                       checked=False, 
                                       vertical_layout=False)
        yolo_coordinates += checkbox_group.draw(form, row_id, y_offset_after_text_fields)
            
        # radio buttons
        row_id += 1
        radio_labels = random.choices(labels, k=random.randint(1, int(form_width / 100)))
        radio_group = RadioButtonGroup(checkbox_radio_width, 
                                       border_color, 
                                       radio_labels, 
                                       label_color, 
                                       field_font, 
                                       field_background_color, 
                                       checked=False, 
                                       vertical_layout=False)
        yolo_coordinates += radio_group.draw(form, row_id, y_offset_after_text_fields)
    
        # buttons
        button_name = random.choice(button_labels)
        button_width = random.randint(len(button_name) * 15, len(button_name) * 25)
        button_position_x = random.randint(10, form_width - button_width - 20)
        button = Button(button_width, 
                        button_height,
                        random.randint(0, 3),                # corners
                        button_color, 
                        button_name, 
                        button_label_color,
                        button_font_size)
        yolo_coordinates += form.draw(button_position_x, button, rows - 1, y_offset_after_text_fields)
        image_quality = random.randint(70, 100)
        
        print("image " + str(i))
        form.create_image("out/out-{}.jpg".format(i), yolo_coordinates, image_quality)
    
  