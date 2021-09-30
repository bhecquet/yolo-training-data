'''
Created on 30 sept. 2021

@author: S047432
'''
import random
import string
import textwrap


classes = {}

def get_class_id(class_name):
    return classes.get(class_name, None)

def set_classes(classe_ids):
    global classes
    classes = classe_ids

def generate_light_color():
    min_sum = 600
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
     
def generate_lighter_color(origin_color, light_index):
    return (min(origin_color[0] + light_index, 255),
            min(origin_color[1] + light_index, 255),
            min(origin_color[2] + light_index, 255))
            
def generate_very_light_color():
    first_channel = random.randint(245, 255)
    second_channel = random.randint(245, 255)
    thrid_channel = random.randint(245, 255)
    color = [first_channel, second_channel, thrid_channel]
    random.shuffle(color)
    return tuple(color) 

def generate_red_color():
    red_channel = random.randint(128, 255)
    if red_channel > 180:
        other_channel = random.randint(0, 128)
    else:
        other_channel = 0
    
    return (red_channel, other_channel, other_channel)

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

def generate_random_string(length, max_width, image_draw, font):
    """
    Generate a random text of [length] character
    This text will wrap in a [max_width] box
    """
    letters = string.ascii_lowercase + '       aaeeeeiioouu.,'
    text = ''.join(random.choice(letters) for i in range(length))
    
    text_width, text_height = image_draw.textsize(text, font)
    
    # find the appropriate width, wrapping text if necessary
    if text_width > max_width:
        good_width = -1
        for i in range(10, len(text)):
            if image_draw.textsize(text[0:i], font)[0] > max_width:
                break
            else:
                good_width = i
                
        text = '\n'.join(textwrap.wrap(text, good_width))
    
    return text
    