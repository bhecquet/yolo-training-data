from PIL import ImageDraw
import random
from form_generator.tools import generate_darker_color, get_class_id
from form_generator.Box import Box
class Checkbox:
    
    def __init__(self, width, arc_radius, border_color, label, label_color, font, background_color, checked=False, check_color=(0, 0, 0), text_after=True):
        self.width = width
        self.height = width
        self.arc_radius = arc_radius
        self.label = label
        self.label_color = label_color
        self.border_color = border_color
        self.background_color = background_color
        self.font = font
        self.checked = checked
        self.check_color = check_color
        self.text_after = text_after
        
    def get_dimensions(self, image_draw):
        label_width, label_height = image_draw.textsize(self.label, self.font)
        overall_width = label_width + 5 + self.width
        
        return label_width, label_height, overall_width
        
    def draw(self, x, y, img, image_draw):
        # compute size of the field
        label_width, label_height, self.overall_width = self.get_dimensions(image_draw)

        if self.text_after:
            field_x = self._draw_box(image_draw, img, x, y, 0)
            self._write_text(image_draw, label_height, x + 5 + self.width, y)
        else:
            field_x = self._draw_box(image_draw, img, x, y, label_width + 5)
            self._write_text(image_draw, label_height, x, y)
        
        if self.checked:
            start_point1 = (field_x + 1, y + self.height / 2)
            end_point1 = (field_x + self.width / 2, y + self.height - 2)
            end_point2 = (field_x + self.width - 1, y + 1)
            image_draw.line([start_point1, end_point1, end_point2], fill=self.check_color, width=2)
            
            
        return [Box(get_class_id('checkbox'), field_x - 1, y - 1, self.width + 2, self.height + 2), 
                Box(get_class_id('checkbox_with_label'), x - 2, y - 2, self.overall_width + 2, max(label_height, self.height + 4))]
    
    def _draw_box(self, image_draw, img, x, y, label_width):
        # box containing arc must be twice the size of the radius
        arc_size_for_corner = self.arc_radius * 2 
    
        field_x = x + label_width

        if self.arc_radius > 0:
            image_draw.arc((field_x, y, field_x + arc_size_for_corner, y + arc_size_for_corner), 180, 270, fill=self.border_color)  # top-left
            image_draw.arc((field_x, y + self.height - arc_size_for_corner, field_x + arc_size_for_corner, y + self.height), 90, 180, fill=self.border_color) # bottom-left
            image_draw.arc((field_x + self.width - arc_size_for_corner, y, field_x + self.width, y + arc_size_for_corner), -90, 0, fill=self.border_color) # top-right
            image_draw.arc((field_x + self.width - arc_size_for_corner, y + self.height - arc_size_for_corner, field_x + self.width, y + self.height), 0, 90, fill=self.border_color) # bottom -right
            
        image_draw.line([(field_x + self.arc_radius, y), (field_x + self.width - self.arc_radius, y)], fill=self.border_color) # top line
        image_draw.line([(field_x + self.width, y + self.arc_radius), (field_x + self.width, y + self.height - self.arc_radius)], fill=self.border_color) # right line
        image_draw.line([(field_x + self.arc_radius, y + self.height), (field_x + self.width - self.arc_radius, y + self.height)], fill=self.border_color) # bottom line
        image_draw.line([(field_x, y + self.arc_radius), (field_x, y + self.height - self.arc_radius)], fill=self.border_color) # left line
        
        
        ImageDraw.floodfill(img, ((2 * field_x + self.width) / 2, (2 * y + self.height) / 2), value=self.background_color)
        return field_x
    
    def _write_text(self, image_draw, label_height, x, y):
        image_draw.text((x, y + (self.height - label_height) / 2), self.label, font=self.font, fill=self.label_color)
        
    
    def get_width(self):
        return self.overall_width
        
class CheckboxGroup:
    """
    Group of check boxes
    """
    
    def __init__(self, width, arc_radius, border_color, labels, label_color, font, background_color, checked=False, vertical_layout=True):

        self.vertical_layout = vertical_layout
        
        self.width = width
        self.arc_radius = arc_radius
        self.labels = labels
        self.label_color = label_color
        self.border_color = border_color
        self.background_color = background_color
        self.font = font
        
    def draw(self, form, row_id, y_offset):
        
        check_color = generate_darker_color(self.border_color, 50)
        if random.choice([True, False]):
            check_color = (0, 0, 0)
        
        
        x = 10
        coordinates = []
        for label in self.labels:
            
            checkbox = Checkbox(self.width, 
                                self.arc_radius, 
                                self.border_color, 
                                label, 
                                self.label_color, 
                                self.font, 
                                self.background_color,
                                check_color=check_color,
                                checked=random.choice([True, False]))
            label_width, label_height, overall_width = checkbox.get_dimensions(form.img_draw)
            
            if (x + overall_width < form.width):
                coordinates += form.draw(x, checkbox, row_id, y_offset)
                x += checkbox.get_width() + 20
            else:
                print("No space to draw checkbox")
            
        return coordinates