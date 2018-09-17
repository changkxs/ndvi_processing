# -*- coding: utf-8 -*-
from __future__ import division
import arcpy
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

##文件路径,需要修改 -- 将NDVI和降雨数据放在一个文件夹内
file_path = r"D:\SCBG\Trendy_Data\NDVI\pre_ndvi"          #ndvi、rain路径
##总年数，需要修改
year = 34

##读取栅格文件
def listRaster(file_path, word):
    arcpy.env.workspace = file_path    
    rasterList = arcpy.ListRasters(word)
    Rnum = 0
    for raster in rasterList:        
        print raster
        Rnum += 1
    print 'Numbers: ', Rnum
    print '-'*50
    return rasterList

##求取相关系数 - R
def R_Value(ndviList, rainList):
    arcpy.env.workspace = file_path
    meanNDVI = CellStatistics(ndviList, "MEAN", "DATA")
    meanRain = CellStatistics(rainList, "MEAN", "DATA")

    List1, List2x, List2y = [], [], []
    for i in range(0, year): #(1,year]
        ndviRaster = Minus(ndviList[i], meanNDVI)
        rainRaster = Minus(rainList[i], meanRain)
        #List1 += ndviRaster * rainRaster
        List1.append(Times(ndviRaster, rainRaster))
        #List2x += Square(ndviRaster)
        List2x.append(Square(ndviRaster))
        #List2y += Square(rainRaster)
        List2y.append(Square(rainRaster))

    sumList1 = CellStatistics(List1, "SUM", "DATA")
    print List1
    sumList2x = CellStatistics(List2x, "SUM", "DATA")
    sumList2y = CellStatistics(List2y, "SUM", "DATA")
    print List2x
    print List2y
    List2 = SquareRoot(Times(sumList2x, sumList2y))        
    outR = Divide(sumList1, List2)
    path_name = file_path + '\\' + 'R_pre_value.tif'
    outR.save(path_name)
    print '-'*50

        
def main():
    ndviList = listRaster(file_path, '*Y*')
    rainList = listRaster(file_path, '*pre*')
    R_Value(ndviList, rainList)

if __name__ == "__main__":
    main()
