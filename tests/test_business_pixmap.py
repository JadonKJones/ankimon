from Ankimon.business import resize_pixmap_img


class FakePixmap:
    def __init__(self, width, height):
        self._width = width
        self._height = height
        self.scaled_args = None

    def width(self):
        return self._width

    def height(self):
        return self._height

    def scaled(self, width, height):
        self.scaled_args = (width, height)
        return (width, height)


def test_resize_pixmap_returns_null_pixmap_unchanged():
    pixmap = FakePixmap(0, 0)

    result = resize_pixmap_img(pixmap, 150)

    assert result is pixmap
    assert pixmap.scaled_args is None


def test_resize_pixmap_preserves_aspect_ratio():
    pixmap = FakePixmap(96, 48)

    result = resize_pixmap_img(pixmap, 150)

    assert result == (150, 75)
    assert pixmap.scaled_args == (150, 75)
