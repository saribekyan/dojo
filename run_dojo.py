# ./run_dojo.py data_id path/to/original_images path/to/segmentation/images path/to/output/folder port
#   A temporary folder data will be created

import os, errno
import os.path
import sys
import glob
import cv2
import random

from optparse import OptionParser

import _dojo

import dojo

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

def print_help():
    print
    print "usage: id path/to/original/images path/to/segmentation/images path/to/output/folder port"
    print
    print

def convert_if_needed(images_dir, output_dir):
    # if needed convert and move the images in images_dir to data_dir

    files = sorted( glob.glob( images_dir + '/*') )
    f = files[0]

    fname, ext = os.path.splitext(f)
    ext = ext[1:]

    im = cv2.imread(f)
    if len(im.shape) == 2 or ((im[..., 0] == im[..., 1]) & (im[..., 1] == im[..., 2])).all():
        print 'data already in correct format'
        return images_dir, ext

    if not mkdir_p(output_dir): # the directory was already there
        print 'data was already converted'
        return output_dir, ext

    for f in files:
        print f
        im = cv2.imread(f)
        im = im[..., 0] + im[..., 1] * 256 + im[..., 2] * 256 * 256
        cv2.imwrite(output_dir + '/' + os.path.basename(f), im)

    return output_dir, ext

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-i", "--id", dest="data_id", help="REQURIRED: the id of this data (anything)")
    parser.add_option("-e", "--orig_images", dest="orig_images_dir", help="REQURIRED: the directory that contains original images")
    parser.add_option("-s", "--seg_images", dest="seg_images_dir", help="REQUIRED: the directory that contains segmented images")
    parser.add_option("-o", "--out_images", dest="output_dir", help="REQUIRED: the directory that will contain the output images")
    parser.add_option("-p", "--port", dest="port", type="int", help="the port of dojo")
    parser.add_option("-d", "--orphans", dest="detect_orphans", action="store_true", help="detecs orphans")

    args, opts = parser.parse_args()

    d = vars(args)
    for key, val in d.items():
        exec(key + '=val')

    if data_id == None or orig_images_dir == None or seg_images_dir == None or output_dir == None:
        print 'Options -i -e -s -o are required. See help'
        sys.exit(1)

    if port == None:
        port = random.randint(5000, 6000)

    if detect_orphans == None:
        detect_orphans = False

    data_dir = os.path.abspath('data/' + data_id)   # directory where the images for this execution will be stored.

    mojo_dir = data_dir + '/mojo'
    
    if mkdir_p(mojo_dir):

        orig_images_dir, ext = convert_if_needed(orig_images_dir, data_dir + '/orig')
        _dojo.image_tile_calculator.run(orig_images_dir, data_dir + '/mojo', ext)

        seg_images_dir, ext = convert_if_needed(seg_images_dir,  data_dir + '/seg')
        _dojo.segmentation_tile_calculator.run(seg_images_dir, mojo_dir, ext)

    logic = dojo.ServerLogic()
    logic.run(mojo_dir, output_dir, port, detect_orphans, configured=True)

