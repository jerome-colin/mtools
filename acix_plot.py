import matplotlib.pylab as pl
import numpy as np
import common.utilities as utl
import sys
import argparse

def main():
    # Argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("data", help="List of paths of collection")
    parser.add_argument("--band", help="Specific band in acix band definition", type=str, required=True)
    parser.add_argument("--samples", help="Reflectance sampling, defaults to 100 (ie. 0.01)", type=int, default=100)
    parser.add_argument("-s", "--save", help="Write location results as npy instead of stacking in memory", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", help="Set verbosity to DEBUG level", action="store_true", default=False)
    args = parser.parse_args()

    filename = "Carpentras.npy"

    data = np.load(args.data)
    band_name = args.band
    site_name = filename[:-4]

    sr_ref = data[0]
    sr_maja = data[1]

    samples = args.samples # Bins of hist
    step = 1 / samples # or 0.01 steps of reflectance value

    bins_count = np.zeros((samples))
    acix_a = np.zeros((samples))
    acix_p = np.zeros((samples))
    acix_u = np.zeros((samples))

    for i in np.arange(0, samples):
        bin_min = i * step
        bin_max = i * step + step

        is_in_range = np.where((sr_ref >= bin_min) & (sr_ref < bin_max))

        bin_sr_ref = sr_ref[is_in_range]
        bin_sr_maja = sr_maja[is_in_range]
        bins_count[i] = len(bin_sr_ref)

        acix_a[i] = utl.accuracy(bin_sr_ref - bin_sr_maja)
        if bins_count[i] > 1:
            acix_p[i] = utl.precision(bin_sr_ref - bin_sr_maja)
        else:
            acix_p[i] = 0

        acix_u[i] = utl.uncertainty(bin_sr_ref - bin_sr_maja)

        if args.verbose:
            print("From %4.2f to %4.2f: %i samples, A=%8.6f, P=%8.6f, U=%8.6f" % (bin_min, bin_max, bins_count[i], acix_a[i], acix_p[i], acix_u[i]))

    cumulated_acix_a = utl.accuracy(sr_ref - sr_maja)
    cumulated_acix_p = utl.precision(sr_ref - sr_maja)
    cumulated_acix_u = utl.uncertainty(sr_ref - sr_maja)
    x_sr = np.arange(0, 1, step) - (step / 2)
    spec = 0.005 + 0.05 * x_sr

    fig, ax1 = pl.subplots(figsize=(8, 8), dpi=300)

    pl.title('%s: %s, samples=%i\n A=%8.6f, P=%8.6f, U=%8.6f' % (site_name, band_name, len(sr_ref), cumulated_acix_a, cumulated_acix_p, cumulated_acix_u))

    pl.xlim(0,0.5)
    ax1.set_xlabel("Surface reflectance (-)")
    ax1.set_ylim(-0.03, 0.03)
    ax1.plot(x_sr, acix_a, 'r-2', label='accuracy')
    ax1.plot(x_sr, acix_p, 'g-2', label='precision')
    ax1.plot(x_sr, acix_u, 'b-2', label='uncertainty')
    ax1.plot(x_sr, spec, 'm', label='suggested specs')
    pl.legend(loc=1)

    ax2 = ax1.twinx()
    ax2.bar(x_sr, bins_count, fill=False, color='w', edgecolor='c', width=0.01, label="nb of points")

    pl.legend(loc=4)
    pl.savefig("acix_" + site_name + "_" + band_name + ".png")


    sys.exit(0)


if __name__ == "__main__":
    main()
