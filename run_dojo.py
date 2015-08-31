# ./run_dojo.py data_id path/to/original_images path/to/segmentation/images path/to/output/folder port
#   A temporary folder data will be created

import os, errno
import os.path
import sys
import glob
import random
import shutil

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

if __name__ == '__main__':
    parser = OptionParser("Usage: %prog ORIGINAL/IMAGES/DIR SEGMENTATAION/IMAGES/DIR OUTPUT/DIR [options]")

    if len(sys.argv) < 4:
        parser.print_help()
        sys.exit(1)

    orig_images_dir = os.path.abspath(sys.argv[1])
    seg_images_dir  = os.path.abspath(sys.argv[2])
    out_dir = os.path.abspath(sys.argv[3])

    parser.add_option("--id", dest="data_id", default=("dojo_%03d" % random.randint(0, 999)), help="the id of this data (anything)")
    parser.add_option("--n_images", dest="n_images", type="int", default=-1, help="process only first n_images images, -1 means all")
    parser.add_option("--n_rows", dest="n_rows", type="int", default=1, help="number of rows of blocks that each image is part of")
    parser.add_option("--n_cols", dest="n_cols", type="int", default=1, help="number of cols of blocks that each image is part of")
    parser.add_option("--port", dest="port", type="int", default=1993, help="the port of dojo")
    parser.add_option("--orphans", dest="detect_orphans", action="store_true", help="detects orphans")
    parser.add_option("--force", dest="force", action="store_true", help="if set, will rewrite all the files")

    args, opts = parser.parse_args()

    d = vars(args)
    for key, val in d.items():
        exec(key + '=val')
    
    if detect_orphans == None:
        detect_orphans = False

    print "Starting Dojo with arguments"
    print args
    print opts
    print

    # where all the data will be stored for this execution. So this folder has to contain images and ids subfolders (mojo format).
    mojo_dir = os.path.join(os.path.expanduser('~'), 'dojo', 'data', data_id)     

    print "The Mojo filesystem: " + mojo_dir

    if force:
        if os.path.exists(mojo_dir):
            shutil.rmtree(mojo_dir)
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)

    if mkdir_p(os.path.join(mojo_dir, 'images')):
#       orig_images_dir, ext = convert_if_needed(orig_images_dir, data_dir + '/orig')
        _dojo.image_tile_calculator.run(orig_images_dir, mojo_dir, n_images, n_rows, n_cols)
    else:
        print "    Images folder already existes"

    if mkdir_p(os.path.join(mojo_dir, 'ids')):
#        seg_images_dir, ext = convert_if_needed(seg_images_dir,  data_dir + '/seg')
        _dojo.segmentation_tile_calculator.run(seg_images_dir, mojo_dir, n_images, n_rows, n_cols)
    else:
        print "    Ids folder already exists"

    mkdir_p(out_dir)
    print "Results saved in " + out_dir

    logic = dojo.ServerLogic()
    logic.run(mojo_dir, out_dir, port, detect_orphans, configured=True)

