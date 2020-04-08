import numpy as np
import os
import argparse

def get_wqb_simple(file_duck_dat):
    f = open(file_duck_dat,'r')
    data = []
    for line in f:
        a = line.split()
        data.append([float(a[1]), float(a[3]), float(a[5]), float(a[8])])
    f.close()
    data = np.array(data[1:])
    Work = data[:,3]
    Wqb_max = max(Work[400:])
    Wqb_min = min(Work[:400])
    Wqb_value = Wqb_max - Wqb_min
    return(Wqb_value, data, Wqb_min)


def get_Wqb_value_all(input_dir):
    file_list = []
    for fil in os.listdir(input_dir):
        if fil[-3:] == 'dat':
            file_list.append(fil)

    Wqb_values = []
    for fil in file_list:
        Wqb_data = get_wqb_simple(fil)
        Wqb_values.append(Wqb_data[0])

    Wqb = min(Wqb_values)
    return(Wqb)

def main():
    parser = argparse.ArgumentParser(description='Get WQB score from OpenDUck data')
    parser.add_argument('-d', '--dir', help='Directory with location of OpenDUck data')
    parser.add_argument('-l', '--ligand', help='Ligand in mol format')
    parser.add_argument('-o', '--output', help='Ligand output in mol forma, with wqb value')

    args = parser.parse_args()

    if args.dir:
        input_dir = args.dir
    else:
        input_dir = os.getcwd()
    
    wqb_val = get_Wqb_value_all(input_dir)

    if args.ligand:
        with open(args.ligand) as f:
            records = f.read().split('$$$$')
            print(records)
        if (len(records) > 2) or (len(records) == 2 and not records[1].isspace()):
            # if there is more than 1 record; 2 is ok if the second is whitespace
            raise IOError('The mol file contains multiple records.')
        else:
            wqb_str = "> <SCORE.DUCK_WQB>\n{}\n".format(wqb_val)
            records[0] += wqb_str
            print(records)
            with open(args.output, 'w') as f:
                f.write('$$$$'.join(records))
    else:
        print(wqb_val)


if __name__ == '__main__':
    main()

