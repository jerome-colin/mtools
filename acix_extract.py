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
    parser.add_argument("-s", "--save", help="Write location results as npy instead of stacking in memory",
                        action="store_true", default=False)
    parser.add_argument("-v", "--verbose", help="Set verbosity to DEBUG level", action="store_true", default=False)
    parser.add_argument("--negative", help="Save sr lt 0", action="store_true", default=False)
    parser.add_argument("--keepall", help="Keep sr <= 0 but cloudfree", action="store_true", default=False)
    parser.add_argument("--stack", help="Stack all sites in one file", action="store_true", default=False)

    args = parser.parse_args()

    # <maja_band>, <hdf_band>, <resolution>, <ref_samples>, <maja_samples>
    bdef_acix = (
        ["band02", "SRE_B2.", "R1", []],
        ["band03", "SRE_B3.", "R1", []],
        ["band04", "SRE_B4.", "R1", []],
        ["band05", "SRE_B5.", "R2", []],
        ["band06", "SRE_B6.", "R2", []],
        ["band07", "SRE_B7.", "R2", []],
        ["band08", "SRE_B8.", "R1", []],
        ["band8a", "SRE_B8A.", "R2", []],
        ["band11", "SRE_B11.", "R2", []],
        ["band12", "SRE_B12.", "R2", []])

    band_id = args.band

    # Create the logger
    logger = utl.get_logger('acix_validate_' + bdef_acix[band_id][0], args.verbose)

    if (band_id < 0 or band_id > len(bdef_acix)):
        logger.error("Band ID out of range with value %i" % band_id)
        sys.exit(3)

    # vector containers for stacked data
    v_stacked_valid_ref = np.zeros((0))
    v_stacked_valid_maja = np.zeros((0))
    v_stacked_lt0_ref = np.zeros((0))
    v_stacked_lt0_maja = np.zeros((0))
    v_stacked_keep_all_ref = np.zeros((0))
    v_stacked_keep_all_maja = np.zeros((0))

    match_count = 0
    len_check = 0

    f = open(args.list, 'r')
    paths_list = f.read().splitlines()

    for p in paths_list:
        paths = p.split(',')
        location_name = paths[0].split('/')[-1]

        # vector containers for location specific data
        v_local_valid_ref = np.zeros((0))
        v_local_valid_maja = np.zeros((0))
        v_local_lt0_ref = np.zeros((0))
        v_local_lt0_maja = np.zeros((0))

        acix_vermote_collection = clc.Collection(paths[0], logger)
        acix_maja_collection = clc.Collection(paths[1], logger)
        compare = cmp.Comparison(acix_vermote_collection, acix_maja_collection, logger)

        for match in compare.matching_products:
            logger.info("One-by-one for %s between %s and %s" % (match[0], match[1], match[2]))
            p_ref = prd.Product_hdf_acix(match[1], logger)
            p_maja = prd.Product_dir_maja(match[2], logger)

            try:
                b_ref = p_ref.get_band(p_ref.find_band(bdef_acix[band_id][0]), scalef=p_ref.sre_scalef)
                m_ref_qa = p_ref.get_band(p_ref.find_band("refqa"))
                b_maja = p_maja.get_band(p_maja.find_band(bdef_acix[band_id][1]), scalef=p_maja.sre_scalef)
                clm = p_maja.get_band(p_maja.find_band("CLM_" + bdef_acix[band_id][2]))
                edg = p_maja.get_band(p_maja.find_band("EDG_" + bdef_acix[band_id][2]))
                m_maja_qa, ratio = p_maja.get_mask(clm, edg, stats=True)
                del clm
                del edg

                # Issue 32:
                if bdef_acix[band_id][2] == "R2":
                    b_maja = b_maja.repeat(2, axis=0).repeat(2, axis=1)
                    logger.info("Upscaling %s from %s to full resolution with nearest neighbor" % (bdef_acix[band_id][1], bdef_acix[band_id][2]))
                    m_maja_qa = m_maja_qa.repeat(2, axis=0).repeat(2, axis=1)
                    logger.info("Upscaling %s QA from %s to full resolution with nearest neighbor" % (bdef_acix[band_id][1], bdef_acix[band_id][2]))


                # default filter : any cloudfree flaged both by ref and maja and sr >= 0
                is_valid = np.where(
                    (b_ref > 0)
                    & (b_maja > 0)
                    & (m_ref_qa == 1)
                    & (m_maja_qa == 1)
                )

                if args.negative:
                    # get sr < 0 though flaged cloudfree
                    is_cloudfree_but_negative = np.where(
                        (m_maja_qa == 1)
                        & (m_ref_qa == 1)
                        & ((b_maja < 0) | (b_ref < 0))
                    )

                if args.keepall:
                    # get sr < 0 though flaged cloudfree
                    is_cloudfree_keep_all = np.where(
                        (m_maja_qa == 1)
                        & (m_ref_qa == 1)
                    )

                # stack local valid values for all timestamp matches
                v_local_valid_ref = np.append(v_local_valid_ref, (b_ref[is_valid]))
                v_local_valid_maja = np.append(v_local_valid_maja, (b_maja[is_valid]))

                if args.negative:
                    # stack local cloudfree negative sr for all timestamp matches
                    v_local_lt0_ref = np.append(v_local_lt0_ref, (b_ref[is_cloudfree_but_negative]))
                    v_local_lt0_maja = np.append(v_local_lt0_maja, (b_maja[is_cloudfree_but_negative]))

                if args.keepall:
                    v_local_keep_all_ref = np.append(v_local_lt0_ref, (b_ref[is_cloudfree_keep_all]))
                    v_local_keep_all_maja = np.append(v_local_lt0_maja, (b_maja[is_cloudfree_keep_all]))


                match_count += 1
                len_check += len(b_ref[is_valid])

                if args.stack:
                    # if all locations have to be stacked in one single vector
                    v_stacked_valid_ref = np.append(v_stacked_valid_ref, v_local_valid_ref)
                    v_stacked_valid_maja = np.append(v_stacked_valid_maja, v_local_valid_maja)

                    if args.negative:
                        v_stacked_lt0_ref = np.append(v_stacked_lt0_ref, v_local_lt0_ref)
                        v_stacked_lt0_maja = np.append(v_stacked_lt0_maja, v_local_lt0_maja)

                    if args.keepall:
                        v_stacked_keep_all_ref = np.append(v_stacked_keep_all_ref, v_local_keep_all_ref)
                        v_stacked_keep_all_maja = np.append(v_stacked_keep_all_maja, v_local_keep_all_maja)

                else:
                    # save local vectors in one compressed file
                    if not args.keepall:
                        np.savez_compressed(location_name + "_valid_" + bdef_acix[band_id][0],
                                            [v_local_valid_ref.astype('float32'), v_local_valid_maja.astype('float32')])
                    if args.negative:
                        np.savez_compressed(location_name + "_sr_lt_0_" + bdef_acix[band_id][0],
                                            [v_local_lt0_ref.astype('float32'), v_local_lt0_maja.astype('float32')])

                    if args.keepall:
                        np.savez_compressed(location_name + "_keep_all_" + bdef_acix[band_id][0],
                                            [v_local_keep_all_ref.astype('float32'), v_local_keep_all_maja.astype('float32')])

            except TypeError as err:
                logger.warning(
                    "Had to skip comparison for %s because of unexpected product dimension (see previous error)"
                    % (match[0]))

    if args.stack:
        # if --stack, save stacked vector in one single compressed file
        np.savez_compressed("Stacked_valid_" + bdef_acix[band_id][0],
                            [v_stacked_valid_ref.astype('float32'), v_stacked_valid_maja.astype('float32')])
        if args.negative:
            np.savez_compressed("Stacked_sr_lt_0_" + bdef_acix[band_id][0],
                                [v_stacked_lt0_ref.astype('float32'), v_stacked_lt0_maja.astype('float32')])

        if args.keepall:
            np.savez_compressed("Stacked_sr_keep_all_" + bdef_acix[band_id][0],
                                [v_stacked_keep_all_ref.astype('float32'), v_stacked_keep_all_maja.astype('float32')])

        if len_check == len(v_stacked_valid_ref) and len_check == len(v_stacked_valid_maja):
            logger.info("Saved %i samples to %s.npy" % (len_check, location_name))
        else:
            logger.error("Inconsistent sample len between len_check=%i and len(v_stacked_valid_ref)=%i"
                         % (len_check, len(v_stacked_valid_ref)))

    sys.exit(0)


if __name__ == "__main__":
    main()
