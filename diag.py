import matplotlib.pylab as pl
import numpy as np
import common.utilities as utl
import common.Product as prd
import common.Collection as clc
import common.Comparison as cmp
import sys
import argparse
from mpl_toolkits.axes_grid1 import make_axes_locatable


def main():
    # Argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("list", help="List of paths of collection")
    parser.add_argument("--saveto", help="subdirectory to save figs to", type=str)
    parser.add_argument("-v", "--verbose", help="Set verbosity to DEBUG level", action="store_true", default=False)

    args = parser.parse_args()
    gain_true = 3.
    gain_false = 2.5

    # Create the logger
    logger = utl.get_logger('Diag', args.verbose)

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
            timestamp = match[0]

            try:
                b_ref_b2 = p_ref.get_band(p_ref.find_band(bdef_acix[0][0]), scalef=p_ref.sre_scalef)
                b_ref_b3 = p_ref.get_band(p_ref.find_band(bdef_acix[1][0]), scalef=p_ref.sre_scalef)
                b_ref_b4 = p_ref.get_band(p_ref.find_band(bdef_acix[2][0]), scalef=p_ref.sre_scalef)
                b_ref_b8 = p_ref.get_band(p_ref.find_band(bdef_acix[6][0]), scalef=p_ref.sre_scalef)
                m_ref_qa = p_ref.get_band(p_ref.find_band("refqa"))
                b_maja_b2 = p_maja.get_band(p_maja.find_band(bdef_acix[0][1]), scalef=p_maja.sre_scalef)
                b_maja_b3 = p_maja.get_band(p_maja.find_band(bdef_acix[1][1]), scalef=p_maja.sre_scalef)
                b_maja_b4 = p_maja.get_band(p_maja.find_band(bdef_acix[2][1]), scalef=p_maja.sre_scalef)
                b_maja_b8 = p_maja.get_band(p_maja.find_band(bdef_acix[6][1]), scalef=p_maja.sre_scalef)
                b_maja_aot = p_maja.get_band(p_maja.find_band("ATB_R1"), layer=1, scalef=p_maja.aot_scalef)
                b_maja_vap = p_maja.get_band(p_maja.find_band("ATB_R1"), layer=0, scalef=p_maja.vap_scalef)
                clm = p_maja.get_band(p_maja.find_band("CLM_" + bdef_acix[0][2]))
                edg = p_maja.get_band(p_maja.find_band("EDG_" + bdef_acix[0][2]))
                m_maja_qa, ratio = p_maja.get_mask(clm, edg, stats=True)

                fig, axs = pl.subplots(nrows=3, ncols=3, figsize=[12, 12])
                fig.suptitle(location_name + ' ' + timestamp[0:4] + '-' + timestamp[4:6] + '-' + timestamp[6:8], fontsize=16)

                cset_true = axs[0, 0].imshow(np.dstack((b_maja_b4*gain_true, b_maja_b3*gain_true, b_maja_b2*gain_true)), interpolation='none', aspect='equal')
                axs[0, 0].set_title("Quicklook (B4, B3, B2)")
                cset_maja_cloud_contour = axs[0, 0].contour(m_maja_qa)
                #axs[0, 0].clabel(cset_maja_cloud_contour, inline=1, fontsize=10)


                cset_maja_qa = axs[1, 0].imshow(m_maja_qa, interpolation='none', aspect='equal', vmin=0, vmax=1, cmap='gray')
                axs[1, 0].set_title("Maja CLM & EDG (valid=1)")
                divider = make_axes_locatable(axs[1, 0])
                cax = divider.append_axes("right", size="5%", pad=0.05)
                pl.colorbar(cset_maja_qa, cax=cax)  # , orientation='horizontal')

                cset_ref_qa = axs[2, 0].imshow(m_ref_qa, interpolation='none', aspect='equal', vmin=0, vmax=1, cmap='gray')
                axs[2, 0].set_title("Reference QA (valid=1)")
                divider = make_axes_locatable(axs[2, 0])
                cax = divider.append_axes("right", size="5%", pad=0.05)
                pl.colorbar(cset_ref_qa, cax=cax)  # , orientation='horizontal')

                # cset_false = axs[0, 1].imshow(np.dstack((b_maja_b8*gain_false, b_maja_b3*gain_false, b_maja_b2*gain_false)), interpolation='none', aspect='equal')
                # axs[0, 1].set_title("%s %s (B8,B3,B2)" % (location_name, timestamp))

                cset_maja_vap = axs[0, 1].imshow(b_maja_vap, interpolation='none', aspect='equal', cmap='RdBu')
                axs[0, 1].set_title("Maja VAP $(g.cm^{-2})$")
                divider = make_axes_locatable(axs[0, 1])
                cax = divider.append_axes("right", size="5%", pad=0.05)
                pl.colorbar(cset_maja_vap, cax=cax, format='%4.2f')#, orientation='horizontal')

                # cset_maja_vap = axs[0, 1].imshow(np.dstack((b_maja_b4*gain_true, b_maja_b3*gain_true, b_maja_b2*gain_true)), interpolation='none', aspect='equal')
                # axs[0, 1].set_title("Maja VAP")
                # divider = make_axes_locatable(axs[0, 1])
                # cax = divider.append_axes("right", size="5%", pad=0.05)
                # pl.colorbar(cset_maja_vap, cax=cax)  # , orientation='horizontal')
                # cset_maja_vap_contour = axs[0, 1].contour(b_maja_vap)
                # axs[0, 1].clabel(cset_maja_vap_contour, inline=1, fontsize=10)

                cset_maja_aot = axs[0, 2].imshow(b_maja_aot, cmap='Wistia')
                axs[0, 2].imshow(np.dstack((b_maja_b4*gain_true, b_maja_b3*gain_true, b_maja_b2*gain_true)), interpolation='none', aspect='equal')
                axs[0, 2].set_title("Maja AOT $(-)$")
                divider = make_axes_locatable(axs[0, 2])
                cax = divider.append_axes("right", size="5%", pad=0.05)
                pl.colorbar(cset_maja_aot, cax=cax, format='%4.2f')  # , orientation='horizontal')
                cset_maja_aot_contour = axs[0, 2].contour(b_maja_aot, cmap='Wistia')
                axs[0, 2].clabel(cset_maja_aot_contour, inline=1, fontsize=10)

                # B2
                is_valid = np.where(
                    (b_ref_b2 > 0)
                    & (b_maja_b2 > 0)
                    & (m_ref_qa == 1)
                    & (m_maja_qa == 1)
                )
                axs[1, 1].hist(b_ref_b2[is_valid].flatten(),
                               bins=200,
                               histtype='step',
                               log=False,
                               label='Ref',
                               range=(0, 1),
                               density=False
                               )
                axs[1, 1].hist(b_maja_b2[is_valid].flatten(),
                               bins=200,
                               histtype='step',
                               log=False,
                               label='Maja',
                               range=(0, 1),
                               density=False
                               )
                axs[1, 1].set_title("B2 (QA=1 & sr>0) RMSE=%8.6f" % utl.rmse(b_ref_b2[is_valid].flatten(), b_maja_b2[is_valid].flatten()))
                axs[1, 1].legend()

                # B3
                is_valid = np.where(
                    (b_ref_b3 > 0)
                    & (b_maja_b3 > 0)
                    & (m_ref_qa == 1)
                    & (m_maja_qa == 1)
                )
                axs[1, 2].hist(b_ref_b3[is_valid].flatten(), bins=200, histtype='step', log=False, label='Ref', range=(0, 1))
                axs[1, 2].hist(b_maja_b3[is_valid].flatten(), bins=200, histtype='step', log=False, label='Maja', range=(0, 1))
                axs[1, 2].set_title("B3 (QA=1 & sr>0) RMSE=%8.6f" % utl.rmse(b_ref_b3[is_valid].flatten(), b_maja_b3[is_valid].flatten()))
                axs[1, 2].legend()

                # B4
                is_valid = np.where(
                    (b_ref_b4 > 0)
                    & (b_maja_b4 > 0)
                    & (m_ref_qa == 1)
                    & (m_maja_qa == 1)
                )
                axs[2, 1].hist(b_ref_b4[is_valid].flatten(), bins=200, histtype='step', log=False, label='Ref', range=(0, 1))
                axs[2, 1].hist(b_maja_b4[is_valid].flatten(), bins=200, histtype='step', log=False, label='Maja', range=(0, 1))
                axs[2, 1].set_title("B4 (QA=1 & sr>0) RMSE=%8.6f" % utl.rmse(b_ref_b4[is_valid].flatten(), b_maja_b4[is_valid].flatten()))
                axs[2, 1].legend()

                # B8
                is_valid = np.where(
                    (b_ref_b8 > 0)
                    & (b_maja_b8 > 0)
                    & (m_ref_qa == 1)
                    & (m_maja_qa == 1)
                )
                axs[2, 2].hist(b_ref_b8[is_valid].flatten(), bins=200, histtype='step', log=False, label='Ref', range=(0, 1))
                axs[2, 2].hist(b_maja_b8[is_valid].flatten(), bins=200, histtype='step', log=False, label='Maja', range=(0, 1))
                axs[2, 2].set_title("B8 (QA=1 & sr>0) RMSE=%8.6f" % utl.rmse(b_ref_b8[is_valid].flatten(), b_maja_b8[is_valid].flatten()))
                axs[2, 2].legend()
                
                fig.tight_layout()
                fig.subplots_adjust(top=0.88)
                #pl.show()
                pl.savefig(location_name + '_' + timestamp + '_quicklooks.png')
                pl.close('all')


            except:
                e = sys.exc_info()
                logger.error(e)





    sys.exit(0)


if __name__ == "__main__":
    main()
