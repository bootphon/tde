import random
from pprint import pformat
from collections import defaultdict

import tde.reader

def load_all_names(corpusfile, verbose):
    with tde.util.verb_print('loading names', verbose, True, True, True):
        names = set()
        names_add = names.add
        for line in open(corpusfile):
            name = line.strip().split(' ')[0]
            names_add(name)
    return names



if __name__ == '__main__':
    import argparse
    def parse_args():
        parser = argparse.ArgumentParser(
            prog='sample_names',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='Sample names',
            epilog="""Example usage:

$ python sample_names.py gold.classes 2000 5

samples 2000 names in 5 folds from gold.classes
""")
        parser.add_argument('corpusfile', metavar='CORPUSFILE',
                            nargs=1,
                            help='corpusfile')
        parser.add_argument('nsamples', metavar='NSAMPLES',
                            nargs=1,
                            help='number of samples')
        parser.add_argument('nfolds', metavar='NFOLDS',
                            nargs=1,
                            help='number of folds')
        parser.add_argument('crossfile', metavar='CROSSFILE',
                            nargs=1,
                            help='output file for cross-speaker names')
        parser.add_argument('withinfile', metavar='WITHINFILE',
                            nargs=1,
                            help='output file for within-speaker names')
        parser.add_argument('corpustype', metavar='CORPUSTYPE',
                            nargs=1,
                            help='identifier for corpus')
        parser.add_argument('-v', '--verbose',
                            action='store_true',
                            dest='verbose',
                            default=False,
                            help='display progress')
        parser.add_argument('-d', '--debug',
                            action='store_true',
                            dest='debug',
                            default=False,
                            help='display debug information')
        return vars(parser.parse_args())
    args = parse_args()

    verbose = args['verbose']
    debug = args['debug']

    corpusfile = args['corpusfile'][0]
    nsamples = int(args['nsamples'][0])
    nfolds = int(args['nfolds'][0])

    crossfile = args['crossfile'][0]
    withinfile = args['withinfile'][0]
    corpustype = args['corpustype'][0]

    all_names = load_all_names(corpusfile, verbose)
    print len(all_names)

    if nsamples > len(all_names):
        print 'number of names in corpus {0} is smaller than number of ' \
            'samples {1}'.format(len(all_names), nsamples)
        exit()


    # cross-speaker
    names_cross = list(tde.util.grouper(nsamples // nfolds,
                                        random.sample(all_names, nsamples)))

    with open(crossfile, 'w') as fid:
        fid.write('\n\n'.join('\n'.join(sorted(ns)) for ns in names_cross))

    # within-speaker
    speakers = defaultdict(set)
    for n in all_names:
        speakers[tde.util.fname2speaker(corpustype)(n)].add(n)

    print pformat({s : len(fs) for s, fs in speakers.iteritems()})

    names_within = [random.sample(fs, min(len(fs), 1000))
                    for fs in speakers.values()]

    with open(withinfile, 'w') as fid:
        fid.write('\n\n'.join('\n'.join(sorted(ns)) for ns in names_within))
