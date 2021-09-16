import numpy as np


def get_pix_coord(shape):
    h, w = shape
    # list of x coordinates and y coordinates (in pixels)
    x_values = np.arange(w)
    y_values = np.arange(h)
    x, y = np.meshgrid(x_values, y_values)
    pix_coord = [x, y]
    
    return pix_coord


def get_hpc_coord(pix_coord, c_ref, c_delt):
    # Transform coordinate in pixel space to coordinate in helioprojective space
    
    c_x, c_y = c_ref
    x, y = pix_coord
    cdelt_x, cdelt_y = c_delt
    
    # convert to floats
    x = x.astype(float)
    y = y.astype(float)
    
    # distance to coord in pixels
    x -= c_x
    y -= c_y
    

    # multiply to get helioprojective coords
    theta_x = x * cdelt_x
    theta_y = y * cdelt_y
    
    hpc_coord = [theta_x, theta_y]
    return hpc_coord


def get_distance(theta_x, theta_y, D_0):
    # and surface of sun (d) in solar radians
    
    # radius of sun
    R_0 = 1
    
    # initialise d
    d = np.ones(theta_x.shape)
    
    cos_theta = np.sin(np.pi/2 - theta_y) * np.cos(theta_x)
    # descriminant in distance formula
    des = D_0**2 * cos_theta**2 - D_0**2 + R_0
    
    # if no solution (point not on sun) return Nan
    d[des < 0] = np.nan
    d *= D_0 * cos_theta - np.sqrt(D_0**2 * cos_theta**2 - D_0**2 + R_0)

    return d


def heliop_to_helioc(hpc_coord, D_0):
    """
    convert helioprojective cartesian coordinates to heliocentric cartesian coordinates
    Theta_x/y in arcsec
    d in solar radii
    """
    theta_x, theta_y = hpc_coord
    # convert to radians
    theta_y = theta_y * np.pi / (180 * 3600)
    theta_x = theta_x * np.pi / (180 * 3600)
    d = get_distance(theta_x, theta_y, D_0)
    x = d * np.cos(theta_y) * np.sin(theta_x)
    y = d * np.sin(theta_y)
    z = D_0 - d * np.cos(theta_y) * np.cos(theta_x)
    
    hc_coord =  np.array([x, y, z])
    return hc_coord


def get_triangle_area(a, b, c):
    # get area of triangle given 3 points (x, y, z) x3
    # vector from a to b
    ab = b - a
    # vector from a to c
    ac = c - a
    
    # area of triangle
    area = 0.5 * np.linalg.norm(np.cross(ab, ac, axis=0), axis=0)
    
    return area

def get_area(hpc_coord, cdelt, D0):
    # get area of pixel given helioprojective cartesian coord
    theta_x, theta_y = hpc_coord
    # the width, height of a pixel in arcsec
    cdelt_x, cdelt_y = cdelt

    # get coords of corners of given pixel
    top_right_hpc = [theta_x + 0.5 * cdelt_x, theta_y + 0.5 * cdelt_y]
    top_left_hpc = [theta_x - 0.5 * cdelt_x, theta_y + 0.5 * cdelt_y]
    bottom_right_hpc = [theta_x + 0.5 * cdelt_x, theta_y - 0.5 * cdelt_y]
    bottom_left_hpc = [theta_x - 0.5 * cdelt_x, theta_y - 0.5 * cdelt_y]
    
    # convert these to heliocentric coords
    top_right_hc = heliop_to_helioc(top_right_hpc, D0)
    top_left_hc = heliop_to_helioc(top_left_hpc, D0)
    bottom_right_hc = heliop_to_helioc(bottom_right_hpc, D0)
    bottom_left_hc = heliop_to_helioc(bottom_left_hpc, D0)
    
    # get area of quadralaterial, by adding area of two triangles
    # (Assume all 4 points are on the same plane)
    triangle_area_1 = get_triangle_area(bottom_left_hc, top_left_hc, top_right_hc)
    triangle_area_2 = get_triangle_area(bottom_left_hc, bottom_right_hc, top_right_hc)
    
    area = triangle_area_1 + triangle_area_2
    return area


# distance to the centre of sun (in solar radii)
def get_pixel_areas(header, shape, cdelt=None, c_ref=None):
    D_0 = header["DSUN_OBS"] / 696340000
    # pixel coordinates of reference pixel
    if c_ref is None:
        c_ref = header["CRPIX1"], header["CRPIX2"]

    # pixel size (x and y) in arc seconds
    if cdelt is None:
        cdelt = [header["CDELT1"], header["CDELT2"]]
     
    # get pixel coordinates
    pix_coord = get_pix_coord(shape)

    # get helioprojective cartesian coordinates (theta_x, theta_y) from pixel coordinates
    hpc_coord = get_hpc_coord(pix_coord, c_ref, cdelt)
    
    # get area of pixel
    area = get_area(hpc_coord, cdelt, D_0)
    
    # convert to m^2 (from solar radii^2)
    area = area * (696340000**2)

    return area
