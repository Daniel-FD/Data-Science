# ECMWF CDS API Setup Instructions

If AEMET data is not available, this notebook can use ECMWF's ERA5 reanalysis data as an alternative.

## Setup Steps:

1. **Register for free account**: Go to https://cds.climate.copernicus.eu/#!/home
2. **Get your API credentials**: After registration, go to https://cds.climate.copernicus.eu/api-how-to
3. **Create credentials file**: Create a file `~/.cdsapirc` with your credentials:
   ```
   url: https://cds.climate.copernicus.eu/api/v2
   key: YOUR_UID:YOUR_API_KEY
   ```
4. **Install the package**: The notebook will install `cdsapi` automatically
5. **Accept license**: You may need to accept the ERA5 license terms in your CDS account

## What ERA5 provides:
- Hourly weather data from 1979 to near real-time
- Global coverage at ~31km resolution 
- 10-meter wind speed components (u and v)
- More reliable than local weather stations for historical analysis

The notebook will automatically attempt to use ERA5 if AEMET stations don't have suitable data.
