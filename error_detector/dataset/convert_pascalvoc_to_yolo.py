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
allowed_classes = ['error_field', 
                   'error_message']

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
            
            
            object_box = ObjectBox(classes.index(class_name),
                               xmin,
                               xmax,
                               ymin,
                               ymax
                                )
            boxes.append(object_box)
            
        with open(os.path.join(os.path.dirname(xml_file_path), os.path.basename(xml_file_path).replace('.xml', '.txt')), 'w') as yolo_file:
            for box in boxes:
                yolo_file.write("{} {:6f} {:6f} {:6f} {:6f}\n".format(box.class_id, *convert_coords_to_yolo(box.x_min, box.x_max, box.y_min, box.y_max, image_width, image_height)))

def convert_coords_to_yolo(x_min, x_max, y_min, y_max, image_width, image_height):
    return ((x_max + x_min) / (2 * image_width),   # x % for the center of the box
               (y_max + y_min) / (2 * image_height),  # y % for the center of the box
               (x_max - x_min) / image_width,         # width % of the box
               (y_max - y_min) / image_height)

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
            
    local_dir = os.path.dirname(os.path.basename(__file__))
    with open(os.path.join(local_dir, 'data', 'web-generated.names'), 'w') as classes_file:
        for class_name in classes:
            classes_file.write(class_name + "\n")

