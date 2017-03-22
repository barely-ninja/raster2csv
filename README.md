This is a tool to digitize raster graphs using skimage library.

You would need to provide axis description, dataset name, color and position of a representative datapoint to use as deconvolution kernel.
The script will then:
1. extract points with given color to monochrome image
2. deconvolve the monochrome image with kernel sourced on image
3. output linearly adjusted positions of local maxima.
