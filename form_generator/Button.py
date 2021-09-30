from PIL import ImageFont, ImageDraw
from form_generator.tools import get_class_id
from form_generator.Box import Box

class Button:
    
    def __init__(self, width, height, arc_radius, form_background_color, label_inside, label_inside_color, font_size):
        self.width = width
        self.height = height
        self.arc_radius = arc_radius
        self.label_inside = label_inside
        self.label_inside_color = label_inside_color
        self.border_color = form_background_color
        self.background_color = form_background_color
        self.font_size = font_size
        
        self.overall_width = self.width
        
    def draw(self, x, y, img, image_draw):
        """
        :param x: the x position of the element
        :param y: the y position of the element
        :param img: The image element we are drawing on
        :param image_draw: the PIL ImageDraw object
        """
        font_size = int(self.height * self.font_size)
        font = ImageFont.truetype("arial.ttf", font_size)
        
        # box containing arc must be twice the size of the radius
        arc_size_for_corner = self.arc_radius * 2 
        text_width, text_height = image_draw.textsize(self.label_inside, font)
        
        # change width if its too low
        self.width = max(text_width + 10, self.width)

        if self.arc_radius > 0:
            image_draw.arc((x, y, x + arc_size_for_corner, y + arc_size_for_corner), 180, 270, fill=self.border_color)  # top-left
            image_draw.arc((x, y + self.height - arc_size_for_corner, x + arc_size_for_corner, y + self.height), 90, 180, fill=self.border_color) # bottom-left
            image_draw.arc((x + self.width - arc_size_for_corner, y, x + self.width, y + arc_size_for_corner), -90, 0, fill=self.border_color) # top-right
            image_draw.arc((x + self.width - arc_size_for_corner, y + self.height - arc_size_for_corner, x + self.width, y + self.height), 0, 90, fill=self.border_color) # bottom -right
            
        image_draw.line([(x + self.arc_radius, y), (x + self.width - self.arc_radius, y)], fill=self.border_color) # top line
        image_draw.line([(x + self.width, y + self.arc_radius), (x + self.width, y + self.height - self.arc_radius)], fill=self.border_color) # right line
        image_draw.line([(x + self.arc_radius, y + self.height), (x + self.width - self.arc_radius, y + self.height)], fill=self.border_color) # bottom line
        image_draw.line([(x, y + self.arc_radius), (x, y + self.height - self.arc_radius)], fill=self.border_color) # left line
        
        ImageDraw.floodfill(img, ((2 * x + self.width) / 2, (2 * y + self.height) / 2), value=self.background_color)
        image_draw = ImageDraw.Draw(img)

        image_draw.text((x + (self.width - text_width) / 2, y + (self.height - text_height) / 2), self.label_inside, font=font, fill=self.label_inside_color)
        
        return [Box(get_class_id('button'), x - 1, y - 1, self.width + 2, self.height + 2)]
    
    def get_width(self):
        return self.overall_width