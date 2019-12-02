#!/usr/bin/python
###############################################################################
# $Id$
#
# Project:  CARBON SINKS
# Purpose:  South African National Land cover classification example
# Author:   Marc Pienaar, marc@saeon.ac.za
#
###############################################################################
from osgeo import gdal
import numpy as np
import time
start_time = time.time()
driver = gdal.GetDriverByName('GTiff')
file = gdal.Open('/Volumes/Samsung_T5/Data/SALC 2018/geotiff/SA_NLC_2018_ALBERS.tif')#e.g. SA land cover 2018 path
band = file.GetRasterBand(1)
#create 2 arrays so that classess aren't overwritten during the reclassification
lista = band.ReadAsArray()
listb= band.ReadAsArray()	

nodata=255
lista.fill(nodata)  
# reclassification of classess
lista[np.where((listb >= 14) & (listb <= 21))] = 1  
lista[np.where( (listb >= 22) & (listb <= 23))] = 2 
lista[np.where(  (listb >= 73)& (listb <= 73))] = 2
lista[np.where( (listb >= 1) & (listb <= 1))] = 3
lista[np.where( (listb >= 2) & (listb <= 4))] = 4
lista[np.where( (listb >= 8) & (listb <= 13))] = 4
lista[np.where( (listb >= 24) & (listb <= 24))] = 4
lista[np.where( (listb >= 40) & (listb <= 40))] = 5
lista[np.where( (listb >= 38) & (listb <= 39))] = 6
lista[np.where( (listb >= 32) & (listb <= 32))] = 7
lista[np.where( (listb >= 33) & (listb <=33))] = 8
lista[np.where( (listb >= 35) & (listb <= 35))] = 9
lista[np.where( (listb >= 41) & (listb <= 41))] = 10
lista[np.where( (listb >= 34) & (listb <= 34))] = 11
lista[np.where( (listb >= 36) & (listb <= 37))] = 12
lista[np.where( (listb >= 5) & (listb <= 7))] = 13
lista[np.where( (listb >= 68) & (listb <= 72))] = 14
lista[np.where( (listb >= 25) & (listb <= 31))] = 15
lista[np.where( (listb >= 47) & (listb <= 67))] = 16
lista[np.where( (listb >= 42) & (listb <= 46))] = 17

DataType=1

# create new file - local output directory
file2 = driver.Create( '/Users/privateprivate/SAEON/Carbon_sinks/python2/Data/land_cover/SALandCover_2018_17_class.tif', file.RasterXSize , file.RasterYSize , 1,DataType)

proj = file.GetProjection()
georef = file.GetGeoTransform()
file2.SetGeoTransform(georef)
file2.SetProjection(proj)
outBand = file2.GetRasterBand(1)
s = outBand.ReadAsArray()	
s=lista
outBand.SetNoDataValue(nodata)
outBand.WriteArray(s)
outBand.FlushCache()
del s
file2=None	
print("--- %s seconds ---" % (time.time() - start_time))
