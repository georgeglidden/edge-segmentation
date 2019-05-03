import math, random, time
from scipy import ndimage as nd
from skimage import io
from PIL import Image
import numpy as np

def getroot(leaf, tree):
    '''return the lowest member (the 'root') of an element's tree.'''
    root = leaf
    try:
        stem = tree[leaf]
        root = getroot(stem, tree)
    except Exception as e:
        pass
    return root

def linkto(a, b, tree):
    '''linking a to b, where a is greater than b.
    if a is already present in a tree, combine the trees of a and b in descending order;
    a and b are still joined without any duplicates in the tree structure.'''
    leaves = set(tree.values())
    if a in leaves:
        root_a = getroot(a, tree)
        root_b = getroot(b, tree)
        if root_a < root_b:
            tree[root_b] = root_a
        elif root_b < root_a:
            tree[root_a] = root_b
    else:
        tree[a] = b

def pair(a, b, tree):
    '''of a and b, the larger value is paired to the smaller value, and the smaller value is returned.
    if a or b is -1, return -1. this prevents pairing tagged regions (>0) to untagged regions (-1).'''
    smaller = -1
    if a == -1 or b == -1:
        return smaller
    if b > a:
        linkto(b, a, tree)
        smaller = a
    elif a > b:
        linkto(a, b, tree)
        smaller = b
    return smaller

def tag(edgemap):
    '''segments the pixels of an edge bitmap into regions differentiated by contiguous edges.'''
    #edge bitmap
    e = edgemap.copy()
    #tag value map
    r = np.full_like(edgemap, -1)
    #forest
    f = dict()
    
    height, width = e.shape
    #begin tag value at 1, store in tags set.
    current_tag = 1
    tags = set()
    
    #ignore boundary pixels for compatability with canny edge bitmaps
    for m in range(1, width-1):
        #extract line segments separated by edge points in column m
        column = []
        line = []
        for n in range(1, height-1):
            point = (n, m)
            value = e[n, m]
            if value == 0:
                line.append(point)
            elif len(line) > 0:
                column.append(line)
                line = []
        if len(line) > 0:
            column.append(line)
            line = []
        '''for each line segment, increment the current tag value and tag all points rightward
        until an edge point or a tagged point is encountered. if a tagged point is encountered,
        pair that point's tag value with the current_tag value.
        '''
        for line_segment in column:
            init_tag = r[line_segment[0]]
            if init_tag > 0:
                current_tag = init_tag
            else:
                current_tag += 1
                while current_tag in tags:
                    current_tag += 1
                tags.add(current_tag)
            lower_y = line_segment[0][0]
            upper_y = line_segment[len(line_segment)-1][0] + 1
            lower_x = line_segment[0][1]
            for y in range(lower_y, upper_y):
                for x in range(lower_x, width-1):
                    point = (y, x)
                    value = e[y, x]
                    tag = r[y, x]
                    if tag != -1:
                        pair(tag, current_tag, f)
                        break
                    if value != 0:
                        break
                    r[y, x] = current_tag
    #output tag value map and tag tree
    return r, f

def extract_regions(tag_value_map, forest):
    '''outputs the final segmentation result.
    in the tag value map, one region may be tagged with several values all sharing one root in their tag tree.
    this function iterates through the tag value map and, using the getroot function with the tag tree, sorts
    each point an array referenced by its root tag value in a dict, then returns the values (points sorted by tag value)
    as a list datatype.'''
    region_dict = dict()
    height, width = tag_value_map.shape
    #following the same shape requirements as iterating the edge map; the tag value map has null tags (-1) on the boundary pixels.
    for m in range(1, width-1):
        for n in range(1, height-1):
            point = (n, m)
            leaf_value = tag_value_map[n, m]
            root_value = getroot(leaf_value, forest)
            try:
                region_dict[root_value].append(point)
            except KeyError:
                region_dict[root_value] = []
                region_dict[root_value].append(point)
    regions = list(region_dict.values())
    #output array of point values segmented by contiguous edge boundary
    return regions

def render_items(items, dimensions):
    height, width = dimensions
    random.seed()
    render = Image.new('RGB', (width, height))
    for item in items:
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        for point in item:
            y, x = point
            render.putpixel((x, y), (r, g, b))
    return render

def segment_by_edges(edge_bitmap):
    tags, forest = tag(edge_bitmap)
    regions = extract_regions(tags, forest)
    return regions
