#!/usr/bin/env python3
"""
Compute per site and stacked RMSE for ACIX

Require: see mtools.yml for conda environment configuration

"""

__author__ = "jerome.colin'at'cesbio.cnes.fr"
__license__ = "MIT"
__version__ = "1.0.3"


import sys
import argparse
import numpy as np
from matplotlib import pylab as pl
import common.utilities as utl
import common.Product as prd
import common.Collection as clc
import common.Comparison as cmp


def main():
    # Argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("list", help="List of paths of collection")
    parser.add_argument("--band", help="Specific band in acix band definition", type=int, required=True)
    parser.add_argument("--samples", help="Reflectance sampling, defaults to 100 (ie. 0.01)", type=int, default=100)
    parser.add_argument("-s", "--save", help="Write location results as npy instead of stacking in memory", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", help="Set verbosity to DEBUG level", action="store_true", default=False)
    args = parser.parse_args()


    # <maja_band>, <hdf_band>, <resolution>, <ref_samples>, <maja_samples>
    bdef_acix = (
        ["band02", "SRE_B2.", "R1",  []],
        ["band03", "SRE_B3.", "R1",  []],
        ["band04", "SRE_B4.", "R1",  []],
        ["band05", "SRE_B5.", "R2",  []],
        ["band06", "SRE_B6.", "R2",  []],
        ["band07", "SRE_B7.", "R2",  []],
        ["band08", "SRE_B8.", "R1",  []],
        ["band8a", "SRE_B8A.", "R2", []],
        ["band11", "SRE_B11.", "R2", []],
        ["band12", "SRE_B12.", "R2", []])

    band_id = args.band

    # Create the logger
    logger = utl.get_logger('acix_validate_' + bdef_acix[band_id][0], args.verbose)

    if (band_id < 0 or band_id > len(bdef_acix)):
        logger.error("Band ID out of range with value %i" % band_id)
        sys.exit(3)

    final_stats = np.zeros((0))

    match_count = 0
    len_check = 0

    f = open(args.list, 'r')
    paths_list = f.read().splitlines()

    for p in paths_list:
        paths = p.split(',')
        location_name = paths[0].split('/')[-1]

        acix_vermote_collection = clc.Collection(paths[0], logger)
        acix_maja_collection = clc.Collection(paths[1], logger)
        compare = cmp.Comparison(acix_vermote_collection, acix_maja_collection, logger)

        for match in compare.matching_products:
            logger.info("One-by-one for %s between %s and %s" % (match[0], match[1], match[2]))
            p_ref = prd.Product_hdf_acix(match[1], logger)
            p_maja = prd.Product_dir_maja(match[2], logger)

            try:
                b_ref = p_ref.get_band(p_ref.find_band(bdef_acix[band_id][0]), scalef=p_ref.sre_scalef)
                b_maja = p_maja.get_band(p_maja.find_band(bdef_acix[band_id][1]), scalef=p_maja.sre_scalef)
                clm = p_maja.get_band(p_maja.find_band("CLM_" + bdef_acix[band_id][2]))
                edg = p_maja.get_band(p_maja.find_band("EDG_" + bdef_acix[band_id][2]))
                mask, ratio = p_maja.get_mask(clm, edg, stats=True)
                del clm
                del edg

                b_ref_valid = utl.is_valid(b_ref, mask)
                logger.info("Negative reflectances in Ref counts %i samples" % (np.sum(b_ref_valid < 0)))
                del b_ref
                b_maja_valid = utl.is_valid(b_maja, mask)
                logger.info("Negative reflectances in Maja counts %i samples" % (np.sum(b_maja_valid < 0)))
                del b_maja
                del mask

                ref_is_positive = np.where(b_ref_valid >= 0)

                if len(b_ref_valid) == len(b_maja_valid):
                    final_stats = np.append(final_stats, b_ref_valid[ref_is_positive] - b_maja_valid[ref_is_positive])
                    match_count += 1
                    len_check += len(b_ref_valid[ref_is_positive])

                else:
                    logger.error("Length unmatch between %s and %s" % (bdef_acix[band_id][0], bdef_acix[band_id][1]))

            except TypeError as err:
                logger.warning("Had to skip comparison for %s because of unexpected product dimension (see previous error)" % (match[0]))

    np.save(location_name, np.asarray(final_stats))

    if len_check == len(final_stats):
        logger.info("Saved %i samples to %s.npy" % (len_check, location_name))
    else:
        logger.error("Inconsistent sample len between len_check=%i and len(final_stats)=%i" % (len_check, len(b_ref_valid)))

    sys.exit(0)


if __name__ == "__main__":
    main()
