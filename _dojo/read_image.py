import os

import PIL
import PIL.Image

def all_files(path, n_images, n_blocks):
    """
    returns all files in the given directory (recursively)
    """
    files = []
    for root, dirnames, filenames in os.walk(path):
        for fname in filenames:
            files.append(os.path.join(root, fname))

    print "Found %d files in %s" % (len(files), path)
    if len(files) % n_blocks != 0:
        print "WARNING: total number of files is %d, but n_blocks is %d" % (len(files), n_blocks)

    if (n_images == -1) or (n_images * n_blocks > len(files)):
        n_images = len(files) / n_blocks

    files = sorted(files)

    grouped_files = []
    for i in xrange(n_images):
        grouped_files.append(files[i * n_blocks : (i + 1) * n_blocks])
    return grouped_files

def stitch_images(im_ind, files, n_rows, n_cols):
    """
    Stitches n_rows x n_cols images in files together. Assumes 8-bit grayscale.
    """

    if len(files) != n_rows * n_cols:
        print "ERROR: %d has %d files instead of %d" % (im_ind, len(files), n_rows * n_cols)
        sys.exit(1)

    images = []

    H = W = 0
    for i in xrange(len(files)):
        im = PIL.Image.open(files[i])
        images.append(im)

        # (width, height) = im.size
        if i < n_cols:      # first row
            W += im.size[0]     # width

        if i % n_cols == 0: # first column
            H += im.size[1]     # height

    big_im = PIL.Image.new(im.mode, (W, H))

    curr_h = curr_w = 0
    for i in xrange(len(files)):
        big_im.paste(images[i], (curr_w, curr_h))
        curr_w += im.size[0] # width
    
        if (i + 1) % n_cols == 0:
            curr_w = 0
            curr_h += im.size[1]

    return big_im

