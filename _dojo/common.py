import os, errno

import PIL
import PIL.Image

def mkdir_p(path):
    try:
        os.makedirs(path)
        print 'mkdir -p ' + path
        return True

    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            print path + ' exists'
            return False

        else: raise

# some global vars
class Common:
    def __init__(self, ni, nr, nc, ds):
        self.n_images = ni
        self.n_rows = nr
        self.n_cols = nc
        self.n_blocks = nr * nc
    
        self.dojo_block_size = ds
    
        self.image_height = None # don't know yet
        self.image_width  = None

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
    
        if (self.n_images == None) or (self.n_images * self.n_blocks > len(files)):
            self.n_images = len(files) / self.n_blocks
    
        files = sorted(files)
    
        grouped_files = []
        for i in xrange(self.n_images):
            grouped_files.append(files[i * self.n_blocks : (i + 1) * self.n_blocks])
        return grouped_files

    def stitch_images(self, im_ind, files):
        """
        Stitches self.n_rows x self.n_cols images in files together. 
        """
    
        if len(files) != self.n_rows * self.n_cols:
            print "ERROR: %d has %d files instead of %d" % (im_ind, len(files), self.n_rows * self.n_cols)
            sys.exit(1)
    
        images = []
    
        for i in xrange(len(files)):
            images.append(PIL.Image.open(files[i]))
    
        if self.image_height == None:
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

    def num_dojo_blocks(self):
        return ((self.image_height + self.dojo_block_size - 1) / self.dojo_block_size) * ((self.image_width + self.dojo_block_size - 1) / self.dojo_block_size)

    def stitch_and_split(self, im_ind, files):
        big_im = self.stitch_images(im_ind, files)

        self.actual_dojo_size = min(max(self.image_height, self.image_width), self.dojo_block_size)

        curr_h = 0

        dojo_images = []
        while curr_h < self.image_height:
            end_h = curr_h + self.actual_dojo_size
            curr_w = 0
            while curr_w < self.image_width:
                end_w = curr_w + self.actual_dojo_size

                if end_h <= self.image_height and end_w <= self.image_width:
                    im = big_im.crop((curr_w, curr_h, end_w - 1, end_h - 1))
                else:
                    im = PIL.Image.new(big_im.mode, (self.actual_dojo_size, self.actual_dojo_size), "white")
                    im.paste(big_im.crop((curr_w, curr_h, min(end_w, self.image_width) - 1, min(end_h, self.image_height) - 1)), (0, 0))

                dojo_images.append(im)

                curr_w += self.actual_dojo_size

            curr_h += self.actual_dojo_size

        return dojo_images

