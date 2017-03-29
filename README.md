This is a tool to digitize raster graphs using skimage library. It should be useful when data markers overlap on image and manual separation is difficult.

In config JSON file you would need to provide axis dimensions, and for each data series the position of a datapoint to use as template directly on image. The script will then:

1. Source datapoint template from given region, find its color
2. Extract points with given color to monochrome image
3. Run correlation-based template matching over monochrome image
4. Output linearly adjusted positions of local correlation maxima.

This particular dataset consists of two images embedded in 'The Use of Burst Frequency Offsets in the Search
for MH370' paper by Holland on page 7. A small merge utility included to combine data from two images.
