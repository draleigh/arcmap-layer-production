#-------------------------------------------------------------------------------
# Name:        append_TRS_values_to_parcel_data.py (Append TRS Values to Parcel Features)
# Purpose:      This script acquires a polygon parcel dataset within a specified area
#                   and adds a field that will contain all of the Township, Range, 
#                   and Section (TRS) values from polygons within a Public Land Survey (PLS) 
#                   dataset that overlap with the parcels. 
#                   
#                   This script has code blocks to excise analysis for parcels smaller
#                   than a certain size and for parcels greater than a certain size which 
#                   incur the most amount of PLS polygon intersections.
#
#
# Author:      Daniel Raleigh
#
# Created:     26 October 2022
# Copyright:   (c) daraleig 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------



# Import modules and packages
import arcpy,os,time,datetime,copy                                                          # necessary modules
from datetime import date, timedelta                                                        # extract submodules
from arcpy import env                                                                       # extract submodules
from arcpy.sa import *                                                                      # import the Spatial Analyst toolbar
arcpy.CheckOutExtension("Spatial")                                                          # check out the Spatial Analyst toolbar

# Date Management

start_time = time.time()                                                                    # define the start time of the script
today = date.today()                                                                        # define the date of the script's run
today_year = today.year                                                                     # define the year of the script's run
today_month = today.month                                                                   # define the month of the script's run
today_day = today.day                                                                       # define the day of the script's run
today_year_str = today.strftime("%Y")                                                       # produce the string value of the script's run date year
today_month_str = today.strftime("%m")                                                      # produce the string value of the script's run date month
today_day_str = today.strftime("%d")                                                        # produce the string value of the script's run date day
today_full_str = today_year_str + today_month_str + today_day_str                           # set up string value of the script's run date (e.g. for January 5, 2002: 20020105
#print(today_full_str)                                                                      # print out today_full_str in the terminal

# Data Locations
Parcel_Data = r"*folderpath*\ParcelProcessing.gdb\Input_Parcel_Data"                        # define location of input parcel data
PLS_Section = r"*folderpath*\pls_sect_data"                                                 # define location of feature class with TRS information
Parcel_Processing_GDB = r"*folderpath*\ParcelProcessing.gdb"                                # define location of geodatabase in which product will be sent

# Set up feature layers and add appropriate field

arcpy.MakeFeatureLayer_management(Parcel_Data, "Parcel_Data")                                               # make a temporary layer for the input data
arcpy.MakeFeatureLayer_management(PLS_Section, "PLS_Section")                                               # make a temporary layer for the feature class with TRS info

Parcel_Data_Addition = os.path.join(Parcel_Processing_GDB, 'Parcel_Data_Addition'+'_' + today_full_str)     # set up a path for the shapefile which will have the new field

# Select only the features that are above a certain size
#   This 'Threshold' value is up to the user. Some parcels are so small that they
#   may not be worth investigating. If unnecessary, adjust the script to skip this step.  
Threshold = 8093.71                                                                                         # square meters for 1 acre: 4046.86, sq m for 2 acres: 8093.71
Size = "Shape_Area >= {}".format(Threshold)                                                                 # set up the expression that will be used to select parcel size
arcpy.SelectLayerByAttribute_management('Parcel_Data', "NEW_SELECTION", Size)                               # use the 'SelectLayerByAttribute_management' function to select parcels greater than the specified size
arcpy.CopyFeatures_management('Parcel_Data', Parcel_Data_Addition)                                          # copy the "finalized" product to add the new field to the previously-defined file path
arcpy.MakeFeatureLayer_management(Parcel_Data_Addition, 'TRS_Add')                                          # make a temporary layer for the input data
# Add the field
inFeatures = 'TRS_Add'                                                                                      # define the inFeatures
fieldName1 = 'TRS'                                                                                          # define the fieldName
fieldType1 = "TEXT"                                                                                         # define the fieldType
fieldPrecision1 = ""                                                                                        # define fieldPrecision (in this case, empty)
fieldScale = ""                                                                                             # define the fieldScale (in this case, empty)
fieldLength1 = 2000                                                                                         # this may need to be very large to account for multiple intersections
fieldAlias1 = 'TRS'                                                                                         # define the fieldAlias
arcpy.management.AddField(inFeatures, fieldName1, fieldType1, fieldPrecision1, fieldScale, fieldLength1, fieldAlias1)   # add the field with the defined attributes


