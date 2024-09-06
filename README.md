Title: NWSAlertMapper
Author: Ethan Burwell
Last Updated: September 6, 2024

About: This code automatically retrieves the latest NWS alert polygons from https://tgftp.nws.noaa.gov/SL.us008001/DF.sha/DC.cap/DS.WWA/current_all.tar.gz
The code contains a library of NWS Hazards that will be mapped. The library of hazards can be edited manually in lines 28-37 of this code. The code
Then loops through all the hazards in the library and saves each hazard as a separate .png map in the current directory as this .py file.

This file requires four mapping shapefiles:
- one outline of the NYS border/shoreline
- one outline of NYS counties
- one of world country borders
- one of us state outlines

The code assumes that these shapefiles are stored in a folder called MappingElements and that the MappingElements folder is stored in the same directory
as the python script. 
