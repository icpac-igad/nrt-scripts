import fiona
import xarray as xr
import rioxarray as rxr
from shapely.geometry import shape


def clip_to_ea(dataset, shp_path, x_dim="lon", y_dim="lat"):
    # read shapefile
    shp = fiona.open(shp_path)

    # convert first feature to shapely shape
    geom = shape(shp[0]['geometry'])

    # open nc file
    ds = rxr.open_rasterio(dataset, decode_times=False)

    # set spatial dimensions
    # ds.rio.set_spatial_dims(x_dim=x_dim, y_dim=y_dim, inplace=True)

    # write crs
    ds = ds.rio.write_crs("epsg:4326", inplace=True)

    # rioxarray has issues with assigning multiple units for multi-temporal data.
    # we only need one
    if isinstance(ds, xr.DataArray):
        units = ds.attrs.get('units')
        if units and isinstance(units, tuple):
            ds.attrs['units'] = units[0]

    # clip to shape
    ds = ds.rio.clip([geom], 'epsg:4326', drop=True)

    return ds
