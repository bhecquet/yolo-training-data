'''
Created on 22 janv. 2020

@author: S047432
'''
from xml.dom import minidom
import argparse
import os
import logging
import collections
import shutil
from PIL import Image

classes = []
ObjectBox = collections.namedtuple('ObjectBox', ['class_id', 'x_min', 'x_max', 'y_min', 'y_max'])

# list of classes that we want exported to yolo text files
# order depends on class_id defined in 'generate-html.py'
allowed_classes = ['field', 
                   'button', 
                   'checkbox', 
                   'radio', 
                   'field_with_label',
                   'checkbox_with_label',
                   'radio_with_label',
                   'field_line', 
                   'field_line_with_label',   
                   '_form_']

def convert(xml_file_path, output_dir):
    """
    convert XML file created by LabelImg (PascalVOC format) to yolo format file
    """
    boxes = []
    forms = []
    
    with open(xml_file_path, 'r') as xml_file:
        
        logging.info("processing %s" % xml_file_path)
        document = minidom.parse(xml_file)
        
        size = document.getElementsByTagName('size')[0]
        image_width = int(size.getElementsByTagName('width')[0].firstChild.nodeValue)
        image_height = int(size.getElementsByTagName('height')[0].firstChild.nodeValue)
        
        image_file =  document.getElementsByTagName('filename')[0].firstChild.nodeValue
        image_file_path = os.path.dirname(xml_file_path) + os.sep + image_file
        
        for detect_object in document.getElementsByTagName('object'):
            class_name = detect_object.getElementsByTagName('name')[0].firstChild.nodeValue
            
            if class_name not in allowed_classes:
                continue
            
            if class_name not in classes and class_name != '_form_':
                classes.append(class_name)
                
            box = detect_object.getElementsByTagName('bndbox')[0]
            xmin = int(box.getElementsByTagName('xmin')[0].firstChild.nodeValue)
            ymin = int(box.getElementsByTagName('ymin')[0].firstChild.nodeValue)
            xmax = int(box.getElementsByTagName('xmax')[0].firstChild.nodeValue)
            ymax = int(box.getElementsByTagName('ymax')[0].firstChild.nodeValue)
            
            
            
            if class_name == '_form_':
                object_box = ObjectBox(-1,
                                   xmin,
                                   xmax,
                                   ymin,
                                   ymax
                                    )
                forms.append(object_box)
            else:
                object_box = ObjectBox(classes.index(class_name),
                                   xmin,
                                   xmax,
                                   ymin,
                                   ymax
                                    )
                boxes.append(object_box)

            
        extract_forms(image_file_path, forms, boxes, output_dir)
            
        with open(os.path.join(os.path.dirname(xml_file_path), os.path.basename(xml_file_path).replace('.xml', '.txt')), 'w') as yolo_file:
            for box in boxes:
                yolo_file.write("{} {:6f} {:6f} {:6f} {:6f}\n".format(box.class_id, *convert_coords_to_yolo(box.x_min, box.x_max, box.y_min, box.y_max, image_width, image_height)))

def convert_coords_to_yolo(x_min, x_max, y_min, y_max, image_width, image_height):
    return ((x_max + x_min) / (2 * image_width),   # x % for the center of the box
               (y_max + y_min) / (2 * image_height),  # y % for the center of the box
               (x_max - x_min) / image_width,         # width % of the box
               (y_max - y_min) / image_height)
    
def create_pascal_voc_file(folder, filename, image_width, image_height, boxes):
    form = minidom.parseString("""
    <annotation>
    <folder>formulaires</folder>
    <filename>{}</filename>
    <path>{}/{}</path>
    <source>
        <database>Unknown</database>
    </source>
    <size>
        <width>{}</width>
        <height>{}</height>
        <depth>3</depth>
    </size>
    <segmented>0</segmented>
    </annotation>
    """.format(filename, folder, filename, image_width, image_height))
    
    for box in boxes:
        object = minidom.parseString("""<object>
        <name>{}</name>
        <pose>Unspecified</pose>
        <truncated>0</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>{}</xmin>
            <ymin>{}</ymin>
            <xmax>{}</xmax>
            <ymax>{}</ymax>
        </bndbox>
    </object>""".format(classes[box.class_id], box.x_min, box.y_min, box.x_max, box.y_max))
        form.childNodes[0].appendChild(object.childNodes[0])
        
    xml_content = form.toxml()
        
    with open(os.path.join(folder, filename.replace('.jpg', '.xml')), 'w') as xml_file:
        xml_file.write(xml_content)
        
def extract_forms(image_file_path, form_coords, element_boxes, output_dir):
    """
    extract image based on '_form_' class coordinates
    """
    with open(image_file_path, 'rb') as image_file:
        image_name = os.path.basename(image_file_path)
        img = Image.open(image_file)
        
        for i, form in enumerate(form_coords):
            name, ext = os.path.splitext(image_name)
            form_image_name = "{}--{}{}".format(name, i, ext)
            new_img = img.crop((form.x_min, form.y_min, form.x_max, form.y_max))
            new_img.save(os.path.join(output_dir, form_image_name))
            
            form_width = form.x_max - form.x_min
            form_height = form.y_max - form.y_min
            
            # create yolo file
            boxes_in_form = []
            with open(os.path.join(output_dir, form_image_name.replace(ext, '.txt')), 'w') as yolo_file:
                for box in element_boxes:
                    if box.x_min >= form.x_min and box.x_max <= form.x_max and box.y_min >= form.y_min and box.y_max <= form.y_max:
                        box_in_form = ObjectBox(box.class_id,
                                   box.x_min - form.x_min,
                                   box.x_max - form.x_min,
                                   box.y_min - form.y_min,
                                   box.y_max - form.y_min
                                    )
                        boxes_in_form.append(box_in_form)
                        yolo_file.write("{} {:6f} {:6f} {:6f} {:6f}\n".format(box.class_id, 
                                                                              *convert_coords_to_yolo(box.x_min - form.x_min, 
                                                                                                      box.x_max - form.x_min, 
                                                                                                      box.y_min - form.y_min, 
                                                                                                      box.y_max - form.y_min, 
                                                                                                      form_width, 
                                                                                                      form_height)))
                        
            create_pascal_voc_file(output_dir, form_image_name, form_width, form_height, boxes_in_form)
           
                    
            

if __name__ == '__main__':
    
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(description='Tool for converting PascalVOC format to yolo format')
    parser.add_argument('input', help='Input directory where PascalVOC (XML) formatted files are')
    parser.add_argument('output', help='Output directory where yolo files will be written')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.input):
        logging.error("{} does not exist".format(args.input))
        
    os.makedirs(args.output, exist_ok=True)
        
    for file in os.listdir(args.input):
        file_path = os.path.join(args.input, file)
        if os.path.splitext(file_path)[1] == '.xml':
            convert(file_path, args.output)
            
    with open(os.path.join(args.output, 'all_classes.txt'), 'w') as classes_file:
        for class_name in classes:
            classes_file.write(class_name + "\n")

