from PIL import ImageFont, ImageDraw
from form_generator.tools import get_class_id
from form_generator.Box import Box
import textwrap

class Message:
    
    def __init__(self, width, height, background_color, text, text_color, font):
        self.width = width
        self.height = height
        self.background_color = background_color
        self.text = text
        self.text_color = text_color
        self.font = font
        
        self.overall_width = self.width
        
    def draw(self, x, y, img, image_draw):
        """
        :param x: the x position of the element
        :param y: the y position of the element
        :param img: The image element we are drawing on
        :param image_draw: the PIL ImageDraw object
        """

        text_width, text_height = image_draw.textsize(self.text, self.font)
        
        # change width if its too low
        self.width = max(text_width + 10, self.width)
        self.height = max(text_height + 10, self.height)

        if self.background_color:
            image_draw.line([(x, y), (x + self.width, y)], fill=self.background_color) # top line
            image_draw.line([(x + self.width, y), (x + self.width, y + self.height)], fill=self.background_color) # right line
            image_draw.line([(x, y + self.height), (x + self.width, y + self.height)], fill=self.background_color) # bottom line
            image_draw.line([(x, y), (x, y + self.height)], fill=self.background_color) # left line
        
            ImageDraw.floodfill(img, ((2 * x + self.width) / 2, (2 * y + self.height) / 2), value=self.background_color)
            
        image_draw = ImageDraw.Draw(img)

        image_draw.text((x + (self.width - text_width) / 2, y + (self.height - text_height) / 2), self.text, font=self.font, fill=self.text_color)
        
        return [Box(get_class_id('message'), x - 1, y - 1, self.width + 2, self.height + 2)]
    
    def get_width(self):
        return self.overall_width