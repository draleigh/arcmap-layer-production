# arcmap-layer-production
 This repository contains examples of scripts that are used to produce ArcMap feature classes of various types.

"forest_stand_groupings_layer_production.py" (Packages Required: os,arcpy,time,datetime,copy)

Issue: I produce an annual batch of maps for members of the public that display potential hunting areas in Minnesota. I found that I had to conduct a series of manual polygon selections, field additions, and calculations that took a decent amount of time. I also found that the input feature class was updated on an irregular basis, but reproducing the same steps to complete the final product for the most updated display was time-consuming. I wanted to find a way to conduct all fo the workflow with a single script that I could easily load to an ArcMap or ArcPro document at successive dates (depending on whether the input layer was updated).

Solution: 

    1. 

The script draws in data from the forest inventory feature class, a selector feature class, and a feature class with work areas. The script also defines the location of the active geodatabase that will be utilized.

    2. 

All "active" selector features (this could be parking lots, trails, roads, etc.) are selected, and those selector features are used to select the work areas in turn. Those are listed and are utilized to select all forest stand polygons within the defined feature class within the selector areas. 

    3. 

This selected batch of forest stand inventory polygons ('ForestStandSelection') is then sub-set to screen out all tree types that are not required. Two new fields ('StandAge' and 'Groupings') are added to the new, reduced feature class ('ForestStandSelection_Reduced').

    4. 

Three UpdateCursor classes are set up to populate 'StandAge' and 'Groupings', respectively, with which are used to prompt the third UpdateCursor to remove rows that are not applicable.

    5. 

The ultimate product is dissolved into multipart features for sourcing in ArcMap documents. 