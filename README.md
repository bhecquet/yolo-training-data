# yolo-training-data
data for training yolo model.

Each folder has all data related to the trainig type
- 'field-detector' contains pictures for training yolo model to find text fields, checkbox, ... on a picture

To train model, you can use Google colab with the following code (some steps could be added depending on selected folder

#### 1. See which GPU you get ####
```
import torch
print('PyTorch %s %s' % (torch.__version__, torch.cuda.get_device_properties(0) if torch.cuda.is_available() else 'CPU'))
```

#### 2. Mount the Google drive to store the trained model and retrieve Yolo ####
```
from google.colab import drive
drive.mount('/content/drive')

%cd /content/

# import yolo project
!rm -rf yolov3
!git clone https://github.com/bhecquet/yolov3

# import training data project
!rm -rf yolo-training-data
!git clone https://github.com/bhecquet/yolo-training-data

%cd yolov3
```

#### 3. generate dataset ####

Exemple pour les données "field-detector"
```
# création des données de test / entrainement
!python /content/yolo-training-data/generate_train_files.py /content/yolo-training-data/field-detector/dataset_extracted /content/yolo-training-data/field-detector/dataset_generated_small --output /content/yolov3/dataset
```

#### 4. Train ####

```
import torch
import os
from IPython.display import Image, clear_output 
print('PyTorch %s %s' % (torch.__version__, torch.cuda.get_device_properties(0) if torch.cuda.is_available() else 'CPU'))
best_fitness = 0.0
cfg = '/content/yolo-training-data/field-detector/data/web-generated.yaml'
model = 'yolov3-tiny.pt'

epoch_to_run = 3

name = os.path.basename(cfg).split(".")[0] + '-' + model.split('.')[0]


!python train.py --img 448 --batch 16 --epochs $epoch_to_run --data $cfg --weights $model --name $name --exist-ok 
weights_file_path = '/content/yolov3/runs/train/%s/weights/best.pt' % (name)
w = torch.load(weights_file_path)

fitness = w['best_fitness']
print("epoch completed: " + epoch_to_run)
print("mAp: " + str(fitness))

!cp /content/yolov3/runs/train/{name}/weights/best.pt /content/drive/My\ Drive/best_{name}_{epochs_completed}.pt
```

#### 4. Detect with trained model ####

```
!python3 detect.py  --source "dataset_real/ac3bfc152e8ba5ba0b3423755fe6d234.jpg" --weights /content/drive/My\ Drive/best_web-generated_-1.pt --img-size 640 --exist-ok  --save-txt
```
