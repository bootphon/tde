from __future__ import division
import os
import os.path as path
import glob

import tde.util.reader
import tde.data.fragment
import tde.data.interval

from itertools import chain

datadir = '/fhgfs/bootphon/scratch/roland/zerospeech2015/buckeye_forced_align'
phndir = path.join(datadir, 'phn', 'test')
wrddir = path.join(datadir, 'wrd', 'test')

def load_annotation(fname):
    bname = '_'.join(path.splitext(path.basename(fname))[0].split('_')[:-1])
    # bname = path.splitext(path.basename(fname))[0]
    r = []
    for line_ix, line in enumerate(open(fname)):
        if line == '':
            continue
        try:
            start, stop, mark = line.strip().split(' ')
        except ValueError:
            raise ValueError('badly formatted line {1}: {0}'.format(line, line_ix))
        try:
            start = float(start)
            stop = float(stop)
        except ValueError:
            raise ValueError('could not convert string to float in line {1}: {0}'.format(line, line_ix))
        try:
            interval = tde.data.interval.Interval(start, stop)
        except ValueError:
            raise ValueError('invalid interval in line {0}: ({1:.3f} {2:.3f})'.format(line_ix, start, stop))
        r.append(tde.data.fragment.FragmentToken(bname, interval, mark))
    return r

phn_fragments = []
for phnfile in glob.iglob(path.join(phndir, '*.phn')):
    annot = load_annotation(phnfile)
    phn_fragments.append(annot)
wrd_fragments = []
for wrdfile in glob.iglob(path.join(wrddir, '*.wrd')):
    annot = load_annotation(wrdfile)
    wrd_fragments.append(annot)

try:
    os.makedirs('newbuckeye')
except OSError:
    pass

outdir = 'newbuckeye'
with open(path.join(outdir, 'english.phn'), 'w') as fid:
    for ftoken in sorted(chain.from_iterable(phn_fragments),
                         key=lambda x: (x.name, x.interval.start)):
        fid.write('{0} {1:.3f} {2:.3f} {3}\n'.format(ftoken.name,
                                                     ftoken.interval.start,
                                                     ftoken.interval.end,
                                                     ftoken.mark))
with open(path.join(outdir, 'english.wrd'), 'w') as fid:
    for ftoken in sorted(chain.from_iterable(wrd_fragments),
                         key=lambda x: (x.name, x.interval.start)):
        fid.write('{0} {1:.3f} {2:.3f} {3}\n'.format(ftoken.name,
                                                     ftoken.interval.start,
                                                     ftoken.interval.end,
                                                     ftoken.mark))

from tde.goldset import extract_gold_fragments
from collections import defaultdict
def make_gold(phn_fragments, outdir, n_jobs=4, verbose=True):
    pairs = extract_gold_fragments(phn_fragments, verbose=verbose, n_jobs=n_jobs, batch_size=1000000)
    classes = defaultdict(set)
    for fragment in chain.from_iterable(pairs):
        classes[fragment.mark].add(fragment)
    with open(path.join(outdir, 'english.classes'), 'w') as fp:
        for ix, mark in enumerate(sorted(classes.keys())):
            fp.write('Class {0} [{1}]\n'.format(ix, ','.join(mark)))
            for fragment in sorted(classes[mark],
                                   key=lambda x: (x.name,
                                                  x.interval.start)):
                fp.write('{0} {1:.2f} {2:.3f}\n'.format(
                    fragment.name, fragment.interval.start, fragment.interval.end))
    return classes

make_gold(phn_fragments, outdir, n_jobs=10, verbose=True)
