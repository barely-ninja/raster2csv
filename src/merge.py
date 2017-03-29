from sys import argv
from json import load

def read_file(filename):
    "read labeled file"
    with open(filename, 'rt') as input_file:
        data = []
        for line in input_file:
            items = line.split('\t')
            try:
                num = int(items[2])
                time = float(items[0])
                bfo = float(items[1])
                data.append((num, time, bfo))
            except IndexError:
                pass
            except ValueError:
                print('Conversion error at:', items)
    return data

def find_offset(s_pts, l_pts):
    'calculates offset between two datasets'
    diff = []
    for value in l_pts:
        same_pt = list(filter(lambda x: x[0] == value[0], s_pts))
        if len(same_pt):
            diff.append(value[2]-same_pt[0][2])
    return sum(diff)/len(diff)

def merge(data):
    'merges two datasets by applying offset and adding extra values'
    s_pts = data[0]
    l_pts = data[1]
    offset = find_offset(s_pts, l_pts)
    result = []
    for row in s_pts:
        result.append((row[1], row[2]+offset))
    result += [(x[1], x[2]) for x in filter(lambda y: y[1] > result[-1][0], l_pts)]
    return result

def main(args):
    "merge data from two pictures after manual comparison"
    try:
        cfg_fn = args[1]
    except KeyError:
        print('Please specify configuration file as argument')
    with open(cfg_fn, 'rt') as cfg_file:
        config = load(cfg_file)

    folder = '/'.join(cfg_fn.split('/')[:-1])
    sources = ['short', 'long']

    for dataset in config:
        filename = dataset['name'].replace(' ', '_')+'.tsv'
        data = [read_file('/'.join((folder, label, filename))) for label in sources]
        ordered = [sorted(rows, key=lambda x: x[0]) for rows in data]
        merged = merge(ordered)
        with open(folder+'/'+filename,'wt') as out_file:
            out_file.write(dataset['name']+'\t'+dataset['time']+'\n')
            out_file.write('Time, sec\tBFO, Hz\n')
            for row in merged:
                out_file.write('{:.2f}\t{:.2f}\n'.format(row[0], row[1]))


if __name__ == "__main__":
    main(argv)
