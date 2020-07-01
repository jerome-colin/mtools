import glob
import sys
import argparse
import numpy as np

def main():
    # Argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path of npz collection")
    parser.add_argument("band", help="Band name")
    args = parser.parse_args()

    flist = glob.glob(args.path + "*" + args.band + "*.npz")

    init = True
    count = 0
    control_ref = 0
    control_maja = 0

    for f in flist:
        data = np.load(f)['arr_0']

        if init:
            sr_ref = data[0]
            sr_maja = data[1]
            init = False

        else:
            sr_ref = np.append(sr_ref, data[0])
            sr_maja = np.append(sr_maja, data[1])

        print("  Adding %s" % f)
        count += 1
        control_ref += len(sr_ref)
        control_maja += len(sr_maja)

    np.savez_compressed("Stacked.npz", [sr_ref, sr_maja])
    print("Final length of sr_ref is %i (ctrl is %i)" % (len(sr_ref), control_ref))
    print("Final length of sr_maja is %i (ctrl is %i)" % (len(sr_maja), control_maja))
    print("Completed with %i files..." % count)

    sys.exit(0)


if __name__ == "__main__":
    main()
