#-------------------------------------------------------------------------------
# Name:        private_ownership_layer_production_xlsx.py (Private Ownership Layer Production)
# Purpose:      This script examines all parcels within 2km of all active Selector features 
#                   (where in a field named 'RequiresDeletion', 'RequiresDeletion = "No"') 
#                   before selecting only those parcels that do not contain specific terms which 
#                   indicate public or First Nations ownership.
#                   Those terms are acquired from a prepared Excel (.xlsx) document and are utilized to produce
#                   a dissolved product of private parcel ownership for display on maps. 
#
# Author:      draleigh
#
# Created:     15 August 2022
# Copyright:   (c) draleigh 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------


# Steps:
#  -define the folder path of the parcels feature class 
#  -Define the Selector feature class folder path for the current year
#  -select all parcels within 2km of the "active" Selector features
#  -produce an expression to only select parcels that do not have specific ownership designations/names
#  -dissolve the selected parcels according to multipart features along lines


# Import Modules and Extensions
import os,arcpy,time,datetime,copy,openpyxl                                                 # list of required modules
from datetime import date, timedelta                                                        # extract submodules
from arcpy import env                                                                       # extract submodule
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
#print(today_full_str)                                                                      # print out today_full_str in the terminal if desired


# Define Data Locations and Other Variables
GDB = r"*folderpath*\Ownership.gdb"                                                                     # define the location of the project database
AllParcels = r"*folderpath*\parcel_FC"                                                                  # define the location of the Minnesota parcel dataset
Selector = r"*folderpath*\selector_feature_class"                                                       # define the location of the current dataset which contains the selection features
Ownership_DataFolder = r"*folderpath*\Data"                                                             # define the location of the "Data" subfolder (if necessary)
Input = r"*folderpath*\Public_Property_Terms.xlsx"                                                      # define the location of the .xlsx file with the search terms



# Set up layers and feature classes (with file paths)
block_start = time.time()                                                                               # set the start time of the code block
print('Setting up file paths, making feature layers.')                                                  # print a statement to the terminal indicating what steps will be taken next
Selector_Features = []                                                                                  # set up an empty list to receive Selector feature names
arcpy.MakeFeatureLayer_management(AllParcels, 'Parcels')                                                # Make a temporary layer for full set of parcels
arcpy.MakeFeatureLayer_management(Selector, 'Selector')                                                          # Make temporary layer for Hunter Walking Trails
Parcel_selection_path = os.path.join(GDB, 'Parcel_Selection_' + today_full_str)                         # Define path of transitional feature class with selected parcels within specified distance of Selector features
Parcel_selection_reduced_path = os.path.join(GDB, 'ParcelSelection_Reduced_' + today_full_str)          # Define path of parcel shapefile after running selection for non-public entities
Parcel_selection_dissolved_path = os.path.join(GDB, 'PrivateParcelSelection_Dissolved_' + today_full_str) # Define path of the dissolved layer of non-public entities
#print(Parcel_selection_path)                                                                           # print the path of the parcel selection feature class, if desired
arcpy.SelectLayerByAttribute_management('Selector', "CLEAR_SELECTION")                                  # clear the selection on the 'Selector' layer to confirm that the layer has no selection
print('Prep work complete (%s taken).\n' % round(time.time() - block_start))                            # print a statement to the terminal indicating the steps that have completed

# Find all entries in 'OWNER_NAME' field
block_start = time.time()                                                                               # set the start time of the code block
print('Confirming active trails, setting aside parcel selections.')                                     # print a statement to the terminal indicating next steps
arcpy.SelectLayerByAttribute_management('Selector', "NEW_SELECTION", "Requires_Deletion = 'No'")        # Select features according to the 'Requires_Deletion' field; this may require adjustments to the Selector shapefile ahead of time
with arcpy.da.SearchCursor('Selector', ['TRAIL_NAME']) as cursor:                                       # set up a SearchCursor to iterate over the 'Selector' layer according to the 'TRAIL_NAME' field
    for row in cursor:                                                                                  # set up a FOR loop to investigate each row within the cursor
        print('Trail Name: {}'.format(row[0]))                                                          # print a statement to the terminal that contains each Selector name
        Selector_Features = Selector_Features + ['{}'.format(row[0])]                                   # append each row's trail name to the 'Selector_Features' list; this list will be unsorted