print('Adding a new field took %s seconds...' % round(time.time() - start_time))                                 # in case of a large dataset, use this as a benchmark
print('Initiating addition of TRS values to the new field...')
# select just the parcels smaller than a certain size
Expression = "Shape_Area < 11700000"                                                                        # in case of datasets with VERY large parcels, some will have so many intersections that the field of added TRS values will be massive; this reduces the number of parcels slightly to remove the largest from the analysis
arcpy.SelectLayerByAttribute_management("TRS_Add", "NEW_SELECTION", Expression)                             # select parcels based on the previous expression

parcel_count = int(arcpy.GetCount_management('TRS_Add').getOutput(0))                                       # calculate the number of parcels being edited


# Begin nested cursor series
#   This code block begins an iteration over all polygons within the 'TRS_Add' layer.
#   The general flow of this nested series is as follows:
#       1. A 'TRS_Add' polygon is selected based on an iterable expression
#       2. This selected polygon is used to select all intersecting polygons within the 'PLS_Section' layer
#       3. A FOR loop produces a string of all values from the 'TRS_SEARCH' field within the 'PLS_Section' polygons
#           A) This string is saved to a variable
#       4. An UpdateCursor class is called to update the 'TRS' field within the 'TRS_Add' polygon from the first step
#       5. The initial loop repeats until it completes all rows of the initial SearchCursor
n = int(0)                                                                                                  # set the start value of the rows
with arcpy.da.SearchCursor("TRS_Add", ['OBJECTID']) as cursor:                                              # start an iteration with SearchCursor
    for entry in cursor:                                                                                    # iterate with the 'OBJECT_List' list entries
        n += 1                                                                                              # add integer value of 1 to every prior value of 'n' within this code block
        Expression = "OBJECTID = {}".format(entry[0])                                                       # set up an iterable expression with the first value of the entry (the value in the row in the field 'OBJECTID')
        stringA = ''                                                                                        # set up an empty string for the expression
        arcpy.SelectLayerByAttribute_management("TRS_Add", "NEW_SELECTION", Expression)                     # use the 'SelectLayerByAttribute_management' function with the 'TRS_Add' layer for "NEW_SELECTION" with the expression defined previously
        arcpy.SelectLayerByLocation_management("PLS_Section", "INTERSECT", "TRS_Add", "", "NEW_SELECTION")  # use the 'SelectLayerByLocation_management' function to select from 'PLS_Section' layer for all features that intersect selected features within 'TRS_Add'
        with arcpy.da.SearchCursor("PLS_Section", ['OBJECTID', 'TRS_SEARCH']) as cursor2:                   # utilize a second, nested SearchCursor to iterate over the 'PLS_Section' layer according to 'OBJECTID' and 'TRS_SEARCH' fields
            for row in cursor2:                                                                             # set up a FOR loop to investigate each row within the cursor2
                str_row1 = str(row[1])                                                                      # convert the data in the second field within the row to be a string value
                stringA = stringA + ", " + str_row1                                                         # add each iteration of str_row1 to the stringA string; while running in Python window in ArcMap 10.8, this needed "str_row[3:-3]" for some reason
                stringB = stringA[2:]                                                                       # remove the ", " from the start of stringA once it has completed its loop
                #print(type(stringB))                                                                       # print the statement to the terminal, if desired
            print(n,"of {}:".format(parcel_count), stringB)                                                 # print a statement to the terminal with the index value of the rows in 'TRS_Add' and the data that will be added to the new 'TRS' field
        with arcpy.da.UpdateCursor("TRS_Add", ['TRS']) as cursor3:                                          # set up an UpdateCursor to update the 'TRS' field by iterating over the 'TRS_Add' feature class
            for row3 in cursor3:                                                                            # set up a FOR loop to investigate each row within cursor3
                row3[0] = stringB                                                                           # define the value of the entry that will be added to the row (as of 2 December 2022, removed the str(stringB) because it was already a string value)
                #print(row3)                                                                                # print the entry to be added to the terminal, if desired
                cursor3.updateRow(row3)                                                                     # update the current row in the table according to stringB

arcpy.SelectLayerByAttribute_management("TRS_Add", "CLEAR_SELECTION")                                       # clear the selection on 'TRS_Add'

# Display time taken just for fun:
print('This script took %s seconds...' % round(time.time() - start_time))                                   # print the statement on time taken to the terminal
