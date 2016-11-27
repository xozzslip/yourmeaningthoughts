from django.test import TestCase
from img.render import Promo, render

TEXT = r"""Дружба часто заканчивается любовью, но любовь редко заканчивается дружбой """


class TestRender(TestCase):
    def test_render(self):
        for i in range(30):
            p = render(TEXT, 'Наталья Исаева')
            p.image.save('img/content/results/' + p.path.split('/')[-1], 'JPEG')
