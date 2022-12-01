#-------------------------------------------------------------------------------
# Name:        forest_stand_groupings_layer_production.py
# Purpose:      For acquiring forest stand polygon data within Work Areas that contain certain features,
#                   selecting all forest stand polygons with proper 'MN_CTYPE' entries,
#                   adding appropriate columns for 'MN_CTYPE' groupings, calculating
#                   stand age for the present year, then dissolving the polygons
#                   according to groups.
#
# Author:      draleigh
#
# Created:     2 August 2022
# Copyright:   (c) draleigh 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------


# Import modules
import os,arcpy,time,datetime,copy                                                          # list of modules that will be needed
from datetime import date, timedelta                                                        # extract the sub-modules
from arcpy import env                                                                       # extract the sub-module
from arcpy.sa import *                                                                      # import the spatial analyst toolbox
arcpy.CheckOutExtension("Spatial")                                                          # check out the Spatial Analyst extension


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


# Define Data Locations and Other Variables
GDB = r"...\Workspace.gdb"                                                                  # define location of the workspace geodatabase
ForestStandInventory = r"forest_stand_inventory.gdb\dnr_forest_stand_inventory"             # define the location of the forest stand inventory dataset
WorkAreas = r".gdb\dnr_wildlife_workareas"                                                  # define the the location of the work area feature class
Selector = r"Selector.gdb\Selector"                                                         # define the location of the most recent Selector feature class

# Determine the number of areas that will provide data for layer production
Selector_WorkAreas = []                                                                                         # set up a temporary list to hold the areas in question

# Set up list of Work Areas based on Hunter Walking Trail presence
block_start = time.time()                                                                                       # set the start time of the code block
arcpy.MakeFeatureLayer_management(ForestStandInventory, 'ForestStands')                                         # Make a temporary layer for the full forest stand inventory
arcpy.MakeFeatureLayer_management(WorkAreas, 'WorkAreas')                                                       # Make temporary layer for work areas
arcpy.MakeFeatureLayer_management(Selector, 'Selector')                                                         # Make temporary layer for Hunter Walking Trails
FSI_Selection_path = os.path.join(GDB, 'ForestStandSelection'+'_' + today_full_str)                             # define the path name of the feature class which will contain all forest stand polygons
FSI_selection_reduced_path = os.path.join(GDB, 'ForestStandSelection_Reduced' +'_' + today_full_str)            # define the path name of the feature class which will hold the refined collection of forest stand polygons
Expression1 = "Requires_Deletion = 'No'"                                                                      # set up a SQL expression to select all active Selector features (if necessary)
arcpy.SelectLayerByAttribute_management('Selector', "NEW_SELECTION", Expression1)                             # select all features that are active from the full list

arcpy.SelectLayerByLocation_management('WorkAreas', "INTERSECT", 'Selector', 0, "NEW_SELECTION")                # select all areas that intersect with the active Selector features
with arcpy.da.SearchCursor('WorkAreas', ['AREA_NAME']) as cursor:                                               # set up a SearchCursor to iterate over the 'WorkAreas' layer according to the field 'AREA_NAME'
    for row in cursor:                                                                                          # set up a FOR loop to investigate each row within the cursor
        print('{} Work Area'.format(row[0]))                                                                    # print the work area name for each entry found per row (which will be the first entry in the 'AREA_NAME' field)
        Selector_WorkAreas = Selector_WorkAreas + ['{}'.format(row[0])]                                         # append each row's area name to the Selector_WorkAreas list; this list will be unsorted
print('\nForest Stand Inventory processing will require data from {} work areas.\n'.format(len(Selector_WorkAreas))) # print the statement to the terminal indicating progress
arcpy.SelectLayerByLocation_management('ForestStands', "WITHIN", 'WorkAreas', 0, "NEW_SELECTION")               # once the SearchCursor has completed, select all polygons from the 'ForestStands' layer that are "WITHIN" the 'WorkAreas' layer
arcpy.CopyFeatures_management('ForestStands', FSI_Selection_path)                                               # make a copy of the selected 'ForestStands' polygons to be the previously-defined FSI_Selection_path feature class
arcpy.SelectLayerByAttribute_management('WorkAreas', "CLEAR_SELECTION")                                         # clear the selection in 'WorkAreas'
print('Forest stands have been selected (%s seconds to process).' % round(time.time() - block_start))           # print a statement that indicates how long the previous code block took to process
print('Forest stands will now be subset with added fields for ongoing analysis.\n')                             # print a statement to the terminal to indicate the next stage of the script


