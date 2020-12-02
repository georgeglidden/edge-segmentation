# Summary
from a HS research project. 
a canny bitmap is used to extract contiguous regions as defined by being entirely enclosed by edge pixels. a time complexity of O((a + b)n) is achieved by using node forests and pixel tags to create an equivalent structure to the final result while the image is being iterated. the equivalent structure is then reduced by collapsing node trees from the forest and extracted regions are output as python lists of pixel coordinates. O((a + b)n) where a is the complexity of the edge map, b is the average height of a node tree in the forest, and n is the total number of pixels in the image (width * height). 
# Modules
using numpy, scipy, scikit, and PIL.
