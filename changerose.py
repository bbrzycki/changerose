from PIL import Image
import glob, os, sys, errno
import numpy as np

BOUNDARY_WIDTH = 1

def copy_image(argv):
    """
    Create image copies with square dimensions by adding additional space to the
    original image. Image copies may fill background with either a solid color
    (default: white) or a computed average based on the edge of the original
    image.
    """
    # Check correct number of arguments
    if len(argv) < 3:
        sys.exit('Usage: python %s <filenames> <background_type>' % (argv[0],))

    # input_files = glob.glob(argv[1])
    input_files = argv[2:]
    background_type = argv[1]

    if len(input_files) == 0:
        sys.exit('The expression \'%s\' does not match any filenames!'
            % (argv[1],))


    for input_file in input_files:

        # Create directory for image copies; potentially spanning multiple
        # directories
        dirname, filename = os.path.split(os.path.abspath(input_file))
        if dirname[-1] != '/':
            dirname = dirname + '/'
        new_dirname = dirname + 'changerose/'
        try:
            os.makedirs(new_dirname)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        # Retain original image
        im = Image.open(input_file)
        im_copy = im.copy()
        im.close()

        # Set requisite dimensions. Center original image within new image.
        max_dimension = max(im_copy.width, im_copy.height)
        paste_position = (int(np.floor(max_dimension/2))
                         -int(np.floor(im_copy.width/2)),
                          int(np.floor(max_dimension/2))
                         -int(np.floor(im_copy.height/2)))
        new_size = (max_dimension, max_dimension)

        # Set background color of image copy.
        background_color = 0
        if background_type == 'average':
            r_tot = 0
            g_tot = 0
            b_tot = 0
            # Analyze border of image to calculate mean color
            if im_copy.width > im_copy.height:
                im_top_bound = im_copy.crop((0,
                                            0,
                                            im_copy.width,
                                            BOUNDARY_WIDTH)).convert('RGB')
                top_bound = im_top_bound.getdata()
                im_bot_bound = im_copy.crop((0,
                                            im_copy.height-BOUNDARY_WIDTH,
                                            im_copy.width,
                                            im_copy.height)).convert('RGB')
                bot_bound = im_bot_bound.getdata()
                for (r,g,b) in top_bound:
                    r_tot += r
                    g_tot += g
                    b_tot += b
                for (r,g,b) in bot_bound:
                    r_tot += r
                    g_tot += g
                    b_tot += b
                pixel_num = len(top_bound) + len(bot_bound)
                background_color = (int(np.round(r_tot / pixel_num)),
                                    int(np.round(g_tot / pixel_num)),
                                    int(np.round(b_tot / pixel_num)))
            elif im_copy.width < im_copy.height:
                im_left_bound = im_copy.crop((0,
                                             0,
                                             BOUNDARY_WIDTH,
                                             im_copy.height)).convert('RGB')
                left_bound = im_left_bound.getdata()
                im_right_bound = im_copy.crop((im_copy.width-BOUNDARY_WIDTH,
                                              0,
                                              im_copy.width,
                                              im_copy.height)).convert('RGB')
                right_bound = im_right_bound.getdata()
                for (r,g,b) in left_bound:
                    r_tot += r
                    g_tot += g
                    b_tot += b
                for (r,g,b) in right_bound:
                    r_tot += r
                    g_tot += g
                    b_tot += b
                pixel_num = len(left_bound) + len(right_bound)
                background_color = (int(np.round(r_tot / pixel_num)),
                                    int(np.round(g_tot / pixel_num)),
                                    int(np.round(b_tot / pixel_num)))
            else:
                # Image is already square to begin with
                pass
        else:
            # Parse background_type argument
            background_color = background_type

        # Create final image
        background_im = Image.new('RGB',new_size,background_color)
        background_im.paste(im_copy, paste_position)
        im_copy.close()

        # Save new image
        root, ext = os.path.splitext(filename)
        background_im.save(new_dirname + root + '_changerose' + ext)
        background_im.close()



if __name__ == '__main__':
    copy_image(sys.argv)
