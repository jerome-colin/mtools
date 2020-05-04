# MTOOLS
#### A collection of classes to:
* retrieve surface reflectance products (Maja S2, Maja Venus zip, HDF) as numpy array, accounting for cloud and edge masks;
* compute statistics from products, collection of products, or from comparison between two collections.

#### Status

version 0.1.0 (not stable)

#### Testing coverage (with pytest):

```
----------- coverage: platform linux, python 3.7.7-final-0 -----------
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
common/Collection.py           63      4    94%   57, 88-89, 103
common/Comparison.py           62      5    92%   15-19
common/Product.py             168     19    89%   20-23, 54-60, 70-71, 133-136, 239, 242, 259
common/Roi.py                  76      8    89%   51-52, 57-58, 92-96, 120
common/test_Collection.py      18      0   100%
common/test_Comparison.py      23      0   100%
common/test_Product.py        169      0   100%
common/test_Roi.py            103      0   100%
common/test_utilities.py       75      0   100%
common/utilities.py            62      3    95%   27-28, 37
---------------------------------------------------------
TOTAL                         819     39    95%

```

#### Python v-env: 
* requirement.txt (pip)
* mtools.yml (conda)

## Product

#### Product.Product
Generic class with the following methods:
* get_content_list(): retreive the content of a product
* find_band(string): get the filename from a <string> pattern
* get_band(band, \[scalef\]): get a band as numpy array, optionally apply scale factor
* get_band_subset(band, roi=None, ulx=None, uly=None, lrx=None, lry=None, scalef=None): get a subset of band by passing either an Roi object of coordinates, optionally with scale factor

#### Product.Product_zip
Extends Product for zipped files. 

#### Product.Product_zip_venus
Extends Product.Product_zip with venus specific methods and attributes.

#### Product.Product_dir_maja
Extends Product with Maja S2 specific methods and attributes.

#### Product.Product_hdf
Extends Product for HDF files.

#### Product.Product_hdf_acix
Extends Product.Product_hdf with ACIX reference S2 specific methods and attributes.

## Roi

#### Roi.Roi_collection
A class to create a collection of ROI from pairs of coordinates described in a csv file and an extent.

#### Roi.Roi
An Roi class that can be passed to Product.get_band_subset()

## Collection
Automatically finds any products in a given path and create collection instances for Comparison.

## Comparison
#### Comparison.Comparison
Cornerstone class to compare two time series of products in collections. Provides facilities to find matching by date between two collections of products, and compute statistics for each band of each product of both collections. Create subclasses of Comparison for various scenarii.

#### Comparison.Comparison_acix
Extends Comparison.Comparison with specific methods for ACIX.
* one_by_one(): output RMSE for valid pixels between each band of each products of two collections passed to Comparison. A valid pixel is within image boundaries (from edge mask) and cloud-free (from cloud mask);
* flatten(): output one RMSE of the entire comparison. 

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

-e, --extent : set ROI extent (in meters, defaults to 100m). An ROI is a square of size extent*extent centered on (utmx, utmy)

## For help:

`roistats.py --help`'

## Requirements:

Dependency list provided as yaml conda environment file in:

`mtools.yml`
