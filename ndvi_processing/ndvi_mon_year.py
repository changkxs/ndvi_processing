# -*- coding: utf-8 -*-
from __future__ import division
import arcpy, os
from arcpy.sa import *
import numpy as np

##原始数据路径，需要修改
modis_path = r'G:\clip'
##临时及最终数据路径，自动创建
NUM = 0
maxmon_path = os.path.join(modis_path, 'path_MaxMonth')
year_path = os.path.join(modis_path, 'path_Year')
##扩展模块
arcpy.CheckOutExtension("Spatial")


##读取原始数据文件
def listRaster():
    arcpy.env.workspace = modis_path
    rasterList = arcpy.ListRasters()
    Rnum = 0
    global NUM
    for raster in rasterList:        
        print raster
        Rnum += 1
    print 'Numbers: ', Rnum
    NUM = Rnum
    print '-'*50
    return rasterList

##求取NDVI - 月最大值
def MaxMon_Raster(rasterList):
    item_list = [1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177, 193,
                 209, 225, 241, 257, 273, 289, 305, 321, 337, 353]
    maxmonList = []    
    if not os.path.exists(maxmon_path):
        os.makedirs(maxmon_path)
    for year in range(2001, 2016):
        #分年
        yearList = []
        for raster in rasterList:
            if int(raster[9:13]) == year:
                yearList.append(raster)
        #分月
        mon1, mon2, mon3, mon4, mon5, mon6, mon7, mon8, mon9, mon10, mon11, mon12 = [], [], [], [], [], [], [], [], [], [], [], []
        year_mon_List = []
        for mons in yearList:            
            if 0 < int(mons[13:16]) <= 31:
                mon1.append(mons)                
            elif 31 < int(mons[13:16]) <= 60:
                mon2.append(mons)
            elif 60 < int(mons[13:16]) <= 91:
                mon3.append(mons)
            elif 91 < int(mons[13:16]) <= 121:
                mon4.append(mons)
            elif 121 < int(mons[13:16]) <= 152:
                mon5.append(mons)
            elif 152 < int(mons[13:16]) <= 182:
                mon6.append(mons)
            elif 182 < int(mons[13:16]) <= 213:
                mon7.append(mons)
            elif 213 < int(mons[13:16]) <= 244:
                mon8.append(mons)
            elif 244 < int(mons[13:16]) <= 274:
                mon9.append(mons)
            elif 274 < int(mons[13:16]) <= 305:
                mon10.append(mons)
            elif 305 < int(mons[13:16]) <= 335:
                mon11.append(mons)
            elif 335 < int(mons[13:16]) <= 365:
                mon12.append(mons)
            else:
                print 'error - error '*10
        #分月结果列表
        year_mon_List.append(mon1)
        year_mon_List.append(mon2)
        year_mon_List.append(mon3)
        year_mon_List.append(mon4)
        year_mon_List.append(mon5)
        year_mon_List.append(mon6)
        year_mon_List.append(mon7)
        year_mon_List.append(mon8)
        year_mon_List.append(mon9)
        year_mon_List.append(mon10)
        year_mon_List.append(mon11)
        year_mon_List.append(mon12)
        #月最值
        Rnum = 0            
        for mon_raster in year_mon_List:
            Rnum += 1
            mon_name = str(year) + '_' + str(Rnum) + '.tif'
            path_name = maxmon_path + '\\' + mon_name
            outMax = CellStatistics(mon_raster, "MAXIMUM", "NODATA")
            outMax.save(path_name)
            maxmonList.append(mon_name)
            print mon_name
            print mon_raster
        print '*'*50
    print '-'*50
    return maxmonList

##求取NDVI - 年均值
def MeanYear_Raster(maxmonList):
    arcpy.env.workspace = maxmon_path
    if not os.path.exists(year_path):
        os.makedirs(year_path)
    Rnum = 0
    for year in range(2001, 2016):
        meanList = []
        name = ''
        for raster in maxmonList:
            if raster[:4] == str(year):
                meanList.append(raster)
                name = 'mean' + raster[:4] + '.tif'
                path_name = year_path + '\\' + name
        outMean = CellStatistics(meanList, "MEAN", "NODATA")        
        outMean.save(path_name)
        Rnum += 1
        print 'Mean: ' + name
    print 'Numbers: ', Rnum
    print '-'*50
        
#主函数
def main():
    rasterList = listRaster()
    maxmonList = MaxMon_Raster(rasterList)
    MeanYear_Raster(maxmonList)

if __name__ == "__main__":
    main()
    print '-'*50








