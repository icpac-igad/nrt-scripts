import fiona
import xarray as xr
import rioxarray as rxr
from shapely.geometry import shape


def clip_to_ea(ds, shp_path="shp/gha_admin0.shp"):
    # read shapefile
    shp = fiona.open(shp_path)

    # convert first feature to shapely shape
    geom = shape(shp[0]['geometry'])

    if not isinstance(ds, xr.Dataset):
        # we assume this is a data path, open it with rioxarray
        ds = rxr.open_rasterio(ds, decode_times=False)

    # write crs
    ds.rio.write_crs("epsg:4326", inplace=True)

    ds.spatial_ref.attrs[
        'crs_wkt'] = "GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AXIS[\"Longitude\",EAST],AXIS[\"Latitude\",NORTH],AUTHORITY[\"EPSG\",\"4326\"]]"
    ds.spatial_ref.attrs[
        'spatial_ref'] = "GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AXIS[\"Longitude\",EAST],AXIS[\"Latitude\",NORTH],AUTHORITY[\"EPSG\",\"4326\"]]"

    # rioxarray has issues with assigning multiple units for multi-temporal data.
    # we only need one
    if isinstance(ds, xr.DataArray):
        units = ds.attrs.get('units')
        if units and isinstance(units, tuple):
            ds.attrs['units'] = units[0]

    # clip to shape
    ds = ds.rio.clip([geom], 'epsg:4326', drop=True)

    if ds.x.attrs.get('axis'):
        del ds.x.attrs['axis']
    if ds.x.attrs.get('long_name'):
        del ds.x.attrs['long_name']
    if ds.x.attrs.get('standard_name'):
        del ds.x.attrs['standard_name']
    if ds.x.attrs.get('units'):
        del ds.x.attrs['units']

    if ds.y.attrs.get('axis'):
        del ds.y.attrs['axis']
    if ds.y.attrs.get('long_name'):
        del ds.y.attrs['long_name']
    if ds.y.attrs.get('standard_name'):
        del ds.y.attrs['standard_name']
    if ds.y.attrs.get('units'):
        del ds.y.attrs['units']

    return ds

    return ds
