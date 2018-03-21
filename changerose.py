from PIL import Image
import glob, os, sys, errno
import numpy as np
import argparse

BOUNDARY_WIDTH = 1

# return a tuple of total size and paste position
def get_new_size(image):
    # Set requisite dimensions. Center original image within new image.
    max_dimension = max(image.width, image.height)
    return (max_dimension, max_dimension)

def get_paste_position(image):
    max_dimension = max(image.width, image.height)
    return (int(np.floor(max_dimension/2))
                     -int(np.floor(image.width/2)),
                      int(np.floor(max_dimension/2))
                     -int(np.floor(image.height/2)))

# colors are tuples, positions are ints
def get_intermediate_pixel(position, edge_position, boundary_position,
                           background_color, boundary_color):
    return tuple([int(a + np.floor((b - a)/(boundary_position - edge_position)
        * (position - edge_position)))
        for (a,b) in zip(background_color,boundary_color)])

def average_color(*images):
    r_tot = 0
    g_tot = 0
    b_tot = 0
    pixel_num = 0
    for image in images:
        rgb_data = image.getdata()
        for (r,g,b) in rgb_data:
            r_tot += r
            g_tot += g
            b_tot += b
        pixel_num += len(rgb_data)
    return (int(np.round(r_tot / pixel_num)),
            int(np.round(g_tot / pixel_num)),
            int(np.round(b_tot / pixel_num)))

# def average_color(image1, image2):
#     rgb_data1 = image1.getdata()
#     rgb_data2 = image2.getdata()
#     r_tot = 0
#     g_tot = 0
#     b_tot = 0
#     for (r,g,b) in rgb_data1:
#         r_tot += r
#         g_tot += g
#         b_tot += b
#     for (r,g,b) in rgb_data2:
#         r_tot += r
#         g_tot += g
#         b_tot += b
#     pixel_num = len(rgb_data1) + len(rgb_data2)
#     return (int(np.round(r_tot / pixel_num)),
#             int(np.round(g_tot / pixel_num)),
#             int(np.round(b_tot / pixel_num)))

def average_first_boundary_color(image, boundary_width = BOUNDARY_WIDTH):
    # Analyze border of image to calculate mean color
    if image.width > image.height:
        top_boundary = image.crop((0,
                                    0,
                                    image.width,
                                    boundary_width)).convert('RGB')
        return average_color(top_boundary)
    elif image.width < image.height:
        left_boundary = image.crop((0,
                                     0,
                                     boundary_width,
                                     image.height)).convert('RGB')
        return average_color(left_boundary)
    else:
        # Image is already square to begin with, background color doesn't matter
        return (0, 0, 0)

def average_second_boundary_color(image, boundary_width = BOUNDARY_WIDTH):
    # Analyze border of image to calculate mean color
    if image.width > image.height:
        bot_boundary = image.crop((0,
                                    image.height-boundary_width,
                                    image.width,
                                    image.height)).convert('RGB')
        return average_color(bot_boundary)
    elif image.width < image.height:
        right_boundary = image.crop((image.width-boundary_width,
                                      0,
                                      image.width,
                                      image.height)).convert('RGB')
        return average_color(right_boundary)
    else:
        # Image is already square to begin with, background color doesn't matter
        return (0, 0, 0)

def average_boundary_color(image, boundary_width = BOUNDARY_WIDTH):
    # Analyze border of image to calculate mean color
    if image.width > image.height:
        top_boundary = image.crop((0,
                                    0,
                                    image.width,
                                    boundary_width)).convert('RGB')
        bot_boundary = image.crop((0,
                                    image.height-boundary_width,
                                    image.width,
                                    image.height)).convert('RGB')
        return average_color(top_boundary, bot_boundary)
    elif image.width < image.height:
        left_boundary = image.crop((0,
                                     0,
                                     boundary_width,
                                     image.height)).convert('RGB')
        right_boundary = image.crop((image.width-boundary_width,
                                      0,
                                      image.width,
                                      image.height)).convert('RGB')
        return average_color(left_boundary, right_boundary)
    else:
        # Image is already square to begin with, background color doesn't matter
        return (0, 0, 0)

