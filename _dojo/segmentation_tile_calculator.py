import os
import sys
import string
import math
import mahotas
import PIL
import PIL.Image
import numpy as np
import scipy
import scipy.io
# import cv2
import h5py
import lxml
import lxml.etree
import glob
import sqlite3
import colorsys

import common

def run(input_dir, output_dir, common_state, no_segmentation):

    tile_num_pixels_y             = 512
    tile_num_pixels_x             = 512
    ncolors                       = 1000

    def save_hdf5( file_path, dataset_name, array ):
        
        hdf5             = h5py.File( file_path, 'w' )
        dataset          = hdf5.create_dataset( dataset_name, data=array )
        hdf5.close()

        print file_path
        print

    def load_id_image ( file_list ): # file_list is a list of files that needs to be stitched together (n_rows x n_cols)
        print file_list

        dojo_images = common_state.stitch_and_split(-1, file_list)
        ids_list = [np.array(d_im) for d_im in dojo_images]

        if len( ids_list[0].shape ) == 3:
            ids_list = [np.array(ids, dtype='int32') for ids in ids_list]
            ids_list = [ids[..., 0] + ids[..., 1] * 256 + ids[..., 2] * 256 * 256 for ids in ids_list]

        return ids_list

    if not no_segmentation:
        files_lists = common_state.all_files(input_dir)

        if len(files_lists) > 0:

            tile_index_z         = 0

            # Make a color map
            color_map = np.zeros( (ncolors + 1, 3), dtype=np.uint8 );
            for color_i in xrange( 1, ncolors + 1 ):
                rand_vals = np.random.rand(3);
                color_map[ color_i ] = [ rand_vals[0]*255, rand_vals[1]*255, rand_vals[2]*255 ];

            num_dojo_blocks = None
            for files in files_lists:

                original_ids_list = load_id_image( files )

                if num_dojo_blocks == None:
                    num_dojo_blocks = common_state.num_dojo_blocks()
                    for i in xrange(num_dojo_blocks):
                        common.mkdir_p(os.path.join(output_dir, '%02d' % i))
               
                for i in xrange(num_dojo_blocks):
                    original_ids = original_ids_list[i]
                    current_image_counts = np.bincount( original_ids.ravel() )
                    current_image_counts_ids = np.nonzero( current_image_counts )[0]
                    current_max = np.max( current_image_counts_ids )
                    
                    ( original_image_num_pixels_x, original_image_num_pixels_y ) = original_ids.shape

                    current_image_num_pixels_y = original_image_num_pixels_y
                    current_image_num_pixels_x = original_image_num_pixels_x
                    current_tile_data_space_y  = tile_num_pixels_y
                    current_tile_data_space_x  = tile_num_pixels_x
                    tile_index_w               = 0
                    ids_stride                 = 1
                    
                    while current_image_num_pixels_y > tile_num_pixels_y / 2 or current_image_num_pixels_x > tile_num_pixels_x / 2:

                        current_tile_ids_path = os.path.join(output_dir, '%02d' % i, 'ids', 'tiles', 'w=' + '%08d' % ( tile_index_w ), 'z=' + '%08d' % ( tile_index_z ))

                        common.mkdir_p( current_tile_ids_path )

                        current_ids = original_ids[ ::ids_stride, ::ids_stride ]
                        
                        num_tiles_y = int( math.ceil( float( current_image_num_pixels_y ) / tile_num_pixels_y ) )
                        num_tiles_x = int( math.ceil( float( current_image_num_pixels_x ) / tile_num_pixels_x ) )

                        for tile_index_y in range( num_tiles_y ):
                            for tile_index_x in range( num_tiles_x ):

                                y = tile_index_y * tile_num_pixels_y
                                x = tile_index_x * tile_num_pixels_x
                                
                                current_tile_ids_name = os.path.join(current_tile_ids_path, 'y=' + '%08d' % ( tile_index_y ) + ','  + 'x=' + '%08d' % ( tile_index_x ) + '.hdf5')
                                
                                tile_ids                                                                   = np.zeros( ( tile_num_pixels_y, tile_num_pixels_x ), np.uint32 )
                                tile_ids_non_padded                                                        = current_ids[ y : y + tile_num_pixels_y, x : x + tile_num_pixels_x ]
                                tile_ids[ 0:tile_ids_non_padded.shape[0], 0:tile_ids_non_padded.shape[1] ] = tile_ids_non_padded[:,:]
                                save_hdf5( current_tile_ids_name, 'IdMap', tile_ids )

                        current_image_num_pixels_y = current_image_num_pixels_y / 2
                        current_image_num_pixels_x = current_image_num_pixels_x / 2
                        current_tile_data_space_y  = current_tile_data_space_y  * 2
                        current_tile_data_space_x  = current_tile_data_space_x  * 2
                        tile_index_w               = tile_index_w               + 1
                        ids_stride                 = ids_stride                 * 2
                        
                tile_index_z = tile_index_z + 1

            print 'Writing colorMap file (hdf5)'

            for i in xrange(num_dojo_blocks):
                output_color_map_file = os.path.join(output_dir, '%02d' % i, 'ids', 'colorMap.hdf5')
                hdf5             = h5py.File( output_color_map_file, 'w' )
                hdf5['idColorMap'] = color_map
                hdf5.close()

    else:
        print "AAAAAAAAAAAAAAAAAAAAA"
        tile_index_z         = 0

        num_dojo_blocks = common_state.num_dojo_blocks()

        dummy_tile = np.ones( (tile_num_pixels_x, tile_num_pixels_y), np.int32)
        dummy_tile_path = os.path.join(output_dir, 'dummy_tile.hdf5')
        save_hdf5(dummy_tile_path, 'IdMap', dummy_tile)

        for dummy_file in xrange(common_state.n_images):
            for i in xrange(num_dojo_blocks):
                
                current_image_num_pixels_y = common_state.actual_dojo_size
                current_image_num_pixels_x = common_state.actual_dojo_size

                current_tile_data_space_y  = tile_num_pixels_y
                current_tile_data_space_x  = tile_num_pixels_x

                tile_index_w               = 0
                ids_stride                 = 1
                
                while current_image_num_pixels_y > tile_num_pixels_y / 2 or current_image_num_pixels_x > tile_num_pixels_x / 2:

                    current_tile_ids_path = os.path.join(output_dir, '%02d' % i, 'ids', 'tiles', 'w=' + '%08d' % ( tile_index_w ), 'z=' + '%08d' % ( tile_index_z ))

                    common.mkdir_p( current_tile_ids_path )

                    num_tiles_y = int( math.ceil( float( current_image_num_pixels_y ) / tile_num_pixels_y ) )
                    num_tiles_x = int( math.ceil( float( current_image_num_pixels_x ) / tile_num_pixels_x ) )

                    for tile_index_y in range( num_tiles_y ):
                        for tile_index_x in range( num_tiles_x ):

                            y = tile_index_y * tile_num_pixels_y
                            x = tile_index_x * tile_num_pixels_x
                            
                            current_tile_ids_name = os.path.join(current_tile_ids_path, \
                                                                'y=' + '%08d' % ( tile_index_y ) + ','  + 'x=' + '%08d' % ( tile_index_x ) + '.hdf5')

                            os.symlink(dummy_tile_path, current_tile_ids_name)
                            #save_hdf5( current_tile_ids_name, 'IdMap', tile_ids )

                    current_image_num_pixels_y = current_image_num_pixels_y / 2
                    current_image_num_pixels_x = current_image_num_pixels_x / 2
                    current_tile_data_space_y  = current_tile_data_space_y  * 2
                    current_tile_data_space_x  = current_tile_data_space_x  * 2
                    tile_index_w               = tile_index_w               + 1
                    ids_stride                 = ids_stride                 * 2
                    
            tile_index_z = tile_index_z + 1

        print 'Writing colorMap file (hdf5)'

        # Make a color map
        color_map = np.zeros( (ncolors + 1, 3), dtype=np.uint8 );
        color_map[1] = 1

        for i in xrange(num_dojo_blocks):
            output_color_map_file = os.path.join(output_dir, '%02d' % i, 'ids', 'colorMap.hdf5')
            hdf5             = h5py.File( output_color_map_file, 'w' )
            hdf5['idColorMap'] = color_map
            hdf5.close()

        print 'NOT Writing segmentInfo file (sqlite)'

        for i in xrange(num_dojo_blocks):
            print 'Writing TiledVolumeDescription file'

            tiledVolumeDescription = lxml.etree.Element( "tiledVolumeDescription",
                fileExtension = "hdf5",
                numTilesX = str( int( math.ceil( common_state.actual_dojo_size / tile_num_pixels_x ) ) ),
                numTilesY = str( int( math.ceil( common_state.actual_dojo_size / tile_num_pixels_y ) ) ),
                numTilesZ = str( tile_index_z ),
                numTilesW = str( tile_index_w ),
                numVoxelsPerTileX = str( tile_num_pixels_x ),
                numVoxelsPerTileY = str( tile_num_pixels_y ),
                numVoxelsPerTileZ = str( 1 ),
                numVoxelsX = str( common_state.actual_dojo_size ),
                numVoxelsY = str( common_state.actual_dojo_size ),
                numVoxelsZ = str( tile_index_z ),
                dxgiFormat = 'R32_UInt',
                numBytesPerVoxel = str( 4 ),      
                isSigned = str( False ).lower() )
            
            output_tile_volume_file = os.path.join(output_dir, '%02d' % i, 'ids', 'tiledVolumeDescription.xml')
            with open( output_tile_volume_file, 'w' ) as file:
                file.write( lxml.etree.tostring( tiledVolumeDescription, pretty_print = True ) )

if __name__ == "__main__":
    run('/home/hayks/dojo/data/2/seg', '/home/hayks/dojo/data/2/mojo', 'png')

