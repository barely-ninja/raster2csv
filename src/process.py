from sys import argv
from json import load
import numpy as np
from skimage.io import imread
from skimage.feature import peak_local_max, match_template
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
    x_ign = config['ignore']['x']
    y_ign = config['ignore']['y']
    px_x = config['x_axis']['pixels']
    px_y = config['y_axis']['pixels']
    u_x = config['x_axis']['shown_units']
    u_y = config['y_axis']['shown_units']

    pix_offset = np.array([px_y[0], px_x[0]])
    units_offset = np.array([u_y[0], u_x[0]])
    pix_scale = np.array([(u_y[1]-u_y[0])/(px_y[1]-px_y[0]),
                          (u_x[1]-u_x[0])/(px_x[1]-px_x[0])])
    for series in config['series']:
        offset = series['element']['size']//2
        x_0, y_0 = series['element']['center']
        element = image[y_0-offset:y_0+offset+1, x_0-offset:x_0+offset+1]
        color = find_color(element)
        kernel = filter_by_color(element, color)
        img_strip = filter_by_color(image, color)

        result = match_template(img_strip, kernel, pad_input=True)

        res_mask = np.ones_like(result, dtype=np.bool)
        try:
            x_lim = config['x_limits']
        except KeyError:
            x_lim = [px_x[0]-offset-1, px_x[1]+offset]
        try:
            series_range = series['y_range']
            res_mask[series_range[1]:series_range[0], x_lim[0]:x_lim[1]] = False
        except KeyError:
            res_mask[px_y[1]:px_y[0], x_lim[0]:x_lim[1]] = False
        res_mask[y_ign[0]:y_ign[1], x_ign[0]:x_ign[1]] = True
        masked_result = np.ma.masked_array(result, mask=res_mask)

        coords = peak_local_max(masked_result, min_distance=1, threshold_rel=0.5, num_peaks=15)

        try:
            manual_picks = np.array([[x[1], x[0]] for x in series['manual']])
            coords = np.append(coords, manual_picks, axis=0)
        except KeyError:
            pass
        out_fn = config['output_prefix']+'_'.join(series['name'].split(' '))
        if config['debug'] == "yes":
            xvals = coords[:, 1]
            yvals = coords[:, 0]
            pad = 20
            plt.plot(xvals, yvals, 'g+', markersize=20)
            plt.imshow(image)
            #plt.imshow(masked_result, cmap='gray')
            plt.xlim([xvals.min()-pad, xvals.max()+pad])
            plt.ylim([yvals.max()+pad, yvals.min()-pad])
            plt.savefig(out_fn+'.png')
            plt.close()

        scaled = (coords-pix_offset)*pix_scale + units_offset
        order = np.argsort(scaled[:, 1])
        np.savetxt(out_fn+'.tsv', list(zip(scaled[order, 1], scaled[order, 0])), '%.2f', '\t')

if __name__ == "__main__":
    main(argv)