def color_background(image, color = 0, boundary_width = BOUNDARY_WIDTH):
    return Image.new('RGB',get_new_size(image),color)

def average_background(image, boundary_width = BOUNDARY_WIDTH):
    background_color = average_boundary_color(image, boundary_width)
    return Image.new('RGB',get_new_size(image),background_color)

def blend_background(image):
    background = average_background(image, boundary_width = 1)
    first_background_color = average_first_boundary_color(image, boundary_width = 1)
    second_background_color = average_second_boundary_color(image, boundary_width = 1)
    # Analyze border of image to calculate mean color
    if image.width > image.height:
        top_boundary_y = get_paste_position(image)[1]
        bot_boundary_y = top_boundary_y + image.height
        for x in np.arange(0, image.width):
            x = int(x)
            top_boundary_color = image.getpixel((x, 0))
            bot_boundary_color = image.getpixel((x, image.height - 1))
            for y in np.arange(0, top_boundary_y):
                y = int(y)
                new_color = get_intermediate_pixel(y,
                                                   0,
                                                   top_boundary_y,
                                                   first_background_color,
                                                   top_boundary_color)
                background.putpixel((x,y), new_color)

            for y in np.arange(bot_boundary_y, image.width):
                y = int(y)
                new_color = get_intermediate_pixel(y,
                                                   image.width - 1,
                                                   bot_boundary_y - 1,
                                                   second_background_color,
                                                   bot_boundary_color)
                background.putpixel((x,y), new_color)

    elif image.width < image.height:
        left_boundary_x = get_paste_position(image)[0]
        right_boundary_x = left_boundary_x + image.width
        for y in np.arange(0, image.height):
            y = int(y)
            left_boundary_color = image.getpixel((0, y))
            right_boundary_color = image.getpixel((image.width - 1, y))
            for x in np.arange(0, left_boundary_x):
                x = int(x)
                new_color = get_intermediate_pixel(x,
                                                   0,
                                                   left_boundary_x,
                                                   first_background_color,
                                                   left_boundary_color)
                background.putpixel((x,y), new_color)

            for x in np.arange(right_boundary_x, image.height):
                x = int(x)
                new_color = get_intermediate_pixel(x,
                                                   image.height - 1,
                                                   right_boundary_x - 1,
                                                   second_background_color,
                                                   right_boundary_color)
                background.putpixel((x,y), new_color)

    else:
        # Image is already square
        pass;

    return background

def copy_image(filenames = '*.png', method = 'color', color = 0):
    """
    Create image copies with square dimensions by adding additional space to the
    original image. Image copies may fill background with either a solid color
    (default: white) or a computed average based on the edge of the original
    image.
    """

    input_files = glob.glob(filenames)

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

        # Create background image layer
        if method == 'color':
            final_im = color_background(im_copy, color = color)
        elif method == 'average':
            final_im = average_background(im_copy)
        elif method == 'blend':
            final_im = blend_background(im_copy)
        else:
            sys.exit('Invalid color method specified!')

        final_im.paste(im_copy, get_paste_position(im_copy))

        im_copy.close()

        # Save final image with informative filename
        root, ext = os.path.splitext(filename)

        final_filename = ''
        if method == 'color':
            final_filename = new_dirname + root + '_changerose_' \
                           + method + '_' + color + ext
        else:
            final_filename = new_dirname + root + '_changerose_' \
                           + method + ext

        final_im.save(final_filename)
        final_im.close()

def main():
    parser = argparse.ArgumentParser(description='Make a square image ' +
        "according to a certain background color prescription.")
    parser.add_argument('-m', '--method', type=str, dest='method',
                        help='method for generating background ' +
                            '(average, blend, color)')
    parser.add_argument('-c', '--color', dest='color', default=0,
                        help='background color')
    parser.add_argument('filenames', type=str,
                        help='regular expression for filenames')

    args = parser.parse_args()

    copy_image(args.filenames, args.method, args.color)

if __name__ == '__main__':
    main()
