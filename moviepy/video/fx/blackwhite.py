import numpy as np

def blackwhite(clip, RGB=None, preserve_luminosity=True):
    """ Desaturates the picture, makes it black and white.
    Parameter RGB allows to set weights for the different color
    channels.
    If RBG is 'CRT_phosphor' a special set of values is used.
    preserve_luminosity maintains the sum of RGB to 1."""
    pass