# Subset the Selector-based Forest Stand Inventory Selection and add appropriate columns
#   These steps make the following selections:
#       1. Subset the Forest Stand Inventory to have only polygons that lie within Work Areas with active Selector features
#       2. Subset that selection to only include specific types of trees (based on 'MN_CTYPE' values)
#       3. Subset that tree-type selection based on other specific criteria
block_start = time.time()
arcpy.MakeFeatureLayer_management(FSI_Selection_path, 'ForestStandSelection')                                   # Make a temporary layer for forest stand inventory
Expression2 = "MN_CTYPE = 12 Or MN_CTYPE = 13 Or MN_CTYPE = 14 Or MN_CTYPE = 82 Or MN_CTYPE = 30 Or MN_CTYPE = 79 Or MN_CTYPE = 71 Or MN_CTYPE = 74 Or MN_CTYPE = 53 Or MN_CTYPE = 62 Or MN_CTYPE = 73" # This expression refers to specific 'MN_CTYPE' values for forest stand species types; the selection was approved by wildlife personnel
arcpy.SelectLayerByAttribute_management('ForestStandSelection', "NEW_SELECTION", Expression2)                   # select all forest stand polygons based on the previously-defined expression
arcpy.CopyFeatures_management('ForestStandSelection', FSI_selection_reduced_path)                               # make a copy of the selected 'ForestStandSelection' polygons to be the previously-defined FSI_selection_reduced_path feature class
arcpy.SelectLayerByAttribute_management('ForestStandSelection', "CLEAR_SELECTION")                              # clear the selection on 'ForestStandSelection'
arcpy.MakeFeatureLayer_management(FSI_selection_reduced_path, 'FSI_Reduced')                                    # make a temporary layer for the reduced forest stand inventory
# Set up attributes for new fields that will be produced, then add the fields:
inFeatures = 'FSI_Reduced'                                                                                      # define a variable for the 'in_table'
fieldName1 = 'Groupings'                                                                                        # define a variable for 'field_name' (field #1)
fieldName2 = 'StangeAge'                                                                                        # define a variable for 'field_name' (field #2, which could have a suffix with the year in question, e.g. "StandAge2022")
fieldType1 = "TEXT"                                                                                             # define a variable for 'field_type' (field #1)
fieldType2 = "SHORT"                                                                                            # define a variable for 'field_type' (field #2)
fieldPrecision1 = ""                                                                                            # define a variable for 'field_precision' (field #1)
fieldPrecision2 = 4                                                                                             # define a variable for 'field_precision' (field #2)
fieldScale = ""                                                                                                 # define a variable for 'field_scale' (to be used for both fields)
fieldLength1 = 25                                                                                               # define a variable for 'field_length' (field #1)
fieldLength2 = ""                                                                                               # define a variable for 'field_length' (field #2)
fieldAlias1 = 'Groupings'                                                                                       # define a variable for 'field_alias' (field #1)
fieldAlias2 = 'StangeAge'                                                                                    # define a variable for 'field_alias' (field #2)

arcpy.management.AddField(inFeatures, fieldName1, fieldType1, fieldPrecision1, fieldScale, fieldLength1, fieldAlias1) # add field #1 to 'FSI_Reduced'
arcpy.management.AddField(inFeatures, fieldName2, fieldType2, fieldPrecision2, fieldScale, fieldLength2, fieldAlias2) # add field #2 to 'FSI_Reduced'
print('Forest stands have been subset and fields have been added (%s seconds to process).' % round(time.time() - block_start))      # print a statement that indicates how long the previous code block took to process
print('Forest stand dataset will now be refined according to species type and age.\n')                          # print a statement to the terminal to indicate the next steps


# Populate 'StangeAge' field values
block_start = time.time()
with arcpy.da.UpdateCursor('FSI_Reduced', ['STAND_AGE', 'SURVEY_YR', 'StangeAge']) as cursor:                   # set up an UpdateCursor to iterate over the 'FSI_Reduced' layer according to the fields 'STAND_AGE', 'SURVEY_YR', and 'StangeAge'
    for row in cursor:                                                                                          # set up a FOR loop to investigate each row within the cursor
        if row[1] > 0:                                                                                          # set up an IF statement to evaluate whether the second value in the row of specified fields ('SURVEY_YR') is greater than 0;
            row[2] = (int(today_year_str) - row[1] + row[0])                                                    # prompt the 'StangeAge' value to be the calculated value of the 'STAND_AGE' added to 'SURVEY_YR' which is subtracted from the current year's value
        else:                                                                                                   # set up an ELSE statement for any entry within 'SURVEY_YR' that is <=0 (0 or <Null>)
            row[2] = 1000                                                                                       # for my purposes, I'm only concerned with display a certain grouping of tree types that are younger than 20 years; I'd prefer that any unknown age be considered too old, and a future expression will prompt these entries to be removed from the dataset
        cursor.updateRow(row)                                                                                   # prompt the cursor to update the row with the values prompted based on the IF statement

