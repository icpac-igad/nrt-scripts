import fiona
import netCDF4
import xarray as xr
import rioxarray
from shapely.geometry import shape


def clip_to_ea(dataset, shp_path="shp/gha_admin0.shp", x_dim="lon", y_dim="lat"):
    # read shapefile
    shp = fiona.open(shp_path)

    # convert first feature to shapely shape
    geom = shape(shp[0]['geometry'])

    # if netcdf.Dataset, reopen with xr
    if isinstance(dataset, netCDF4.Dataset):
        ds = xr.open_dataset(xr.backends.NetCDF4DataStore(dataset))
    # if xr.Dataset, use the dataset
    elif isinstance(dataset, xr.Dataset):
        ds = dataset
    else:
        # we assume this is a data path, open it
        ds = xr.open_dataset(dataset)

    # set spatial dimensions
    ds.rio.set_spatial_dims(x_dim=x_dim, y_dim=y_dim, inplace=True)

    # write crs
    ds.rio.write_crs("epsg:4326", inplace=True)

    # clip to shape
    ds = ds.rio.clip([geom], 'epsg:4326', drop=True)

    return ds