'''
Created on 30 sept. 2021

@author: S047432
'''
import random
import os
from PIL import ImageFont
from form_generator.Form import Form
from form_generator.tools import generate_light_color, generate_very_light_color,\
    generate_dark_color, compute_color_diff, generate_darker_color,\
    generate_red_color, generate_lighter_color, get_class_id,\
    generate_random_string
from form_generator.TextField import TextField
from form_generator.TextFieldLine import TextFieldLine
from form_generator.Checkbox import CheckboxGroup
from form_generator.RadioButton import RadioButtonGroup
from form_generator.Button import Button
from form_generator.Message import Message

class FormGenerator(object):

    def __init__(self, output_directory, number_of_images):

        self.output_directory = output_directory
        self.number_of_images = number_of_images
        
    def generate(self):
        
        min_width = 300
        max_width = 416
        max_height = 416
        min_rows = 4
        max_rows = 6
        min_field_height = 16
        max_field_height = 34 # may be 40 when field width is greater, due to font size
        min_checkbox_width = 8
        max_checkbox_width = 16
        number_of_images = self.number_of_images
        
        
        os.makedirs(self.output_directory, exist_ok=True)
        
        labels = ['Name', 'Nom', 'Prenom', 'Login', 'Age', 'password', 'Birthdate', 'location', 'information', 'vehicule', 'Chat', 
                  'naissance', 'Address', 'adresse', 'Ville', 'City', 'Rue', 'Street', 'email', 'Username', 'Contact', 'Phone', 'number', 
                  'Age', 'Message', 'zip code', 'Code postal', 'Country', 'Pays', 'State', 'Company', 'Entreprise', 'URL']
        button_labels = ['OK', 'Validate', 'Cancel', 'Save', 'Hello', 'Enregistrer', 'continue', 'Stop', 'Ajouter', 'Add', 'Remove', 'Supprimer']
        
        i = 0
        for i in range(number_of_images):
            
            print("image " + str(i))
            
            # size fields
            field_height = random.randint(min_field_height, max_field_height)
            button_height = random.randint(min_field_height, max_field_height)
            
            # font
            field_font_size = random.uniform(0.6, 0.8)
            field_font = ImageFont.truetype("form_generator/arial.ttf", int(field_height * field_font_size))
            
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
            
            
            field_has_value = random.choices([True, False])[0]   # does the field has a value inside
            yolo_coordinates = []
            field_aligned = random.randint(0, 1)
            field_names = random.choices(labels, k=rows - 3)
            field_min_label_size = max([form.img_draw.textsize(n, field_font)[0] for n in field_names])
            field_fixed_size = random.randint(field_min_label_size + 10, field_min_label_size + 30)
            border_color = (form_background_color[0] - 15, form_background_color[1] - 15, form_background_color[2] - 15)
            line_color = generate_darker_color(border_color, 50) # for TextFieldLine
            
            # be sure we do not generate a "red" color
            line_color = (min(line_color[0], int(min(line_color[1], line_color[2]) / 2)), line_color[1], line_color[2])
            
            form_color_diff = 0
            while form_color_diff < 4:
                label_color = generate_dark_color()
                form_color_diff = compute_color_diff(label_color, form_background_color)
                
            # be sure we do not generate a "red" color
            label_color = (min(label_color[0], int(min(label_color[1], label_color[2]) / 2)), label_color[1], label_color[2])
            
            for row_id, field_name in enumerate(field_names):
                
                current_field_background_color = field_background_color
                current_field_border_color = border_color
                current_field_line_color = line_color
                 
                # whether the field is in error (if it's in error, border color and/or content will be a sort of red)
                field_in_error = random.choices([True, False])[0]
                
                if field_in_error:
                    current_field_border_color = generate_red_color()
                    current_field_line_color = current_field_border_color
                    
                    # whether field background is also red
                    if random.choices([True, False])[0]:
                        current_field_background_color = generate_lighter_color(current_field_border_color, random.randint(25, 55))
                
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
                    text_field = TextField(field_width,         # field width 
                                           field_height,        # field height
                                           random.randint(0, 3),# corners
                                           current_field_border_color , 
                                           field_name,          # name of the text field
                                           label_color, 
                                           field_value, 
                                           field_font,
                                           current_field_background_color,
                                           field_label_size,
                                           field_label_position)
                else:
                    
                    
                    text_field = TextFieldLine(field_width,             # field width 
                                           field_height,                # field height
                                           current_field_line_color, 
                                           field_name,                          # name of the text field
                                           label_color, 
                                           field_value, 
                                           field_font,
                                           field_label_size)
                    
                text_field_yolo_coordinates = form.draw(10, text_field, row_id)
                
                # keep only fields in error
                if field_in_error:
                    print("field error %d:%s" % (row_id, field_name))
                    text_field_yolo_coordinates[0][0] = get_class_id('error_field')
                
                yolo_coordinates += text_field_yolo_coordinates
                
            # messages
            message_width = random.randint(form_width - 150, form_width - 50)
            message_font_size = random.uniform(0.5, field_font_size)
            message_font = ImageFont.truetype("form_generator/arial.ttf", int(field_height * message_font_size))
            message_text = generate_random_string(random.randint(10, 100), message_width, form.img_draw, message_font)
            message_height = form.img_draw.textsize(message_text, message_font)[1]
            
            message_in_error = random.choices([True, False])[0]
                
            if message_in_error:
                # background in red
                if random.choices([True, False])[0]:
                    message_background = generate_lighter_color(generate_red_color(), random.randint(35, 65))
                    text_color = label_color
                    
                # text in red
                else:
                    message_background = None
                    text_color = generate_red_color()
                print("message error")
            else:
                message_background = None
                text_color = label_color
            
            
            message = Message(width=message_width, 
                              height=message_height, 
                              background_color=message_background, 
                              text=message_text, 
                              text_color=text_color, 
                              font=message_font)
           
            message_yolo_coordinates = form.draw((form_width - message_width) / 2, 
                                          message, 
                                          rows - 3, 
                                          y_offset_after_text_fields)
             
            # keep only messages in error
            if message_in_error:
                message_yolo_coordinates[0][0] = get_class_id('error_message')
            

            yolo_coordinates += message_yolo_coordinates
        
            image_quality = random.randint(70, 100)
            
            form.create_image(self.output_directory + "/out-{}.jpg".format(i), yolo_coordinates, image_quality)