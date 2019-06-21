import arcpy


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Ulwazi custom Tools"
        self.alias = "UlwaziTools"
        self.description = "Toolkit containing custom tools made by SAEON Ulwazi Node"

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "GDAL_Area_weighting"
        self.description = "Tool for calculating the area in m^2 for each class of a classified raster that is within each of the input polygons"
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input workspace",
            name="arcpy.env.workspace",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")
        param1 = arcpy.Parameter(
            displayName="Input classified raster",
            name="input_raster",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")
        param2 = arcpy.Parameter(
            displayName="Input features",
            name="input_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="In Fields",
            name="in_fields",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        param3.parameterDependencies = [param2.name]

        params = [param0, param1, param2, param3]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        import arcpy
        import os
        environList = os.environ['PATH'].split(';')
        environList.insert(0, r'C:\Program Files\GDAL')
        os.environ['PATH'] = ';'.join(environList)
        import gdal
        import ogr
        import os
        import time
        start_time = time.time()
        gdal.UseExceptions()
        gdal.AllRegister()
        # path to gdal data directory
        gdal.SetConfigOption("GDAL_DATA", "C:\\Program Files\\GDAL\\gdal-data")

        outWorkspace = arcpy.GetParameterAsText(0) + "/"
        input_raster = arcpy.GetParameterAsText(1)
        input_features = arcpy.GetParameterAsText(2)
        field_name = arcpy.GetParameterAsText(3)

        arcpy.env.workspace = outWorkspace
        arcpy.env.overwriteOutput = True
        output_features = outWorkspace + "\\projected.shp"
        out_coordinate_system = arcpy.SpatialReference(arcpy.Describe(input_raster).spatialReference.factoryCode)
        Temp_polygon_shp_for_clipping_path = outWorkspace + "\\temp.shp"
        # outWorkspace = "C:\\Users\\theon_000\\Downloads\\test2\\output/"
        # input_raster = "C:\\Users\\theon_000\\Downloads\\test2\\landcover_2013_test.tif"
        # input_features = "C:\\Users\\theon_000\\Downloads\\test2\\grid_500m_test.shp"
        # output_features = "C:\\Users\\theon_000\\Downloads\\test2\\output\\proj_grid.shp"

        # out_coordinate_system = arcpy.SpatialReference('WGS 1984 UTM Zone 35S')
        # Temp_polygon_shp_for_clipping_path = "C:\\Users\\theon_000\\Downloads\\test2\\output\\temp.shp"

        proj_grid = arcpy.Project_management(input_features, output_features, out_coordinate_system)

        # new files that will be created

        Hi_res_clipped_raster_path2 = '/vsimem/hi_res22.tif'
        Hi_res_raster_path = '/vsimem/hi_res.tif'
        Hi_res_clipped_raster_path = '/vsimem/clip.tif'

        ds = gdal.Warp(Hi_res_clipped_raster_path, input_raster,
                       format='GTiff', cutlineDSName=input_features)
        ds = None

        dataset = gdal.Open(Hi_res_clipped_raster_path, gdal.GA_ReadOnly)
        geotransform = dataset.GetGeoTransform()
        x_res = dataset.RasterXSize
        y_res = dataset.RasterYSize

        out_ds = gdal.Translate(Hi_res_raster_path, dataset,
                                format='GTiff', width=x_res * geotransform[1], height=y_res * abs(geotransform[5]))

        out_ds = None
        dataset = None  # remove resources

        # read the shapefile
        driverName = "ESRI Shapefile"
        drv = ogr.GetDriverByName(driverName)
        dataSource_in = drv.Open(output_features, 0)  # 0 means read-only. 1 means writeable.
        layer = dataSource_in.GetLayer(0)
        featureCount = layer.GetFeatureCount()
        sourceprj = layer.GetSpatialRef()

        for i in range(layer.GetFeatureCount()):
            feature = layer.GetFeature(i)
            geometry = feature.GetGeometryRef()
            (minX, maxX, minY, maxY) = geometry.GetEnvelope()
            dataSource_out = drv.CreateDataSource(Temp_polygon_shp_for_clipping_path)
            layer2 = dataSource_out.CreateLayer(Temp_polygon_shp_for_clipping_path, sourceprj)
            layer2.CreateFeature(feature)
            attrs = feature.GetField(field_name)
            feature.Destroy()
            dataSource_out.Destroy()
            out_ds = gdal.Translate(Hi_res_clipped_raster_path2,
                                    Hi_res_raster_path,
                                    projWin=[minX, maxY, maxX, minY])
            out_ds = None
            dataset = gdal.Open(Hi_res_clipped_raster_path2,
                                gdal.GA_ReadOnly)
            hist = dataset.GetRasterBand(1).GetDefaultHistogram()
            buckets = hist[3]
            geotransform = dataset.GetGeoTransform()
            dataset = None
            area = geotransform[1] * abs(geotransform[5])
            numList = [outWorkspace, str(attrs), ".txt"]
            seperator = ''
            sum = 0
            filename1 = seperator.join(numList)
            if os.path.exists(filename1):
                os.remove(filename1)
            else:
                ""
            file1 = open(filename1, "a")
            # L = [str(attrs)]
            # seperator = ''
            file1.write(str(attrs))
            for h in range(len(buckets)):
                if buckets[h] > 0:
                    buckets[h] = buckets[h] * area
                    sum = sum + buckets[h]
            for h in range(len(buckets)):
                L = [",", str(buckets[h])]
                seperator = ''
                file1.write(seperator.join(L))
            file1.close()
            # print("{} {} {}".format(i, " of ", layer.GetFeatureCount()))

        dataSource_in.Destroy()  # source
        print("--- %s seconds ---" % (time.time() - start_time))
        return
