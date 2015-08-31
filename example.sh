echo "Intentional error in this script will prevent from running it without looking at the arguments. This is to prevent deleting already generated files. This script is just an example."

pythonERROR run_dojo.py /disk/3d_render_3before_3after_tiles_output_dir \ # images are here
                   NO_SEG \                                          # no segmentation
                   ~/dojo/out \                                      # output file of dojo - quite useless
                   --id p3_10 \         # the id is to identify the generated data easily, just a convenience
                   --n_images 2 \       # the number of images to be processed
                   --n_rows 4 \         # each image is a block 4x3 in p3
                   --n_cols 3 \         # 
                   --dojo_size 16384 \  # height/width of each dojo instance (in this case there will be 12)
                   --force \            # force to erase the data and regenerate it (CAREFUL with this, you might erase already generated data!)
                   --no_seg \           # there is no segmentation
                   --n_dojo_blocks 12   # if --force is not used, provide the number of dojo blocks, because it cannot compute without reading the data

