This folder contains all pictures and configuration for training a Yolo model to detect fields (text fields, checkbox, ...) on a picture

- `generate-html.py` is a script that generates forms (see below)
- `convert_pascalvoc_to_yolo.py` from `dataset_real` folder, generate small pictures
- `dataset_real` contains all pictures get from web 
- `dataset_extracted` is the extraction of smaller pictures from `dataset_real` so that training does not consume too much GPU memory. It's based on zones called '_form_' which contain some fields. Each form will be about 400x400 pixels

## Generate small pictures ##

If you give big pictures to training, algorithm will resize them and detection will be bad. So we crop pictures around forms. To do so, while annotating the pictures with `labelImg`we add a `_form_` class that is used to delimit parts of form.
There may be several `_form_` for a single picture

### Generation ###

`python convert_pascalvoc_to_yolo.py dataset_real dataset_extracted`

## Generate forms ##

`generate-html.py` script will create pictures with various forms so that training can be more accurate

### Configuration ###

Install requirements with `pip install -r requirements.txt`

### Generation ###

To generate file, execute `python generate-html.py data/web-generated.names`

Content of `data/web-generated.names` is the list of class names in the same order as what we have in `data/web-generated.yaml`
