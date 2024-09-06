'''
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
'''
import os
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.patches as patches
from pyproj import Transformer
import tarfile
import requests
from io import BytesIO
from datetime import datetime

# Retrieve the current file path
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
save_path = os.path.join(current_dir, 'MappingElements')

################################################
# DEFINE WHAT NWS HAZARDS WE WANT TO WORK WITH
################################################

# Creates a library of the Hazards we want to use this code to display.
hazard_library = pd.DataFrame({
    'Name': ['None', 'Rip Current', 'Beach Hazards'],
    'PHENOM': ['None', 'RP', 'BH'],
    'SIG': ['None', 'S', 'S'],
    'SigType': ['None', 'Statement', 'Statement'],
    'Color': ['None', '#40E0D0', '#40E0D0']
})

################################################
# SET UP THE SHAPEFILES
################################################

# URL to download the latest NWS alert shapefiles
tar_gz_url = 'https://tgftp.nws.noaa.gov/SL.us008001/DF.sha/DC.cap/DS.WWA/current_all.tar.gz'

# Download the latest NWS alert shapefiles
response = requests.get(tar_gz_url)
save_path = os.path.join(current_dir, 'MappingElements') ###!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! IF USING JUPYTER: you may need to set savepath = [the MappingElements folder file path]
if response.status_code == 200:
    with tarfile.open(fileobj=BytesIO(response.content), mode="r:gz") as tar:
        tar.extractall(path=save_path)
else:
    raise Exception(f"Failed to download file from {tar_gz_url}, status code: {response.status_code}")

# Save the NWS alert shapefiles
NWS_shapefile_path = os.path.join(save_path, 'current_all.shp') ###!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! IF USING JUPYTER: you may need to modify this line to be "NWS_shapefile_path = '[replace brackets and this text with filepath to the MappingElements folder]/current_all.shp'

# File path to the mapping shapefiles
state_shapefile_path = os.path.join(save_path, 'NYS Shorline.shp') ###!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! IF USING JUPYTER: you may need to paste the full path name for this shapefile
counties_path = os.path.join(save_path, 'NYS Counties.shp') ###!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! IF USING JUPYTER: you may need to paste the full path name for this shapefile
USstates_path = os.path.join(save_path, 'US StatesCoastlines.shp') ###!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! IF USING JUPYTER: you may need to paste the full path name for this shapefile
world_path = os.path.join(save_path, 'Worlds-32116.shp') ###!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! IF USING JUPYTER: you may need to paste the full path name for this shapefile

# Load all the shapefiles
state_gdf = gpd.read_file(state_shapefile_path)
USstates_gdf = gpd.read_file(USstates_path)
counties_gdf = gpd.read_file(counties_path)
hazards_gdf = gpd.read_file(NWS_shapefile_path)
world_gdf = gpd.read_file(world_path)

# Convert all shapefile coordinate reference systems to EPSG:32116
target_crs = 'EPSG:32116'
state_gdf = state_gdf.to_crs(target_crs)
USstates_gdf = USstates_gdf.to_crs(target_crs)
counties_gdf = counties_gdf.to_crs(target_crs)
hazards_gdf = hazards_gdf.to_crs(target_crs)
world_gdf = world_gdf.to_crs(target_crs)

################################################
# Set up the lat/lon bounds of the map
################################################

# Convert latitude/longitude bounds to EPSG:32116 coordinates
lat_min, lat_max = 40.4, 45.6
lon_min, lon_max = -80, -71.2

# Initialize transformer from EPSG:4326 (lat/lon) to EPSG:32116
transformer = Transformer.from_crs("EPSG:4326", target_crs, always_xy=True)

# Convert bounds to EPSG:32116 coordinates
x_min, y_min = transformer.transform(lon_min, lat_min)
x_max, y_max = transformer.transform(lon_max, lat_max)

#######################################################
# Loop through the NWS Hazards Library we already set up
#######################################################

