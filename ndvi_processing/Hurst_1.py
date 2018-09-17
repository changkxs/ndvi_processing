# -*- coding: utf-8 -*-
import os
import arcpy
from arcpy import env
from arcpy.sa import *
from numpy import mean,std,max,min,log
import numpy as np
import math
arcpy.CheckOutExtension("Spatial")
print "dsd"
#线形拟合
def linefit(x , y):
    N = float(len(x))
    sx,sy,sxx,syy,sxy=0,0,0,0,0
    for i in range(0,int(N)):
        sx  += x[i]
        sy  += y[i]
        sxx += x[i]*x[i]
        syy += y[i]*y[i]
        sxy += x[i]*y[i]
    a = (sy*sx/N -sxy)/( sx*sx/N -sxx)
    b = (sy - a*sx)/N
    r = abs(sy*sx/N-sxy)/math.sqrt((sxx-sx*sx/N)*(syy-sy*sy/N))
    return a,b,r
#列出所有文件
def listdir(path):
    list_name=[]
    for file in os.listdir(path):
        # print file

        if os.path.splitext(file)[1] == '.tif':
            file_path = os.path.join(path, file)
            list_name.append(file_path)
    return list_name



data=[]
arrdata=[] #读取所有数据
# x1=[[1,2,3,4],
#     [1,2,3,4]]
# x2=[[1,2,3,4],
#     [1,2,3,4]]

#获得参考图像
inRas = arcpy.Raster(r"E:\image\Data\NDVI-Y\1982Y.tif")
lowerLeft = arcpy.Point(inRas.extent.XMin, inRas.extent.YMin)
cellSize = inRas.meanCellWidth
bandcount=inRas.bandCount
extent=inRas.extent
height=inRas.height
width=inRas.width
spatial=inRas.spatialReference
amount=height*width

list_name=listdir(r"E:\image\Data\NDVI-Y") #tiff文件所在目录
yearsum=len(list_name)
for i in list_name:
    inRas = arcpy.Raster(i)
    # lowerLeft = arcpy.Point(inRas.extent.XMin,inRas.extent.YMin)
    # cellSize = inRas.meanCellWidth

    # Convert Raster to numpy array
    tempppp=arcpy.RasterToNumPyArray(inRas,nodata_to_value=0)
    arrdata.append(arcpy.RasterToNumPyArray(inRas,nodata_to_value=0))

#将读取的数据合并
for i in range(height):
    for j in range(width):
        tempdata = []
        for k in arrdata:
            tempdata.append(k[i][j])
        data.append(tempdata)
rszyh=[ [0 for i in range(yearsum-1)] for i in range(amount)]
e=[0]*(yearsum-1)
s=[0]*(yearsum-1)
temp=[0]*(yearsum-1)
x=[0]*(yearsum-1)
zyyy=[0]*(yearsum-1)
r=[0]*(yearsum-1)
for k in range(amount):#像元数量
    for i in range(1,yearsum):#年份
        e[i-1]=mean(data[k][0:i]);
        s[i-1]=std(data[k][0:i]); #标准差
        for j in range(i):
            temp13=data[k][j]
            temp[j]=data[k][j]-e[i-1]
            x[i-1]=sum(temp)
            zyyy[j]=x[i-1];
        r[i-1]=max(zyyy)-min(zyyy)
        if s[i-1]==0:
            rszyh[k][i - 1]=0
        else:
            rszyh[k][i-1]=log(r[i-1]/s[i-1])
rszyh


x=range(1,yearsum)
x=log(x)
a=[]
b=[]
r=[]
tempi=0
tempa =[]
tempb =[]
tempr =[]
for i in rszyh:
    tempi=tempi+1
    ta,tb,tr=linefit(x,i)

    tempa.append(ta)
    if tempi % width == 0:
        a.append(tempa)
        tempa = []

    tempb.append(tb)
    if tempi % width == 0:
        b.append(tempb)
        tempb = []

    tempr.append(tr)
    if tempi % width == 0:
        r.append(tempr)
        tempr = []

#Convert Array to raster (keep the origin and cellsize the same as the input)
a_np=np.array(a)
b_np=np.array(b)
r_np=np.array(r)
newRaster = arcpy.NumPyArrayToRaster(a_np,lowerLeft,cellSize,
                                     value_to_nodata=0)
newRaster.save(r"E:\image\Data\hurst\a.tif")
newRaster = arcpy.NumPyArrayToRaster(b_np,lowerLeft,cellSize,
                                     value_to_nodata=0)
newRaster.save(r"E:\image\Data\hurst\b.tif")
newRaster = arcpy.NumPyArrayToRaster(r_np,lowerLeft,cellSize,
                                     value_to_nodata=0)
newRaster.save(r"E:\image\Data\hurst\r.tif")
print "dsd"