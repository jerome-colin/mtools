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

    # Create the logger
    logger = utl.get_logger('acix_validate', args.verbose)

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
    if (band_id < 0 or band_id > len(bdef_acix)):
        logger.error("Band ID out of range with value %i" % band_id)
        sys.exit(3)

    samples = args.samples
    step = 1 / samples

    final_stats = ([])
    for s in range(samples):
        final_stats.append([])

    f = open(args.list, 'r')
    paths_list = f.read().splitlines()

    for p in paths_list:
        paths = p.split(',')
        #location_name = paths[0].split('/')[-1]

        acix_vermote_collection = clc.Collection(paths[0], logger)
        acix_maja_collection = clc.Collection(paths[1], logger)
        compare = cmp.Comparison(acix_vermote_collection, acix_maja_collection, logger)

        for match in compare.matching_products:
            logger.info("One-by-one for %s between %s and %s" % (match[0], match[1], match[2]))
            p_ref = prd.Product_hdf_acix(match[1], logger)
            p_maja = prd.Product_dir_maja(match[2], logger)

            b_ref = p_ref.get_band(p_ref.find_band(bdef_acix[band_id][0]), scalef=p_ref.sre_scalef)
            b_maja = p_maja.get_band(p_maja.find_band(bdef_acix[band_id][1]), scalef=p_maja.sre_scalef)
            clm = p_maja.get_band(p_maja.find_band("CLM_" + bdef_acix[band_id][2]))
            edg = p_maja.get_band(p_maja.find_band("EDG_" + bdef_acix[band_id][2]))
            mask, ratio = p_maja.get_mask(clm, edg, stats=True)
            del clm
            del edg

            b_ref_valid = utl.is_valid(b_ref, mask)
            del b_ref
            b_maja_valid = utl.is_valid(b_maja, mask)
            del b_maja
            del mask

            if len(b_ref_valid) == len(b_maja_valid):

                for s in range(samples):
                    for i in range(len(b_maja_valid)):
                        if b_maja_valid[i] >= (s * step - step / 2) and b_maja_valid[i] < (s * step + step / 2):
                            final_stats[s].extend([b_ref_valid[i] - b_maja_valid[i]])

            else:
                logger.error("Length unmatch between %s and %s" % (bdef_acix[band_id][0], bdef_acix[band_id][1]))

    x_sr   = np.arange(0, 1, step) - (step / 2)
    spec   = 0.005 + 0.05 * x_sr
    n_sr   = np.zeros(samples)
    acix_a = np.zeros(samples)
    acix_p = np.zeros(samples)
    acix_u = np.zeros(samples)

    full_stats = ([])

    for s in range(samples):
        n_sr[s] = len(final_stats[s])
        if n_sr[s] == 0:
            acix_a[s] = np.nan
            acix_p[s] = np.nan
            acix_u[s] = np.nan
        else:
            acix_a[s] = np.abs(utl.accuracy(np.asarray(final_stats[s])))
            acix_p[s] = np.abs(utl.precision(np.asarray(final_stats[s])))
            acix_u[s] = np.abs(utl.uncertainty(np.asarray(final_stats[s])))
        full_stats.extend(final_stats[s])

        logger.debug("RESULT, %s, %s, %8.3f, %8.3f, %i, %8.6f, %8.6f, %8.6f" %
                    ("STACKED",
                     bdef_acix[band_id][0],
                     s * step,
                     s * step + step,
                     n_sr[s],
                     acix_a[s],
                     acix_p[s],
                     acix_u[s]))

    full_acix_a = np.abs(utl.accuracy(np.asarray(full_stats)))
    full_acix_p = np.abs(utl.precision(np.asarray(full_stats)))
    full_acix_u = np.abs(utl.uncertainty(np.asarray(full_stats)))
    full_n_sr = len(full_stats)

    logger.info("RESULT, %s, %s, %i, %8.6f, %8.6f, %8.6f" %
                 ("STACKED",
                  bdef_acix[band_id][0],
                  full_n_sr,
                  full_acix_a,
                  full_acix_p,
                  full_acix_u))

    fig, ax1 = pl.subplots(figsize=(8, 8), dpi=300)

    pl.title('%s \n A=%8.6f, P=%8.6f, U=%8.6f' % (bdef_acix[band_id][0], full_acix_a, full_acix_p, full_acix_u))

    pl.xlim(0,0.6)
    ax1.set_xlabel("Surface reflectance (-)")
    ax1.set_ylim(0, 0.03)
    ax1.plot(x_sr, acix_a, 'r-2', label='accuracy')
    ax1.plot(x_sr, acix_p, 'g-2', label='precision')
    ax1.plot(x_sr, acix_u, 'b-2', label='uncertainty')
    ax1.plot(x_sr, spec, 'm', label='suggested specs')
    pl.legend()

    ax2 = ax1.twinx()
    ax2.bar(x_sr, n_sr, fill=False, color='w', edgecolor='c', width=0.01, label="nb of points")

    pl.legend()
    pl.savefig("acix_stacked_" + bdef_acix[band_id][0] + ".png")

    sys.exit(0)


if __name__ == "__main__":
    main()
