'''
Created on 30 sept. 2021

@author: S047432
'''
from PIL import Image
from PIL import ImageDraw

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
