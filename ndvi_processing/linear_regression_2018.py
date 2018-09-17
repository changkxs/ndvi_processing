# ----------
# Name: linear_regression
# Date and Author: 12/18/2017 by Ye Yongchang
# Description:
#     Do linear regression for time-series remote sensing iamge
#     Extract the pvalue, R2 and slope to file
#     The script was tested on python 3.6.1 - 64 bit
# ----------

import os
import re
import time
import numpy as np
from osgeo import gdal
from scipy import stats

# set workspace
s = os.sep
PATHRD_x = "E:" + s + "T"
PATHRD_y = "E:" + s + "Year"
PATHWT = "E:" + s + "out"

def listfile(input_path, type = False):
    """THis function gives the full path of files or dirs in a directory."""
    # The default parameter type is False, all the files and dirs will be return.
    # If the type is given 'file' or 'dir/folder', only the assigned file type will be returned.
    path_files = list()
    path_dirs = list()
    for root, dirs, files in os.walk(input_path):
        for file in files:
            path_files.append(os.path.join(root, file))
        for dir in dirs:
            path_dirs.append(os.path.join(root, dir))
        break  # not recursive

    if type == "file":
        path = path_files
    elif type == "folder" or type == "dir":
        path = path_dirs
    else:
        path = path_files + path_dirs
    return (path)

class Rasterattr:
    """This class get the raster attributes: nodata, data type, number of bands, number of columns and number of rows, geotransform, spatial reference, the data array"""
    def __init__(self, input):
        # input may be a object or file path
        if isinstance(input, str):
            d = gdal.Open(input)
        elif isinstance(input, gdal.Dataset):
            d = input

        self.nodata = d.GetRasterBand(1).GetNoDataValue()
        self.dtype = d.GetRasterBand(1).DataType
        # number of bands
        self.nbands = d.RasterCount
        # ncols
        self.xsize = d.RasterXSize
        # nrows
        self.ysize = d.RasterYSize
        # (x_top_left, x_resolution, rotation, y_top_left, rotation, y_resolution)
        # roatation, 0 if image is "north up"
        self.geotrans = d.GetGeoTransform()
        self.spatialref = d.GetProjection()

class Rwgeotiff:
    def geotiffarray(self, input, band = 1):
        """This function get the array from a file or gdal.Dataset object"""
        if isinstance(input, str):
            d = gdal.Open(input)
        elif isinstance(input, gdal.Dataset):
            d = input
        d = d.GetRasterBand(band).ReadAsArray()
        return(d)

    def array2geotiff(self, array, xsize, ysize, dtype, nodata, geotrans, spatialref, output_file):
        """This function write a matrix to one-band geotiff."""
        driver = gdal.GetDriverByName('GTiff')
        target = driver.Create(output_file, xsize, ysize, 1, dtype, ['COMPRESS=LZW'])
        target.SetGeoTransform(geotrans)
        target.SetProjection(spatialref)
        target.GetRasterBand(1).WriteArray(array)
        # set No data
        target.GetRasterBand(1).SetNoDataValue(nodata)
        # write to disk
        target.FlushCache()

    def wt2geotiff(self, input, output_file):
        """This function write a file or raster object to geotiff."""
        if os.path.exists(output_file):
            raise IOError("The output file has existed")
        else:
            # get attribute
            r = Rasterattr(input)
            # get array
            array = self.geotiffarray(input)
            self.array2geotiff(array, r.xsize, r.ysize, r.dtype, r.nodata, r.geotrans, r.spatialref, output_file)

def images_to_array(input_files):
    """This function returns an array. The columns equal to the number of images. The rows equal to the cellsize of one image."""
    # It read each image to array and unlist the array by rows
    # Bind all the rows to a matrix, each row as a column of the matrix

    # get the xsize and ysize of the raster
    r = Rasterattr(input_files[0])
    w = Rwgeotiff()

    # create an matrix
    array = np.empty((r.xsize*r.ysize, len(input_files)), dtype = np.float32)
    #  read each file to array
    for i, each_file in enumerate(input_files):
        array[:, i] = w.geotiffarray(each_file).ravel()
    return(array)

def main():
    files_y = listfile(PATHRD_y)
    files_y = [x for x in files_y if re.match(".*.tif$", x, re.IGNORECASE)]
    files_x = listfile(PATHRD_x)
    files_x = [x for x in files_x if re.match(".*.tif$", x, re.IGNORECASE)]

    # get the xsize and ysize of the raster
    r = Rasterattr(files_y[0])
    # get nodata index
    w = Rwgeotiff()
    d = w.geotiffarray(files_y[0]).ravel()
    not_na_index = np.where(d != r.nodata)[0]

    # read image data
    array_y = images_to_array(files_y)
    array_x = images_to_array(files_x)

    # create an matrix for output
    r_array = np.full(r.xsize*r.ysize, r.nodata, dtype = np.float32)
    pvalue_array = np.full(r.xsize * r.ysize, r.nodata, dtype=np.float32)

    for i in not_na_index:
        x = array_x[i, :]
        y = array_y[i, :]
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        # r2 = r_value**2

        r_array[i] = r_value
        pvalue_array[i] = p_value

    # write array to file
    r_array = r_array.reshape(r.ysize, r.xsize)
    pvalue_array = pvalue_array.reshape(r.ysize, r.xsize)

    outputfile_r = PATHWT + s + os.path.basename(PATHRD_x) + "_r.tif"
    outputfile_pvalue = PATHWT + s + os.path.basename(PATHRD_x) + "_pvalue.tif"
    w.array2geotiff(r_array, r.xsize, r.ysize, gdal.GDT_Float32, r.nodata, r.geotrans, r.spatialref, outputfile_r)
    w.array2geotiff(pvalue_array, r.xsize, r.ysize, gdal.GDT_Float32, r.nodata, r.geotrans, r.spatialref, outputfile_pvalue)

if __name__ == "__main__":
    # start time
    start_time = time.time()
    main()
    # end time
    print("running time: %s" % ((time.time() - start_time) / 60))
