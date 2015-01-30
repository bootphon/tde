"""This script extracts the gold fragments from a corpus.

"""

import sys
import cPickle as pickle
import argparse


if __name__ == '__main__':
    def parse_args():
        parser = argparse.ArgumentParser(
            prog='goldset.py',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='Extract the set of gold fragments from phone file.',
            epilog="""Example usage:

$ python goldset.py mycorpus.phn mygoldset.pkl

extracts the gold fragments from `mycorpus.phn` and writes them to the binary
file `mygoldset.pkl`.

Note that the phone file must be formatted like this:

fileid starttime endtime phone
...
""")
        parser.add_argument('infile', metavar='INPUT',
                            nargs=1,
                            help='input phone file')
        parser.add_argument('outfile', metavar='OUTPUT',
                            nargs=1,
                            help='output gold file')
        parser.add_argument('-l', '--length',
                            action='store',
                            dest='minlength',
                            default=3,
                            help='minimum length of fragments considered')
        parser.add_argument('-v', '--verbose',
                            action='store_true',
                            dest='verbose',
                            default=False,
                            help='display progress during extraction')
        parser.add_argument('-n', '--n_jobs',
                            action='store',
                            dest='n_jobs',
                            default=1,
                            help='number of parallel jobs')
        return vars(parser.parse_args())

    args = parse_args()
    minlength = args['minlength']
    inputfile = args['infile'][0]
    verbose = args['verbose']
    if verbose:
        print 'Reading phone file...',
        sys.stdout.flush()
    tokenlists = read_phone_file(inputfile)
    if verbose:
        print 'done.'
        sys.stdout.flush()
    n_jobs = int(args['n_jobs'])
    fragments = extract_gold_fragments(tokenlists, minlength=minlength,
                                       verbose=verbose, n_jobs=n_jobs)

    with open(args['outfile'][0], 'wb') as fid:
        pickle.dump(fragments, fid, -1)
