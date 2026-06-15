"""Small XML compatibility wrapper around xml.etree.ElementTree."""
from xml.etree.ElementTree import *  # noqa: F401,F403
from xml.etree.ElementTree import Element as _Element
from xml.etree.ElementTree import ParseError as XMLSyntaxError


class LxmlError(Exception):
    pass


def XMLParser(*args, **kwargs):
    from xml.etree.ElementTree import XMLParser as _XMLParser
    return _XMLParser()

