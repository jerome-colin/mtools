__author__ = "jerome.colin'at'cesbio.cnes.fr"
__license__ = "MIT"
__version__ = "1.0.2"

import sys
import argparse
import numpy as np
import common.utilities as utl
import common.Product as prd
import common.Collection as clc
import common.Comparison as cmp


def test_acix_validate():

    list = "acix_list.txt"
    save = False
    verbose = False

    # Create the logger
    logger = utl.get_logger('test_acix_validate', verbose)

    # <maja_band>, <hdf_band>, <resolution>, <ref_samples>, <maja_samples>
    bdef_acix = (
        ["band02", "SRE_B2.", "R1", [], []],
        ["band03", "SRE_B3.", "R1", [], []],
        ["band04", "SRE_B4.", "R1", [], []],
        ["band05", "SRE_B5.", "R2", [], []],
        ["band06", "SRE_B6.", "R2", [], []],
        ["band07", "SRE_B7.", "R2", [], []],
        ["band08", "SRE_B8.", "R1", [], []],
        ["band8a", "SRE_B8A.", "R2", [], []],
        ["band11", "SRE_B11.", "R2", [], []],
        ["band12", "SRE_B12.", "R2", [], []])

    f = open(list, 'r')
    paths_list = f.read().splitlines()

    for p in paths_list:
        paths = p.split(',')
        location_name = paths[0].split('/')[-1]

        # Container for local statistics
        local_stats = (
            [[], []],
            [[], []],
            [[], []],
            [[], []],
            [[], []],
            [[], []],
            [[], []],
            [[], []],
            [[], []],
            [[], []])

        acix_vermote_collection = clc.Collection(paths[0], logger)
        acix_maja_collection = clc.Collection(paths[1], logger)
        compare = cmp.Comparison(acix_vermote_collection, acix_maja_collection, logger)

        for match in compare.matching_products:
            logger.info("One-by-one for %s between %s and %s" % (match[0], match[1], match[2]))
            p_ref = prd.Product_hdf_acix(match[1], logger)
            p_maja = prd.Product_dir_maja(match[2], logger)

            for b in range(len(bdef_acix)):
                b_ref = p_ref.get_band(p_ref.find_band(bdef_acix[b][0]), scalef=p_ref.sre_scalef)
                b_maja = p_maja.get_band(p_maja.find_band(bdef_acix[b][1]), scalef=p_maja.sre_scalef)
                clm = p_maja.get_band(p_maja.find_band("CLM_" + bdef_acix[b][2]))
                edg = p_maja.get_band(p_maja.find_band("EDG_" + bdef_acix[b][2]))
                mask, ratio = p_maja.get_mask(clm, edg, stats=True)
                del clm
                del edg

                b_ref_valid = utl.is_valid(b_ref, mask)
                del b_ref
                b_maja_valid = utl.is_valid(b_maja, mask)
                del b_maja
                del mask

                if len(b_ref_valid) == len(b_maja_valid):
                    local_stats[b][0].extend(b_ref_valid)
                    local_stats[b][1].extend(b_maja_valid)
                    if not save:
                        bdef_acix[b][3].extend(b_ref_valid)
                        bdef_acix[b][4].extend(b_maja_valid)
                    else:
                        np.save(location_name + '_' + bdef_acix[b][0] + '.npy', np.stack((b_ref_valid, b_maja_valid)))

                else:
                    logger.error("Length unmatch between %s and %s" % (bdef_acix[b][0], bdef_acix[b][1]))

        for l in range(len(local_stats)):
            rmse = utl.rmse(np.asarray(local_stats[l][0]), np.asarray(local_stats[l][1]))
            acix_A = utl.accuracy(np.asarray(local_stats[l]))
            acix_P = utl.precision(np.asarray(local_stats[l]))
            acix_U = utl.uncertainty(np.asarray(local_stats[l]))
            logger.info("RESULT, %s, %s, %8.6f, %8.6f, %8.6f, %8.6f" % (location_name, bdef_acix[l][0], rmse, acix_A, acix_P, acix_U))

        del local_stats

    if not save:
        for b in range(len(bdef_acix)):
            rmse = utl.rmse(np.asarray(bdef_acix[b][3]), np.asarray(bdef_acix[b][4]))
            acix_A = utl.accuracy(np.asarray(np.asarray(bdef_acix[b][3])))
            acix_P = utl.precision(np.asarray(np.asarray(bdef_acix[b][3])))
            acix_U = utl.uncertainty(np.asarray(np.asarray(bdef_acix[b][3])))
            logger.info("RESULT, Stacked, %s, %8.6f, %8.6f, %8.6f, %8.6f" % (bdef_acix[b][0], rmse, acix_A, acix_P, acix_U))

