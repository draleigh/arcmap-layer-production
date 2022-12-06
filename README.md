# arcmap-layer-production
 This repository contains examples of scripts that are used to produce ArcMap feature classes of various types.

"forest_stand_groupings_layer_production.py" (Packages Required: os,arcpy,time,datetime,copy)

Issue: 

I produce an annual batch of maps for members of the public that display potential hunting areas in Minnesota. I found that I had to conduct a series of manual polygon selections, field additions, and calculations that took a decent amount of time. I also found that the input feature class was updated on an irregular basis, but reproducing the same steps to complete the final product for the most updated display was time-consuming. I wanted to find a way to conduct all fo the workflow with a single script that I could easily load to an ArcMap or ArcPro document at successive dates (depending on whether the input layer was updated).

Solution: 

    1. The script draws in data from the forest inventory feature class, a selector feature class, and a feature class with work areas. The script also defines the location of the active geodatabase that will be utilized.

    2. All "active" selector features (this could be parking lots, trails, roads, etc.) are selected, and those selector features are used to select the work areas in turn. Those are listed and are utilized to select all forest stand polygons within the defined feature class within the selector areas. 

    3. This selected batch of forest stand inventory polygons ('ForestStandSelection') is then sub-set to screen out all tree types that are not required. Two new fields ('StandAge' and 'Groupings') are added to the new, reduced feature class ('ForestStandSelection_Reduced').

    4. Three UpdateCursor classes are set up to populate 'StandAge' and 'Groupings', respectively, with which are used to prompt the third UpdateCursor to remove rows that are not applicable.

    5. The ultimate product is dissolved into multipart features for sourcing in ArcMap documents. 

#___________________________________________________________________________________________________________________________________


"first_nations_ownership_layer_production.py" (Packages Required: os,arcpy,time,datetime,copy,openpyxl)

Issue: 

I produce an annual batch of maps for members of the public that display area for hunting in Minnesota. The maps display walkable areas on public land, but often include public area boundaries that border parcels owned by First Nations/Native American tribal entities. To ensure that members of the public do not trespass, I am required to carefully assess parcel data to confirm that private land is prominently displayed. 

However, the ocular inspection of all parcels on 250+ maps is laborious, and I wanted to find a more effective way to display First Nations land without having to conduct manual inspections of parcels across all of the mapped areas. It is clear that the variability of landowner names presents a challenge to find a concise collection of names, but some public ownership titles (e.g. "Indian Land", "Indian Reservation", "U S Indian Land", etc.) will be more consistent across broader stretches of territory. I determined to set up a script that would incorporate known terms/keywords for First Nations ownership, and then produce a layer which selected all parcels that contained the keywords that had been prepared for the script in an Excel workbook. The workbook can be adjusted over time and easily sorted when necessary to provide a dynamic input file for successive iterations of this layer's production.   

Solution:

    1. Import modules and assign variables to file and geodatabase paths.

    2. Confirm all selector features which will be used to select parcel data, then iterate over all selector features to make a complete list. Produce a layer of selected parcels within a specified distance of the selector features. 

    3. Open the Excel workbook which contains the terms that have been collected for First Nations ownership, then iterate over the workbook sheet to find the appropriate entries to collect a list of 'keyWords'.

    4. Set up a series of expressions that will be used to query the parcels whose owners are sought after. Apply the combined expression to the selected parcels, then dissolve the remaining parcels to produce a final layer that can be utilized for map production.

#___________________________________________________________________________________________________________________________________

"private_ownership_layer_production.py" (os,arcpy,time,datetime,copy,openpyxl)

Issue:

I produce an annual batch of maps for members of the public that display areas for hunting in Minnesota. The maps display walkable areas on public land, but often include public area boundaries that border private property. To ensure that members of the public do not trespass, I am required to carefully assess parcel data to confirm that private land is prominently displayed. 

