import argparse
# import os
import shutil

# from duck.steps.parametrize import prepare_system
# from duck.utils.get_from_fragalysis import get_from_prot_code
# from duck.utils.cal_ints import find_interaction
# from duck.steps.prepare import prep_lig
# from duck.steps.chunk import (
#     chunk_with_amber,
#     do_tleap,
#     remove_prot_buffers_alt_locs,
#     find_disulfides,
# )
# from duck.steps.equlibrate import do_equlibrate
from duck.steps.normal_md import perform_md
from duck.steps.steered_md import run_steered_md
from duck.utils.check_system import check_if_equlibrated
# import yaml, sys, os
# from duck.utils.s3io import copy_directory_to_s3,download_file_from_s3


def main():
    parser = argparse.ArgumentParser(description='Perform SMD runs for dynamic undocking')
    parser.add_argument('-i', '--input', help='Equilibrated system as input')
    parser.add_argument('-p', '--pickle', help='Pickle file')
    parser.add_argument('-n', '--num-runs', type=int, help='Number of SMD runs.')
    # parser.add_argument('-o', '--output', help="PDB output")
    parser.add_argument('-l', '--md-len', type=float, help='MD run length.')
    parser.add_argument('-d', '--start-dist', type=float, help='Starting distance')
    parser.add_argument('-v', '--init-velocity', type=float, help='Initial velocity')
    parser.add_argument('--gpu-id', type=int, help='GPU ID (optional); if not specified, runs on CPU only.')

    args = parser.parse_args()
    shutil.copyfile(args.input, "equil.chk")
    shutil.copyfile(args.pickle, "complex_system.pickle")

    # Now do the MD
    # remember start_dist
    for i in range(args.num_runs):
        if i == 0:
            md_start = "equil.chk"
        else:
            md_start = "md_" + str(i - 1) + ".chk"
        log_file = "md_" + str(i) + ".csv"
        perform_md(
            md_start,
            "md_" + str(i) + ".chk",
            log_file,
            "md_" + str(i) + ".pdb",
            md_len=args.md_len,
            gpu_id=args.gpu_id,
        )
        # Open the file and check that the potential is stable and negative
        if not check_if_equlibrated(log_file, 3):
            print("SYSTEM NOT EQUILIBRATED")
            sys.exit()
        # Now find the interaction and save to a file
        run_steered_md(
            300,
            "md_" + str(i) + ".chk",
            "smd_" + str(i) + "_300.csv",
            "smd_" + str(i) + "_300.dat",
            "smd_" + str(i) + "_300.pdb",
            "smd_" + str(i) + "_300.dcd",
            args.start_dist,
            init_velocity=args.init_velocity,
            gpu_id=args.gpu_id,
        )
        run_steered_md(
            325,
            "md_" + str(i) + ".chk",
            "smd_" + str(i) + "_325.csv",
            "smd_" + str(i) + "_325.dat",
            "smd_" + str(i) + "_325.pdb",
            "smd_" + str(i) + "_325.dcd",
            args.start_dist,
            init_velocity=args.init_velocity,
            gpu_id=args.gpu_id,
        )


# sed -i.bak -e 's/\$\$\$\$/> <SCORE.DUCK_WQB>\n-0.015815293149895382\n\n\$\$\$\$/g' tst.sdf

if __name__ == "__main__":
    main()
