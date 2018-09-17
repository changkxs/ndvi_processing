# -*- coding: utf-8 -*-
import arcpy
import time
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, TheilSenRegressor
from sklearn.linear_model import RANSACRegressor

print(__doc__)

estimators = [('OLS', LinearRegression()),
              ('Theil-Sen', TheilSenRegressor(random_state=42)),
              ('RANSAC', RANSACRegressor(random_state=42)), ]
colors = {'OLS': 'turquoise', 'Theil-Sen': 'gold', 'RANSAC': 'lightgreen'}

path = r"D:\SCBG\LUCC\Forest\clip"

##List the source data
def listRaster():
    arcpy.env.workspace = path
    rasterList = arcpy.ListRasters()
    num = 0
    for raster in rasterList:
        print raster
        num += 1
    print '-'*50
    print 'Raster Nums: ', num
    return rasterList

def getRaster(rasterList):
    for raster in rasterList:
        num = 0
        #Get the geoprocessing result object
        meanResult_R = arcpy.GetRasterProperties_management(raster, "MEAN", "Band_1")
        meanResult_G = arcpy.GetRasterProperties_management(raster, "MEAN", "Band_2")
        meanResult_B = arcpy.GetRasterProperties_management(raster, "MEAN", "Band_3")
        print meanResult_R, meanResult_G, meanResult_B
        #Get the elevation standard deviation value from geoprocessing result object
        #elevSTD = elevSTDResult.getOutput(0)

def main():
    rasterList = listRaster()
    getRaster(rasterList)
    
if __name__ == "__main__":
    main()
