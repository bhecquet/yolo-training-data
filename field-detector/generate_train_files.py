"""
Script that will create a "dataset" folder with "images" and "labels" sub-folders
These folders will contain pictures from "dataset_extracted" and "dataset_real" folders
"""
import glob, os
import random
import shutil

local_path = os.path.dirname(os.path.abspath(__file__)) + '/'


# Percentage of images to be used for the test set
percentage_test = 10;
max_number_of_files = 2000
dataset_folder = local_path + 'dataset'
dataset_training_folder = os.path.join(dataset_folder, 'training')
dataset_testing_folder = os.path.join(dataset_folder, 'testing')
dataset_training_images_folder = os.path.join(dataset_training_folder, 'images')
dataset_training_labels_folder = os.path.join(dataset_training_folder, 'labels')
dataset_testing_images_folder = os.path.join(dataset_testing_folder, 'images')
dataset_testing_labels_folder = os.path.join(dataset_testing_folder, 'labels')


if os.path.isdir(dataset_folder):
    shutil.rmtree(dataset_folder, ignore_errors=True)
os.makedirs(dataset_training_images_folder, exist_ok=True)
os.makedirs(dataset_training_labels_folder, exist_ok=True)
os.makedirs(dataset_testing_images_folder, exist_ok=True)
os.makedirs(dataset_testing_labels_folder, exist_ok=True)

for dataset_path in [local_path + 'dataset_extracted', local_path + 'dataset_generated_small']:
    
    random.seed(2)
    
    counter = 1  
    index_test = round(100 / percentage_test)  
    for path_and_filename in glob.iglob(os.path.join(dataset_path, "*.jpg")):  
        file_path, ext = os.path.splitext(path_and_filename)
        
        train_or_test = random.randint(0, 100)
        if train_or_test < percentage_test:
            shutil.copy(path_and_filename, dataset_testing_images_folder)
            shutil.copy(file_path + '.txt', dataset_testing_labels_folder)
        else:
            shutil.copy(path_and_filename, dataset_training_images_folder)
            shutil.copy(file_path + '.txt', dataset_training_labels_folder)
    
