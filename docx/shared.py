class _Unit(float):
    """Minimal python-docx compatible length stored in English Metric Units."""

    @property
    def emu(self):
        return int(self)

    @property
    def inches(self):
        return float(self) / 914400

    @property
    def pt(self):
        return float(self) / 12700


def Pt(value):
    return _Unit(float(value) * 12700)


def Inches(value):
    return _Unit(float(value) * 914400)


def Emu(value):
    return _Unit(value)


class RGBColor(tuple):
    def __new__(cls, r, g, b):
        return tuple.__new__(cls, (r, g, b))
