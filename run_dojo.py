# ./run_dojo.py data_id path/to/original_images path/to/segmentation/images path/to/output/folder port
#   A temporary folder data will be created

import os
import os.path
import sys
import glob
import random
import shutil

from optparse import OptionParser

import _dojo

import dojo

from _dojo import common
from _dojo.common import Common

from multiprocessing import Process

if __name__ == '__main__':
    parser = OptionParser("Usage: %prog ORIGINAL/IMAGES/DIR SEGMENTATAION/IMAGES/DIR OUTPUT/DIR [options]")

    parser.add_option("--id", dest="data_id", default="000", help="the id of this data (anything) [default: %default]")
    parser.add_option("--n_images", dest="n_images", type="int", default=-1, help="process only first n_images images, -1 means all [default: %default]")
    parser.add_option("--n_rows", dest="n_rows", type="int", default=1, help="number of rows of blocks that each image is part of [default: %default]")
    parser.add_option("--n_cols", dest="n_cols", type="int", default=1, help="number of cols of blocks that each image is part of [default: %default]")
    parser.add_option("--dojo_size", dest="dojo_size", type="int", default=2048, help="height/width of each dojo instance. [default: %default]")
    parser.add_option("--port", dest="port", type="int", default=1993, help="the starting port of dojo executions [default: %default]")
    parser.add_option("--force", dest="force", action="store_true", default=False, help="if set, will rewrite all the files")
    parser.add_option("--n_dojo_blocks", dest="num_dojo_blocks", type="int", default=-1,
            help="number of dojo blocks, if mojo data is already generated [default: %default]")
    parser.add_option("--no_seg", dest="no_segmentation", action="store_true", default=False,
            help="if set, will assume that there is not segmentation and use one label instead; in this case the second argument is ignored.")
    parser.add_option("--orphans", dest="detect_orphans", action="store_true", default=False, help="detects orphans")
    parser.add_option("--only_gen", dest="only_gen", action="store_true", default=False, help="if set only generates the data without running dojo")

    if len(sys.argv) < 4:
        parser.print_help()
        sys.exit(1)

    orig_images_dir = os.path.abspath(sys.argv[1])
    seg_images_dir  = os.path.abspath(sys.argv[2])
    out_dir = os.path.abspath(sys.argv[3])

    args, opts = parser.parse_args()

    d = vars(args)
    for key, val in d.items():
        exec(key + '=val')
    
    print "Starting Dojo with arguments"
    print args
    print opts
    print

    # where all the data will be stored for this execution. So this folder has to contain images and ids subfolders (mojo format).
    mojo_dir = os.path.join(os.path.expanduser('~'), 'dojo', 'data', data_id)     

    print "The Mojo filesystem: " + mojo_dir

    # do we delete everything or the data there can be used?
    if force:
        if os.path.exists(mojo_dir):
            shutil.rmtree(mojo_dir)

    # a variable that holds common imformation
    common_state = Common(n_images, n_rows, n_cols, dojo_size)

    # generate image tiles
    if common.mkdir_p(os.path.join(mojo_dir, '00', 'images')):
        _dojo.image_tile_calculator.run(orig_images_dir, mojo_dir, common_state)
    else:
        print "    Images folder already existes"

    # generate segmentation tiles
    if common.mkdir_p(os.path.join(mojo_dir, '00', 'ids')):
        _dojo.segmentation_tile_calculator.run(seg_images_dir, mojo_dir, common_state, no_segmentation)
    else:
        print "    Ids folder already exists"

    if only_gen:
        sys.exit(0)

    if common_state.image_height != None:
        num_dojo_blocks = common_state.num_dojo_blocks()

    for i in xrange(num_dojo_blocks):
        common.mkdir_p(os.path.join(out_dir, '%02d' % i))

    print "Results will be saved in " + out_dir
    
    def parallel_server(id):
        logic = dojo.ServerLogic()
        logic.run(os.path.join(mojo_dir, '%02d' % id), os.path.join(out_dir, '%02d' % id), port + id, detect_orphans, configured=True)

    processes = []
    for i in xrange(num_dojo_blocks):
        print "Starting %d" % i
        p = Process(target = parallel_server, args=(i, ))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

