# -*- coding: utf-8 -*-
from __future__ import division
import arcpy, os
from arcpy.sa import *
import numpy as np

##原始数据路径，需要修改
modis_path = r'D:\Trendy_Data\NDVI\modis_shiyan'
##临时及最终数据路径，自动创建
NUM = 0
raster_path = r'D:\Trendy_Data\NDVI\modis_shiyan\path_Raster'
LSWI_EVI_path = r'D:\Trendy_Data\NDVI\modis_shiyan\path_LSWI_EVI'
Proj_path = r'D:\Trendy_Data\NDVI\modis_shiyan\path_Proj'
Clip_path = r'D:\Trendy_Data\NDVI\modis_shiyan\path_Clip'
##替换为河南省边界
inMaskData = r'D:\Trendy_Data\NDVI\modis_shiyan\henan\henan.shp'
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

##提取指定波段数据
def extractRaster(rasterList):
    b1_List, b2_List, b3_List, b6_List = [], [], [], []
    modisList = []
    Rnum = 0
    if not os.path.exists(raster_path):
        os.makedirs(raster_path)
    for in_raster in rasterList:
        raster_name_b1 = in_raster[8:16] + '_b1' + '.tif'
        raster_name_b2 = in_raster[8:16] + '_b2' + '.tif'
        raster_name_b3 = in_raster[8:16] + '_b3' + '.tif'
        raster_name_b6 = in_raster[8:16] + '_b6' + '.tif'
        out_raster_b1 = raster_path + '\\' + raster_name_b1
        out_raster_b2 = raster_path + '\\' + raster_name_b2
        out_raster_b3 = raster_path + '\\' + raster_name_b3
        out_raster_b6 = raster_path + '\\' + raster_name_b6
        arcpy.ExtractSubDataset_management(in_raster,out_raster_b1,0)
        arcpy.ExtractSubDataset_management(in_raster,out_raster_b2,1)
        arcpy.ExtractSubDataset_management(in_raster,out_raster_b3,2)
        arcpy.ExtractSubDataset_management(in_raster,out_raster_b6,5)
        b1_List.append(raster_name_b1)
        b2_List.append(raster_name_b2)
        b3_List.append(raster_name_b3)
        b6_List.append(raster_name_b6)
        Rnum += 1
        print 'MODIS: ' + raster_name_b1, raster_name_b2, raster_name_b3, raster_name_b6
    modisList.append(b1_List)
    modisList.append(b2_List)
    modisList.append(b3_List)
    modisList.append(b6_List)
    print 'Numbers: ', Rnum
    print '-'*50
    return modisList

##计算指数 -- LSWI - EVI
def LSWI_EVI_Raster(modisList):
    arcpy.env.workspace = raster_path
    indexList = []
    Rnum = 0
    if not os.path.exists(LSWI_EVI_path):
        os.makedirs(LSWI_EVI_path)
    #arcpy.env.workspace = LSWI_EVI_path
    for i in range(0, NUM):
        #print modisList[0][i], modisList[1][i], modisList[2][i], modisList[3][i]
        LSWI_name = 'LSWI_' + modisList[0][i][0:8] + '.tif'
        EVI_name = 'EVI_' + modisList[0][i][0:8] + '.tif'
        LSWI_path_name = LSWI_EVI_path + '\\' + LSWI_name
        EVI_path_name = LSWI_EVI_path + '\\' + EVI_name
        #LSWI = (b2-b6)/(b2+b6)
        #modiy 1.0
        out_LSWI = Divide(Times(Minus(modisList[1][i], modisList[3][i]), 1.0),
                          Times(Plus(modisList[1][i], modisList[3][i]), 1.0))
        '''
        out_LSWI = Divide(Minus(modisList[1][i], modisList[3][i]),
                          Plus(modisList[1][i], modisList[3][i]))
        '''
        #EVI = 2.5*(b2-b1)/(b2+(6*b1-7.5*b3)+1)
        #
        out_EVI = Times(2.5, Divide(Minus(modisList[1][i], modisList[0][i]),
                             Plus(Plus(modisList[1][i], 1),
                             Minus(Times(6, modisList[0][i]), Times(7.5, modisList[2][i])))))
        #save
        out_LSWI.save(LSWI_path_name)
        print LSWI_name
        out_EVI.save(EVI_path_name)
        print EVI_name
        indexList.append(LSWI_name)
        indexList.append(EVI_name)
        Rnum += 1
    print 'Numbers: ', Rnum
    print '-'*50
    return indexList

##重投影栅格数据
def Proj_Raster(indexList):
    arcpy.env.workspace = LSWI_EVI_path
    if not os.path.exists(Proj_path):
        os.makedirs(Proj_path)
    projList = []
    Rnum = 0
    for index in indexList:
        prj_name = index[:-4] + '_prj' + '.tif'
        prj_path_name = Proj_path + '\\' + prj_name
        #default resemble: 500m
        arcpy.ProjectRaster_management(index, prj_path_name, "PROJCS['Asia_North_Albers_Equal_Area_Conic',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',105.0],PARAMETER['Standard_Parallel_1',25.0],PARAMETER['Standard_Parallel_2',47.0],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]", "NEAREST", "500", "", "", "")
        projList.append(prj_name)
        Rnum += 1
        print 'Project: ' + prj_name
    print 'Numbers: ', Rnum
    print '-'*50
    return projList

##裁剪栅格数据
def Clip_Raster(projList):
    arcpy.env.workspace = Proj_path
    if not os.path.exists(Clip_path):
        os.makedirs(Clip_path)
    Rnum = 0
    for inRaster in projList:
        # Execute ExtractByMask
        clip_name = inRaster[:-4] + '_clip' + '.tif'
        clip_path_name = Clip_path + '\\' + clip_name
        outClip = ExtractByMask(inRaster, inMaskData)
        outClip.save(clip_path_name)
        Rnum += 1
        print 'Clip: ' + clip_name
    print 'Numbers: ', Rnum
    print '-'*50

#主函数
def main():
    rasterList = listRaster()
    modisList = extractRaster(rasterList)
    indexList = LSWI_EVI_Raster(modisList)
    projList = Proj_Raster(indexList)
    Clip_Raster(projList)

if __name__ == "__main__":
    main()
    print 'Complete the processing......'
    print '-'*50