# Loop through all PHENOM values in the library
for input_phenom in hazard_library['PHENOM'].values:
    fig, ax = plt.subplots(figsize=(10, 10))

    # Set background color
    ax.set_facecolor('#a6cee3')  

    # Plot each layer in order
    world_gdf.plot(ax=ax, color='#eeeeee', edgecolor='black') 
    USstates_gdf.plot(ax=ax, color='#eeeeee', edgecolor='black')
    counties_gdf.plot(ax=ax, color='white', edgecolor='black')
    state_gdf.plot(ax=ax, color='none', edgecolor='black', linewidth=2)

    hazard_info = hazard_library[hazard_library['PHENOM'] == input_phenom].iloc[0]
    name = hazard_info['Name']
    phenom = hazard_info['PHENOM']
    sig = hazard_info['SIG']
    color = hazard_info['Color']
    
    # Check if input PHENOM is 'None'
    if input_phenom == 'None':
        ax.text(
            x=0.47, y=0.425,
            s="There are no active weather\nalerts for New York State.",
            ha='center',
            va='center',
            fontsize=18,
            color='black',
            alpha=0.5,
            transform=ax.transAxes,
            bbox=dict(
                facecolor='white', 
                edgecolor='none', 
                alpha=1,
                boxstyle='round,pad=0.4',
                zorder=10
            )
        )
        
    # Otherwise map each hazard    
    else:
        # Filter weather hazards within New York State
        hazards_within_ny = gpd.sjoin(hazards_gdf, state_gdf, how='inner', predicate='intersects')
        # Filter hazards by attributes PHENOM and SIG
        filtered_hazards = hazards_within_ny[(hazards_within_ny['PHENOM'] == phenom) & (hazards_within_ny['SIG'] == sig)]
            
        # Plot hazards if present
        if not filtered_hazards.empty:
            filtered_hazards.plot(ax=ax, color=color, alpha=1, edgecolor='none')
            counties_gdf.plot(ax=ax, color='none', edgecolor='black')
            state_gdf.plot(ax=ax, color='none', edgecolor='black', linewidth=2)
            
            # Add legend
            legend_handle = patches.Patch(color=color, label=f'{name} {hazard_info["SigType"]}')
            ax.legend(handles=[legend_handle], title="Alert Type", loc='lower left', bbox_to_anchor=(0.1, 0.075), fontsize=15, title_fontsize=18)
        
        # Otherwise state that there are none of the specific hazard type present    
        else:
            ax.text(
                x=0.47, y=0.425,
                s=f'There are no {name}\nalerts for New York State.',
                ha='center',
                va='center',
                fontsize=18,
                color='black',
                alpha=0.5,
                transform=ax.transAxes,
                bbox=dict(
                    facecolor='white', 
                    edgecolor='none', 
                    alpha=1,
                    boxstyle='round,pad=0.4',
                    zorder=10
                )
            )

#######################################################
# Set up the title and the generated time
#######################################################


    #In the following lines of code i have TWO add map title sections
    #This is so i can shift the box to be centered around the titel AND the generated date/time text 
    
    # Add map title - JUST THE BOX
    ax.text(
        x=0.5, y=0.96,  # Position near the top of the plot
        s="            New York State Weather Alerts            ",
        ha='center',
        va='top',
        fontsize=20,
        fontweight='bold',
        color='black',
        alpha=0, #SET IT SO THE TEXT IS INVISIBLE
        bbox=dict(
            facecolor='white',
            edgecolor='black',
            boxstyle='round,pad=0.6'
        ),
        transform=ax.transAxes,
        zorder=10
    )
    
    # Add map title - JUST THE TEXT
    ax.text(
        x=0.5, y=0.97,  # Position near the top of the plot
        s="            New York State Weather Alerts            ",
        ha='center',
        va='top',
        fontsize=20,
        fontweight='bold',
        color='black',
        bbox=dict(
            facecolor='white',
            edgecolor='black',
            boxstyle='round,pad=0.6',
            alpha=0 #SET IT SO THE BOX IS INVISIBLE
        ),
        transform=ax.transAxes,
        zorder=10
    )
    
    # Add Map generated time
    current_time = datetime.now().strftime('%I:%M %p')
    current_date = datetime.now().strftime('%B %d, %Y')
    ax.text(
        x=0.5, y=0.915,  # Position near the bottom of the plot
        s=f"Map generated at {current_time} on {current_date}",
        ha='center',
        va='center',
        fontsize=12,
        color='black',
        bbox=dict(
            facecolor='none',
            edgecolor='none',
        ),
        transform=ax.transAxes,
        zorder=10
    )

#######################################################
# finalize and save the things
#######################################################

    # Set plot boundaries
    ax.set_xlim([x_min, x_max])
    ax.set_ylim([y_min, y_max])

    # Remove axis labels and tick marks
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('')
    ax.set_ylabel('')
    
    # Save the plot
    output_map_path = os.path.join(current_dir, f'Current_NY_{name}_Alert.png') ###!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! IF USING JUPYTER: you may need to modify this line to be " output_map_path = f'[replace brackets and this text with file path to NWS_Alerts folder that you downloaded]/Current_NY_{name}_Alert.png'
    plt.savefig(output_map_path)
    plt.close()  # Close the figure to avoid memory issues

    print(f"Plot saved as {output_map_path}")
