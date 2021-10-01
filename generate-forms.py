'''
Created on 30 sept. 2021
This scripts aims at generating form pictures that can be used to train yolo model

@author: S047432
'''
import argparse
import logging
import os
import yaml
from form_generator.tools import set_classes
from field_detector.FormGenerator import FormGenerator as FormGeneratorForFieldDetector
from error_detector.FormGenerator import FormGenerator as FormGeneratorForErrorDetector


                    
def extract_class_names(model_configuration_file):
    
    allowed_classes = {}
    with open(os.path.abspath(model_configuration_file)) as conf:
        data = yaml.load(conf, Loader=yaml.FullLoader)
        for i, class_name in enumerate(data['names']):
            allowed_classes[class_name] = i

    return allowed_classes

if __name__ == '__main__':
    
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(description='Tool for generating training picture for a specific model')
    parser.add_argument('modelConf', help='Path to the YAML model configuration file. It contains at least le list of classes ')
    parser.add_argument('modelName', choices=['field_detector', 'error_detector'], help='Name of the model for which we create files')
    parser.add_argument('output', help='Output directory where image files will be written')
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    
    set_classes(extract_class_names(args.modelConf)) 
   
    if args.modelName == 'field_detector':
        generator = FormGeneratorForFieldDetector(args.output, 2000)
    elif args.modelName == 'error_detector':
        generator = FormGeneratorForErrorDetector(args.output, 1000)
        
    generator.generate()