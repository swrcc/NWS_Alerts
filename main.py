import geopandas as gpd
import matplotlib.pyplot as plt
from pyscript import display

def plot_map():
    # Load the shapefile
    gdf = gpd.read_file('current_all.shp')

    # Create a Matplotlib figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))

    # Set the map boundaries to the US
    ax.set_xlim(-125, -66)
    ax.set_ylim(24, 50)

    # Plot the shapefile data
    gdf.plot(ax=ax, edgecolor='black', facecolor='none')

    # Add a title
    ax.set_title('Weather Hazards Map of the United States')

    # Optionally, add gridlines
    ax.grid(True)

    # Display the plot using PyScript
    display(fig, target="mpl")

# Call the function to plot the map
plot_map()