However, the ocular inspection of all parcels on 250+ maps is laborious, and I wanted to find a more effective way to display private land without having to conduct manual inspections of parcels across all of the mapped areas. It is clear that the variability of private landowner names presents a challenge to find a concise collection of names, but some public ownership titles (e.g. "State Government", "County Government", "Yurok Tribe", etc.) will be more consistent across broader stretches of territory. I determined to set up a script that would incorporate known terms/keywords for public and First Nations ownership, and then produce a layer which selected all parcels except those that contained those entries. The workbook can be adjusted over time and easily sorted when necessary to provide a dynamic input file for successive iterations of this layer's production.   

Solution:

    1. Import modules and assign variables to file and geodatabase paths.

    2. Confirm all selector features which will be used to select parcel data, then iterate over all selector features to make a complete list. Produce a layer of selected parcels within a specified distance of the selector features. 

    3. Open the Excel workbook which contains the terms that have been collected for public and First Nations ownership, then iterate over the workbook sheet to find the appropriate entries to collect a list of 'keyWords'.

    4. Set up a series of expressions that will be used to query out the parcels whose owners are not sought after. Apply the combined expression to the selected parcels, then dissolve the remaining parcels to produce a final layer that can be utilized for map production. 


#______________________________________________________________________________________________________________________


"lakeshore_parcel_selection_layer_production.py" (os,arcpy,time,datetime,copy,openpyxl)

Issue:

I was tasked with assisting a colleague who wanted to contact landowners with lakeshore property (or property in very close proximity to lakes). This colleague wanted to be able to provide lake-specific IDs that could be used to change selections based on new information. While manually adding those values is possible, it is also time-consuming. I designed a script that would acquire the lake-based IDs, from a curated Excel workbook (.xlsx), set up an expression to select all lakes with those defined values, and then select all parcels that intersected with those lakes to produce a final product.

Solution:

    1. Import modules and assign variables to file and geodatabase paths.

    2. Open the Excel workbook which contains the lake ID values, iterate over the workbook sheet to find the appropriate entries to collect a list of IDs. 

    3. Set up an expression that will be used to query the lake feature class. This query selects lakes with matching lake ID values, then uses those selected lakes to select all parcels that intersect with those lakes (and produces a final feature class from the ultimate parcel selection).
        A) The final step for "INTERSECT" with the lake boundaries can be adjusted if the user wishes to include parcels at a specific distance beyond the lake boundary. 



#_______________________________________________________________________________________________________________________


"append_TRS_values_to_parcel_data.py" (arcpy,os,time,datetime,copy)

Issue:

I am tasked annually with collecting, consolidating, and merging parcel data according to ownership names and address information. Colleagues determined that it would be helpful to know the Township, Range, and Section (TRS) values from Public Land Survey (PLS) polygons that overlap with all of these parcel polygons. Instead of manually entering the information or joining the data manually, I decided to write a script that would append the information to a new field in the attribute table of the parcel dataset.

Solution: 

    1. Import modules and assign variables to file and geodatabase paths.

    2. Adjust the size of parcels that will receive TRS data. This can be adjusted prior to running the script (or taken out entirely).

    3. Add a new field ['TRS'] to hold the Township, Range, and Section values.

    4. The script processes a series of nested cursor classes.
        Begin nested cursor series (this code block begins an iteration over all polygons within the 'TRS_Add' layer):
        A) A 'TRS_Add' polygon is selected based on an iterable expression
        B) This selected polygon is used to select all intersecting polygons within the 'PLS_Section' layer
        C) A FOR loop produces a string of all values from the 'TRS_SEARCH' field within the 'PLS_Section' polygons
            - This string is saved to a variable
        D) An UpdateCursor class is called to update the 'TRS' field within the 'TRS_Add' polygon from the first step
        E) The initial loop repeats until it completes all rows of the initial SearchCursor

    5. The final product comprises the initial parcel data feature class with an additional field which contains TRS values.