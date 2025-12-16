"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.DataFrame(pd.read_csv("data/referendum.csv", sep=";"))
    regions = pd.DataFrame(pd.read_csv("data/regions.csv"))
    departments = pd.DataFrame(pd.read_csv("data/departments.csv"))

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    # keep only codes and names
    df = pd.merge(regions, departments, left_on='code', right_on='region_code')
    df = df.drop(columns=['id_x', 'slug_x', 'slug_y', 'id_y', 'region_code'])
    df = df.rename(columns={'code_x': 'code_reg', 'code_y': 'code_dep',
                            'name_x': 'name_reg', 'name_y': 'name_dep'})
    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    rows_idx_reg_and_deps = regions_and_departments.loc[
        regions_and_departments['name_dep'].str.contains('DOM|TOM|COM')].index
    regions_and_departments = regions_and_departments.drop(
        rows_idx_reg_and_deps)
    rows_to_drop = referendum.loc[
        referendum['Department code'].str.contains('Z')].index
    referendum = referendum.drop(index=rows_to_drop)
    referendum = referendum.replace(
        ['1', '2', '3', '4', '5', '6', '7', '8', '9'],
        ['01', '02', '03', '04', '05', '06', '07', '08', '09'])
    df = pd.merge(referendum, regions_and_departments,
                  left_on='Department code', right_on='code_dep', how='left')
    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df = referendum_and_areas.groupby(['code_reg', 'name_reg']).sum()
    df = df.reset_index(level='name_reg')
    df = df.drop(columns=['Department code', 'Department name', 'Town code',
                          'Town name', 'code_dep', 'name_dep'])
    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geodata = gpd.read_file('data/regions.geojson')
    df = pd.merge(referendum_result_by_regions, geodata, left_on='code_reg',
                  right_on='code', how='left')
    geodata_merged = gpd.GeoDataFrame(df)
    geodata_merged['ratio'] = geodata_merged['Choice A'] / (
        geodata_merged['Choice A'] + geodata_merged['Choice B'])
    return geodata_merged


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
