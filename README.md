# ROISTATS

Lightweight utility to compute band statistics from zipped Venus products over user defined Regions of Interest.

Coordinates are expressed in UTM, ROI extent in meters.

## Usage:

`python roistats.py <full_path_produit.zip> <roi_definition.csv> [-v|e]`

A ROI definition file must be in csv, with one line per ROI containing:

`<int_roi_id>, <float_utmx>, <float_utmy>`

With:

* int_roi_id: any user-defined int

* float_utmx: x (UTM) centre coordinate of the ROI

* float_utmy: y (UTM) centre coordinate of the ROI

Optional arguments:

-v, --verbose : set log file verbosity to DEBUG (defaults to INFO)
-e, --extent : set ROI extent (in meters). An ROI is a square of size extent*extent centered on (utmx, utmy)

## For help:

`roistats.py --help`'

## Requirements:

Dependency list provided as yaml conda environment file in:

`mtools.yml`

# MTOOLS

Generic classes for product and ROI definition can be found in 'common'