print('Number of selector features: ', len(Selector_Features))                                          # print a statement to the terminal with the number of Selector features in the list
arcpy.SelectLayerByLocation_management('Parcels', "WITHIN_A_DISTANCE", 'Selector', '2 kilometers', "NEW_SELECTION")  # Select all parcels within 2km of the "active" Selector
arcpy.CopyFeatures_management('Parcels', Parcel_selection_path)                                         # copy the features from 'Parcels' to the predefined 'Parcel_selection_path' file
arcpy.MakeFeatureLayer_management(Parcel_selection_path, 'Parcel_Selection')                            # make a temporary layer for the selected parcels
arcpy.SelectLayerByAttribute_management('Parcels', "CLEAR_SELECTION")                                   # Clear selection on the full parcel layer
print('''Parcels selected and set aside (%s taken), 
proceeding with public and First Nations keyword selection from Excel document.\n''' % (round(time.time() - block_start))) # print a statement to the terminal indcating time taken for block to process and next steps

# Acquire keywords and proceed to setting up definition queries
block_start = time.time()                                                                               # set the start time of the code block
keyWords_Full = []                                                                                      # set up a list of keyWords to be used for selection
wb = openpyxl.load_workbook(Input)                                                                      # use the openpyxl module to load the predefined workbook
sheet = wb['Public_Terms']                                                                              # define the sheet within the workbook that will be utilized
for val in sheet.iter_rows(min_col=1):                                                                  # set up a FOR loop to iterate over rows in the sheet for the first column (in this case, the terms are in the first column, the only column with data in the sheet)
    keyWords_Full.append(val[0].value)                                                                  # add the initial value from that row (limited to start a 'min_col=#') to the 'keyWords_Full' list
    print(val[0].value)                                                                                 # print statement to the terminal with the value being appended
keyWords = keyWords_Full[1:]                                                                            # remove the first value in the list (the header of the column, if necessary)
#print(keyWords)                                                                                       # print the list to the terminal (if desired)

# Fields for dissolution and final table

# Define the list of owner fields that could contain owner information
#   These fields will be investigated for the key terms that relate to public or First Nations ownership
#ownerFields = ['OWNER_NAME', 'TAX_NAME', 'OWNER_MORE', 'TAX_ADD_L1']                                # this is the full list of fields that do and could potentially contain ownership designations/names
ownerFields = ['OWNER_NAME', 'TAX_NAME']                                                            # this list contains fields that are supposed to only contain ownership designations/names


# Set up empty strings for the expressions
Owner_Exp = ''                                                                                      # set up a string for Owner expression with 1st field (to combine with Tax expression)
Tax_Exp = ''                                                                                        # set up a string for Tax expression with 1st field (to combine with Owner expression)
Full_Exp = ''                                                                                       # set up a string to receive the expression combinations

# Set up Owner_Exp
for i in range(len(keyWords)):                                                                      # set up a FOR loop to iterate over each entry in the keyWords list
    Owner_Exp = Owner_Exp + str(ownerFields[0] + " <> '{}' And ".format(keyWords[i]))               # append each slice of the keyWords list with appropriate syntax for the ultimate SQL expression
Owner_Exp = Owner_Exp + str(ownerFields[0] + ' IS NOT NULL')                                        # once the FOR loop has completed, add a final expression

# Set up Tax_Exp
for k in range(len(keyWords)):                                                                      # set up a FOR loop to iterate over each entry in the keyWords list
    Tax_Exp = Tax_Exp + str(ownerFields[1] + " <> '{}' And ".format(keyWords[k]))                   # append each slice of the keyWords list with appropriate syntax for the ultimate SQL expression
Tax_Exp = Tax_Exp + str(ownerFields[1] + ' IS NOT NULL')                                            # once the FOR loop has completed, add a final expression

Full_Exp = "("+Owner_Exp+") Or ("+Tax_Exp+")"                                                       # complete the expression by combining the four partial expressions (Owner and Tax)
##print(Full_Exp)
print('Definition query has been completed (%s seconds).\n' % (time.time() - block_start))          # print a statement to the terminal which indicates the actions which have been completed


print('Starting selection of non-public parcels...')
block_start = time.time()                                                                           # set the start time of the code block 
arcpy.SelectLayerByAttribute_management('Parcel_Selection', "NEW_SELECTION", Full_Exp)              # select all polygons within 'Parcel_Selection' according to the Full_Exp
# Dissolve the non-public parcels to produce pre-defined feature class by name with multipart options, dissolving along lines
arcpy.Dissolve_management('Parcel_Selection', Parcel_selection_dissolved_path,
                          "", "", 'MULTI_PART', 'DISSOLVE_LINES')

print('Finished with dissolving. Check for a shapefile named MNPrivateParcelSelection_Dissolved_' + today_full_str) # print statement to the terminal with the expected name of the product

# Display time taken just for fun:
print('This script took %s seconds...' % round(time.time() - start_time))                           # print statement to the terminal with time taken to complete the script
