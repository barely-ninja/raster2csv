from sys import argv
from json import load
import numpy as np
from skimage.io import imread
from skimage.feature import match_template
import matplotlib.pyplot as plt

def find_color(element):
    'Finds series color if distinct from background'
    blank = 255
    return element[np.any(element < blank, axis=2)][0]

def filter_by_color(image, color):
    'Returns b/w image after looking up points with given color'
    zeros = np.zeros_like(image[..., 0], dtype=np.float)
    ones = np.ones_like(image[..., 0], dtype=np.float)
    result = np.where(np.sum(image-color, axis=2) == 0, ones, zeros)
    return result

def main(args):
    'I/O and main loop over data series'
    try:
        cfg_fn = args[1]
    except KeyError:
        print('Please specify configuration file as argument')
    with open(cfg_fn, 'rt') as cfg_file:
        config = load(cfg_file)
    image = imread(config['input_file'])
    for series in config['series']:
        offset = series['element']['size']//2
        x_0, y_0 = series['element']['center']
        element = image[y_0-offset:y_0+offset+1, x_0-offset:x_0+offset+1]
        color = find_color(element)
        kernel = filter_by_color(element, color)
        img_strip = filter_by_color(image, color)
        result = match_template(img_strip, kernel)
        plt.imshow(result, cmap='gray')
        plt.show()

if __name__ == "__main__":
    main(argv)
