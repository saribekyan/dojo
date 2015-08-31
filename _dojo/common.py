import os

import PIL
import PIL.Image

# some global vars
class Common:
    def __init__(self, ni, nr, nc, dh, dw):
        self.n_images = ni
        self.n_rows = nr
        self.n_cols = nc
        self.n_blocks = nr * nc
    
        self.dojo_block_h = dh
        self.dojo_block_w = dw
    
        self.image_height = -1 # don't know yet
        self.image_width  = -1
    
    def all_files(self, path):
        """
        returns all files in the given directory (recursively)
        """
        files = []
        for root, dirnames, filenames in os.walk(path):
            for fname in filenames:
                files.append(os.path.join(root, fname))
    
        print "Found %d files in %s" % (len(files), path)
        if len(files) % self.n_blocks != 0:
            print "WARNING: total number of files is %d, but self.n_blocks is %d" % (len(files), self.n_blocks)
    
        if (self.n_images == -1) or (self.n_images * self.n_blocks > len(files)):
            self.n_images = len(files) / self.n_blocks
    
        files = sorted(files)
    
        grouped_files = []
        for i in xrange(self.n_images):
            grouped_files.append(files[i * self.n_blocks : (i + 1) * self.n_blocks])
        return grouped_files
    
    def stitch_images(self, im_ind, files):
        
        """
        Stitches self.n_rows x self.n_cols images in files together. Assumes 8-bit grayscale.
        """
    
        if len(files) != self.n_rows * self.n_cols:
            print "ERROR: %d has %d files instead of %d" % (im_ind, len(files), self.n_rows * self.n_cols)
            sys.exit(1)
    
        images = []
    
        for i in xrange(len(files)):
            images.append(PIL.Image.open(files[i]))
    
        if self.image_height == -1:
            self.image_height = self.image_width = 0
            for i in xrange(len(files)):
                im = images[i]
    
                # (width, height) = im.size
                if i < self.n_cols:      # first row
                    self.image_width += im.size[0]     # width
    
                if i % self.n_cols == 0: # first column
                    self.image_height += im.size[1]     # height
    
        big_im = PIL.Image.new(images[0].mode, (self.image_width, self.image_height))
    
        curr_h = curr_w = 0
        for i in xrange(len(files)):
            big_im.paste(images[i], (curr_w, curr_h))
            curr_w += images[i].size[0] # width
        
            if (i + 1) % self.n_cols == 0:
                curr_w = 0
                curr_h += images[i].size[1]
    
        return big_im
    
