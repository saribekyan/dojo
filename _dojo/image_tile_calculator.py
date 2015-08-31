import os
import sys
import string
import math
import PIL
import PIL.Image
import lxml
import lxml.etree
import glob
import numpy as np

import Image
import common

def run(input_dir, output_dir, common_state):

    print input_dir
    print output_dir

    tile_num_pixels_y = 512
    tile_num_pixels_x = 512

    original_input_images_path = input_dir
    output_image_extension     = '.tif'
    image_resize_filter        = PIL.Image.ANTIALIAS

    files = common_state.all_files(input_dir)

    tile_index_z = 0

    for im_ind in xrange(len(files)):

        dojo_images = common_state.stitch_and_split(im_ind, files[im_ind])

        if im_ind == 0: # now we know the size of the image, we can create appropriate folders
            num_dojo_blocks = common_state.num_dojo_blocks()
            for i in xrange(num_dojo_blocks):
                common.mkdir_p(os.path.join(output_dir, '%02d' % i))

        for i in xrange(len(dojo_images)):
            output_tile_image_path = os.path.join(output_dir, '%02d' % i, 'images', 'tiles')

            original_image = dojo_images[i]
            ( original_image_num_pixels_x, original_image_num_pixels_y ) = original_image.size

            current_image_num_pixels_y = original_image_num_pixels_y
            current_image_num_pixels_x = original_image_num_pixels_x
            current_tile_data_space_y  = tile_num_pixels_y
            current_tile_data_space_x  = tile_num_pixels_x
            tile_index_w               = 0

            while current_image_num_pixels_y > tile_num_pixels_y / 2 or current_image_num_pixels_x > tile_num_pixels_x / 2:
                
                current_tile_image_path    = os.path.join(output_tile_image_path, 'w=' + '%08d' % ( tile_index_w ), 'z=' + '%08d' % ( tile_index_z ))

                common.mkdir_p( current_tile_image_path )

                current_image = original_image.resize( ( current_image_num_pixels_x, current_image_num_pixels_y ), image_resize_filter )            
                
                num_tiles_y = int( math.ceil( float( current_image_num_pixels_y ) / tile_num_pixels_y ) )
                num_tiles_x = int( math.ceil( float( current_image_num_pixels_x ) / tile_num_pixels_x ) )

                for tile_index_y in range( num_tiles_y ):
                    for tile_index_x in range( num_tiles_x ):

                        y = tile_index_y * tile_num_pixels_y
                        x = tile_index_x * tile_num_pixels_x

                        current_tile_image_name = os.path.join(current_tile_image_path, 'y=' + '%08d' % ( tile_index_y ) + ','  + 'x=' + '%08d' % ( tile_index_x ) + output_image_extension)

                        tile_image = current_image.crop( ( x, y, x + tile_num_pixels_x, y + tile_num_pixels_y ) )     
                        tile_image.save( current_tile_image_name )
                        print current_tile_image_name
                        
                current_image_num_pixels_y = current_image_num_pixels_y / 2
                current_image_num_pixels_x = current_image_num_pixels_x / 2
                current_tile_data_space_y  = current_tile_data_space_y  * 2
                current_tile_data_space_x  = current_tile_data_space_x  * 2
                tile_index_w               = tile_index_w + 1
                
        tile_index_z = tile_index_z + 1

        #if tile_index_z >= nimages_to_process:
        #    break

    for i in xrange(num_dojo_blocks):
        #Output TiledVolumeDescription xml file
        tiledVolumeDescription = lxml.etree.Element( "tiledVolumeDescription",
            fileExtension = output_image_extension[1:],
            numTilesX = str( int( math.ceil( original_image_num_pixels_x / tile_num_pixels_x ) ) ),
            numTilesY = str( int( math.ceil( original_image_num_pixels_y / tile_num_pixels_y ) ) ),
            numTilesZ = str( tile_index_z ),
            numTilesW = str( tile_index_w ),
            numVoxelsPerTileX = str( tile_num_pixels_x ),
            numVoxelsPerTileY = str( tile_num_pixels_y ),
            numVoxelsPerTileZ = str( 1 ),
            numVoxelsX = str( original_image_num_pixels_x ),
            numVoxelsY = str( original_image_num_pixels_y ),
            numVoxelsZ = str( tile_index_z ),
            dxgiFormat = 'R8_UNorm',
            numBytesPerVoxel = str( 1 ),      
            isSigned = str( False ).lower() )
    
        output_tile_volume_file = os.path.join(output_dir, '%02d' % i, 'images', 'tiledVolumeDescription.xml')
        with open( output_tile_volume_file, 'w' ) as file:
            file.write( lxml.etree.tostring( tiledVolumeDescription, pretty_print = True ) )

if __name__ == '__main__':
    run('/home/hayks/Dropbox/RDExtendLeft/orig_images/', '/home/hayks/Dropbox/tmp', 'png')