# Populate 'Groupings' field values

with arcpy.da.UpdateCursor('FSI_Reduced', ['MN_CTYPE', 'StangeAge', 'Groupings']) as cursor:                    # set up an UpdateCursor to iterate over the 'FSI_Reduced' layer according to the fields 'MN_CTYPE', 'StangeAge', and 'Groupings'
    for row in cursor:                                                                                          # set up a FOR loop to investigate each row within the cursor
        if (row[0] == 12 and row[1] < 20) or (row[0] == 13 and row[1] < 20) or (row[0] == 14 and row[1] < 20) or (row[0] == 82 and row[1] < 20): # set up an IF statement that evaluates the polygons within 'FSI_Reduced' according to the 'MN_CTYPE' and 'StangeAge'
            row[2] = 'Young Forest'                                                                             # if the ELIF statement evaluates to true, populate the third field with 'Young Forest' if the youngest polygons are found to match the 'MN_CTYPE' values, as well
        elif row[0] == 30 or row[0] == 79:                                                                      # set up an ELIF statement to evaluate whether polygons have specific 'MN_CTYPE' values
            row[2] = 'Oak'                                                                                      # if the ELIF statement evaluates to TRUE, populate the third field with 'Oak'
        elif (row[0] == 53 and row[1] < 20) or row[0] == 62 or row[0] == 71 or row[0] == 73 or row[0] == 74:    # set up an ELIF statement to evaluate whether polygons have specific values according to 'MN_CTYPE' and 'StangeAge'
            row[2] = 'Dense Conifer'                                                                            # if the ELIF statement evaluates to TRUE, populate the third field with 'Dense Conifer'
        elif (row[0] == 12 and row[1] >= 20) or (row[0] == 13 and row[1] >= 20) or (row[0] == 14 and row[1] >= 20) or (row[0] == 82 and row[1] >= 20) or (row[0] == 53 and row[1] >= 20): # set up an ELIF statement to evaluate whether polygons have specific values according to 'MN_CTYPE' and 'StangeAge'
            row[2] = 'Remove'                                                                                   # if the ELIF statement evaluates to TRUE, populate the third field with 'Remove'
        cursor.updateRow(row)                                                                                   # once the IF/ELIF statements have processed, update the row of the cursor

# Remove inapplicable polygons

with arcpy.da.UpdateCursor('FSI_Reduced', ['Groupings']) as cursor:                                             # set up an UpdateCursor to iterate over the 'FSI_Reduced' layer according to the 'Groupings' field
    for row in cursor:                                                                                          # set up a FOR loop to investigate each row within the cursor
        if row[0] == 'Remove':                                                                                  # set up an IF statement to evaluate whether the first value within the row (row[0]) is equivalent to 'Remove'
            cursor.deleteRow()                                                                                  # if the IF statement evaluates to TRUE, delete the row
print('Forest stand final product has been completed (%s seconds to process).' % round(time.time() - block_start))   # print a statement that indicates how long the previous code block took to process
print('The final product will now be dissolved according to the "'"Grouping"'" field.\n')                       # print a statement to the terminal indicating the next step in the script.

# Dissolve by 'Groupings' field entries
#
# For my work, I present product layer in ArcMap documents so that each dissolved (multipart) polygon
#   displays its forest grouping type with a label. I don't need to know the individual species, but
#   this next bit can be ignored if it's unnecessary.
FSI_Reduced_Dis_path = os.path.join(GDB, 'ForestStandSelection_Reduced_Dissolved' +'_' + today_full_str)        # define the path name of the feature class which will contain all forest stand polygons
arcpy.management.Dissolve('FSI_Reduced', FSI_Reduced_Dis_path, ['Groupings'], "", "MULTI_PART", "DISSOLVE_LINES")   # dissolve the 'FSI_Reduced' feature class (with all of the populated fields and reduced rows) so that it is multipart and dissolved along lines according to the just-defined FC name


# Display time taken just for fun:
print('This script took %s seconds to complete...' % round(time.time() - start_time))                                    # print a statement to the terminal to indicate how long the script took to fully process







