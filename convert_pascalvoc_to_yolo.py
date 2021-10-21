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
import yaml

ObjectBox = collections.namedtuple('ObjectBox', ['class_id', 'x_min', 'x_max', 'y_min', 'y_max'])
allowed_classes = []

def convert_to_jpg(image_file_path):
    """
    if file is not jpg, convert to jpg
    """
    if image_file_path.lower().endswith(".jpg") or image_file_path.lower().endswith(".jpeg"):
        return image_file_path, False
    
    jpg_image_file_path = image_file_path.replace(os.path.splitext(image_file_path)[1], '.jpg')
    
    if not os.path.isfile(jpg_image_file_path):
        Image.open(image_file_path).convert("RGB").save(jpg_image_file_path, "jpeg")
    
    return jpg_image_file_path, True

def convert(xml_file_path, output_dir):
    """
    convert XML file created by LabelImg (PascalVOC format) to yolo format file
    """
    boxes = []
    forms = []
    image_converted = False
    
    with open(xml_file_path, 'r') as xml_file:
        
        logging.info("processing %s" % xml_file_path)
        document = minidom.parse(xml_file)
        
        size = document.getElementsByTagName('size')[0]
        image_width = int(size.getElementsByTagName('width')[0].firstChild.nodeValue)
        image_height = int(size.getElementsByTagName('height')[0].firstChild.nodeValue)
        
        image_file =  document.getElementsByTagName('filename')[0].firstChild.nodeValue
        image_file_path = os.path.dirname(xml_file_path) + os.sep + image_file
        
        # convert image and update XML
        image_file_path, image_converted = convert_to_jpg(image_file_path)
        
        if image_converted:
            document.getElementsByTagName('path')[0].firstChild.nodeValue = image_file_path
            document.getElementsByTagName('filename')[0].firstChild.nodeValue = os.path.basename(image_file_path)
        
        for detect_object in document.getElementsByTagName('object'):
            class_name = detect_object.getElementsByTagName('name')[0].firstChild.nodeValue
            
            if class_name not in allowed_classes:
                continue
      
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
                object_box = ObjectBox(allowed_classes.index(class_name),
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

    # update XML file
    if image_converted:
        with open(xml_file_path, 'w') as xml_file:
            document.writexml(xml_file)

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
    </object>""".format(allowed_classes[box.class_id], box.x_min, box.y_min, box.x_max, box.y_max))
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
           
                    
def extract_class_names(model_configuration_file):
    global allowed_classes
    with open(os.path.abspath(model_configuration_file)) as conf:
        data = yaml.load(conf, Loader=yaml.FullLoader)
        allowed_classes = data['names'] + ['_form_']

if __name__ == '__main__':
    
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(description='Tool for converting PascalVOC format to yolo format')
    parser.add_argument('input', help='Input directory where PascalVOC (XML) formatted files are')
    parser.add_argument('output', help='Output directory where yolo files will be written')
    parser.add_argument('modelConf', help='Path to the YAML model configuration file. It contains at least the list of classes ')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.input):
        logging.error("{} does not exist".format(args.input))
        
    os.makedirs(args.output, exist_ok=True)
    
    extract_class_names(args.modelConf)
        
    for file in os.listdir(os.path.abspath(args.input)):
        file_path = os.path.join(os.path.abspath(args.input), file)
        if os.path.splitext(file_path)[1] == '.xml':
            convert(file_path, os.path.abspath(args.output))
            
  

