class _Unit(float):
    pass


def Pt(value):
    return _Unit(value)


def Inches(value):
    return _Unit(value)


def Emu(value):
    return _Unit(value)


class RGBColor(tuple):
    def __new__(cls, r, g, b):
        return tuple.__new__(cls, (r, g, b))

