import os
import random
from PIL import Image, ImageFilter, ImageDraw, ImageFont


class Promo:
    RATIO = 16 / 9
    HEIGHT = 500
    WIDTH = int(HEIGHT * RATIO)
    CORNER_OFFSET = 20

    def __init__(self, path):
        self.path = path
        self.image = Image.open(path)
        self.image.convert("RGBA")

        if not self.is_dark():
            self.main_color, self.second_color = ((0, 0, 0), (255, 255, 255))
        else:
            self.main_color, self.second_color = ((255, 255, 255), (0, 0, 0))

    def show(self):
        self.image.show()

    def cut(self):
        width, height = self.image.size
        current_ratio = width / height
        resized_width, resized_height = self.WIDTH, int(self.WIDTH / current_ratio)
        self.image = self.image.resize((resized_width, resized_height))

        if current_ratio < self.RATIO:
            offset = (resized_height - self.HEIGHT) // 2
            self.image = self.image.crop((0, offset, resized_width, resized_height - offset))
        else:
            offset = (resized_width - self.WIDTH) // 2
            self.image = self.image.crop((offset, 0, resized_width - offset, resized_height))

    def blur(self):
        self.image = self.image.filter(ImageFilter.BLUR)

    def is_dark(self):
        colors = self.image.convert("RGB").getcolors(self.HEIGHT * self.WIDTH)
        dark, bright = 0, 0
        for color in colors:
            count, rgb = color
            if sum(rgb) / 3 > 127:
                bright += count
            else:
                dark += count
        return dark > bright

    def draw_borders(self):
        width, height = self.image.size
        left_bottom = (self.CORNER_OFFSET, self.CORNER_OFFSET)
        right_bottom = (width - self.CORNER_OFFSET, self.CORNER_OFFSET)
        left_top = (self.CORNER_OFFSET, height - self.CORNER_OFFSET)
        right_top = (width - self.CORNER_OFFSET, height - self.CORNER_OFFSET)
        borders_width = 1 if self.is_dark() else 2

        draw = ImageDraw.Draw(self.image)
        draw.line(left_bottom + right_bottom, fill=self.main_color, width=borders_width)
        draw.line(left_bottom + left_top, fill=self.main_color, width=borders_width)
        draw.line(right_bottom + right_top, fill=self.main_color, width=borders_width)
        draw.line(right_top + left_top, fill=self.main_color, width=borders_width)

    def draw_text(self, text, font_type):
        draw = ImageDraw.Draw(self.image)
        text_size = self.caclulate_font_size(len(text))
        fnt = ImageFont.truetype(font_type, text_size)
        textsize = draw.multiline_textsize(text, font=fnt)
        width, height = self.image.size
        center = (width // 2, height // 2)

        def draw_shadow(offset=(0, 0)):
            draw.multiline_text((center[0] - textsize[0] // 2 + offset[0],
                                center[1] - textsize[1] // 2 + offset[1]),
                                text=text, font=fnt, fill=self.second_color, align='center')

        borders_offset = [(-1, -1), (-2, -2)]
        for offset in borders_offset:
            draw_shadow(offset)
        draw.multiline_text((center[0] - textsize[0] // 2, center[1] - textsize[1] // 2),
                            text=text, font=fnt, fill=self.main_color, align='center')

    def draw_signature(self, text, font_type):
        SIG_OFFSET = 5
        width, height = self.image.size
        draw = ImageDraw.Draw(self.image)
        fnt = ImageFont.truetype(font_type, 28)
        textsize = draw.multiline_textsize(text, font=fnt)
        rb_corner = (width - self.CORNER_OFFSET, height - self.CORNER_OFFSET)
        signature_pos = (rb_corner[0] - textsize[0] - SIG_OFFSET,
                         rb_corner[1] - textsize[1] - SIG_OFFSET)
        draw.multiline_text((signature_pos[0] - 1, signature_pos[1] - 1),
                            text=text, font=fnt, fill=self.second_color, align='center')
        draw.multiline_text((signature_pos), text=text, font=fnt, fill=self.main_color)

    def save(self):
        path = 'img/content/results/' + self.path.split('/')[-1]
        self.image.save(path, 'JPEG')
        return path

    @classmethod
    def split_to_lines(cls, text):
        words = [word + ' ' for word in text.split()]
        current_line_length = 0
        text = ""
        for word in words:
            text += word
            current_line_length += len(word)
            if current_line_length > 30:
                current_line_length = 0
                text += '\n'
        return text

    @classmethod
    def caclulate_font_size(cls, text_length):
        if text_length > 300:
            return 32
        elif text_length > 200:
            return 34
        elif text_length > 100:
            return 36
        elif text_length > 50:
            return 38
        else:
            return 40


def render(text, signature):
    FONTS_PATH = 'img/content/fonts/'
    IMAGES_PATH = 'img/content/images/'
    os.listdir(FONTS_PATH)
    font_type = FONTS_PATH + random.choice(os.listdir(FONTS_PATH))
    print(font_type)
    background_image = IMAGES_PATH + random.choice(os.listdir(IMAGES_PATH))
    p = Promo(background_image)
    p.cut()
    p.draw_borders()
    p.draw_text(Promo.split_to_lines(text), font_type)
    p.draw_signature(signature, font_type)
    return p
