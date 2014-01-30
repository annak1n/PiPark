"""
Authors: Nicholas Sanders & Humphrey Shotton
Filename: main.py
Version: [2014/01/26]

Description:
PiPark main program file.

"""

import urllib

import imageread
import senddata
import settings as s
try:
    import setup_data
except ImportError:
    print "ERROR: setup_data.py does not exist. Run setup.py first."
    sys.exit()

# -----------------------------------------------------------------------------
#
#       Main Program
#
# -----------------------------------------------------------------------------
def __main():
    """Run the main program. """
    
    # setup camera and image save location
    camera = imageread.setup_camera()
    camera.start_preview()
    image_location = "./images/pipark.jpeg"

    # load data sets and count num spaces on control boxes
    space_boxes, control_boxes = __setup_box_data()
    
    num_spaces = len(space_boxes)
    num_controls = len(control_boxes)

    print "Number of spaces:", num_spaces, "Number of Control boxes:", num_controls
    
    assert num_spaces > 0
    assert num_controls == 3
    
    
    # run centralised program loop
    while True:
        space_averages = []
        control_averages = []
        
        # take new picture, save to specified location
        camera.capture(image_location)
        print "INFO: New picture taken,", image_location

        # load image
        try:
            image = imageread.Image.open(image_location)
            pixels = image.load()
        except:
            print "ERROR: Image has failed to load."

        # setup spaces
        for space in space_boxes:
            
            space_x, space_y, space_w, space_h = __get_area_values(space)
            
            print "Space dims:"
            print "x", space_x, "y", space_y, "w", space_w, "h", space_h

            space_averages.append(imageread.get_area_average(pixels, space_x, space_y, space_w, space_h))

        # setup control
        for control in control_boxes:

            control_x, control_y, control_w, control_h = __get_area_values(control)

            print "Control dims:"
            print "x", control_x, "y", control_y, "w", control_w, "h", control_h

            control_averages.append(imageread.get_area_average(pixels, control_x, control_y, control_w, control_h))
            
        print "\n\n"
        # compare control points to spaces
        for i, space in zip(space_boxes, space_averages):

            num_controls = 0
            for control in control_averages:
                if imageread.compare_area(space, control):
                    num_controls += 1

            #for j, control in enumerate(control_averages):
            if num_controls >= 2:
                print "INFO: Space", i[0], "occupied!"
                print senddata.send_update(i[0], 1), "\n"
            else:
                print "INFO: Space", i, "vacant!"
                print senddata.send_update(i[0], 0), "\n"

        print "INFO: Sleeping for 5s"
        imageread.time.sleep(5)

# -----------------------------------------------------------------------------
#  Get Area Values
# -----------------------------------------------------------------------------
def __get_area_values(area):
    """
    Keyword Arguments:
    area -- tuple in form (x1, y1, x2, y2) from setup.py

    Returns:
    x, y, width, height
    """

    try:
        assert isinstance(area, tuple)
    except AssertionError:
        print "ERROR: Area must be tuple data type [__get_area_values()]."

    min_x_percent = area[2] if area[2] < area[4] else area[4]
    min_y_percent = area[3] if area[3] < area[5] else area[5]
    width_percent = abs(area[2] - area[4])
    height_percent = abs(area[3] - area[5])

    min_x = int(min_x_percent * s.PICTURE_RESOLUTION[0])
    min_y = int(min_y_percent * s.PICTURE_RESOLUTION[1])
    width = int(width_percent * s.PICTURE_RESOLUTION[0])
    height = int(height_percent * s.PICTURE_RESOLUTION[1])

    return min_x, min_y, width, height

# -----------------------------------------------------------------------------
#  Setup Box Data
# -----------------------------------------------------------------------------
def __setup_box_data():
    """Import and return the boxes dictionary from setup_data.py. """
    
    # attempt to load dictionary from setup_data.py, if file does not exist
    # print error message and quit the program
    try:
        box_data = setup_data.boxes
        print "INFO: box_data successfully created."
    except:
        print "ERROR: setup_data.py does not contain the variable 'boxes'."
        sys.exit()
    
    # setup_data.py exists, check that dictionary contains items, if dicionary
    # is empty print error message and quit the program
    if not box_data:
        print "ERROR: boxes in setup_data.py is empty!"
        sys.exit()
    else:
        print "INFO: box_data contains data!"

    space_boxes = []
    control_boxes = []
    
    for data_set in box_data:
        if data_set[1] == 0: space_boxes.append(data_set)
        elif data_set[1] == 1: control_boxes.append(data_set)
        else: print "ERROR: Box-type not set to either 0 or 1."

    print "space boxes:", space_boxes, "\ncontrol boxes:", control_boxes
    return space_boxes, control_boxes

    
# -----------------------------------------------------------------------------
#  Run Program
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    __main()