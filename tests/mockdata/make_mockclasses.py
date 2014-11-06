from collections import defaultdict
import numpy as np
from itertools import chain
import random
import argparse

import tde.corpus
import tde.reader
import tde.goldset


def get_intervals(fragments):
    names = set(f.name for f in fragments)
    start_per_name = {n: np.inf for n in names}
    end_per_name = {n: 0.0 for n in names}
    for fragment in fragments:
        name = fragment.name
        interval = fragment.interval
        if interval.start < start_per_name[name]:
            start_per_name[name] = interval.start
        if interval.end > end_per_name[name]:
            end_per_name[name] = interval.end
    return {name: tde.corpus.Interval(start_per_name[name],
                                      end_per_name[name])
            for name in names}


def random_fragment(intervals, exclude):
    exclude_per_name = defaultdict(list)
    for fr in exclude:
        exclude_per_name[fr.name].append(fr.interval)

    eligible_per_name = defaultdict(list)
    for name in exclude_per_name:
        ivals = sorted(exclude_per_name[name],
                       key=lambda x: x.start)

        prev_end = intervals[name].start
        for ival in ivals:
            if ival.start == prev_end:
                continue
            eligible_per_name[name].append(tde.corpus.Interval(prev_end,
                                                               ival.start))
            prev_end = ival.end
        if prev_end == intervals[name].end:
            continue
        eligible_per_name[name].append(tde.corpus.Interval(prev_end,
                                                           intervals[name].end))

    name, interval = random.choice(intervals.items())
    if name in eligible_per_name:
        # pick an eligible interval
        interval = random.choice(eligible_per_name[name])

    start = np.around(random.uniform(interval.start, interval.end), 3)
    end = np.around(random.uniform(start, interval.end), 3)
    interval = tde.corpus.Interval(start, end)
    return tde.corpus.FragmentToken(name, interval)

def fragments_to_classes(fragments):
    classes = defaultdict(set)
    for fragment1, fragment2 in fragments:
        classes[tuple(fragment1.mark)].add(fragment1)
        classes[tuple(fragment1.mark)].add(fragment2)
    return classes


def generate_classes(fragments, jitter,
                     fragment_drop, class_drop,
                     fragment_add, class_add):
    gold_fragments = tde.goldset.extract_gold_fragments(fragments)
    fragments = list(chain.from_iterable(fragments))
    intervals = get_intervals(fragments)

    gold_classes = fragments_to_classes(gold_fragments)

    # associate a ClassID
    gold_classes = {tde.corpus.ClassID(ix, mark): gold_classes[mark]
                    for ix, mark in enumerate(gold_classes.keys())}

    # sample classnames
    classnames_kept = random.sample(gold_classes.keys(),
                                    int(len(gold_classes.keys())
                                        * (1 - class_drop)))
    # add hallucinated classnames
    classnames_added = [tde.corpus.ClassID(i)
                        for i in range(len(gold_classes),
                                       len(gold_classes)
                                       + int(len(gold_classes) * class_add))]

    classes = {}
    for k in classnames_kept:
        # sample fragments
        fs_orig = gold_classes[k]
        fs_sampled = random.sample(fs_orig,
                                   int(len(fs_orig) * (1 - fragment_drop)))

        if jitter > 0.:
            # add jitter. stay within the range of the interval for this file
            fs_jittered = []
            for fr in fs_sampled:
                interval_orig = fr.interval
                start_jitter = max(interval_orig.start
                                   + random.gauss(0, jitter),
                                   intervals[fr.name].start)
                end_jitter = min(interval_orig.end + random.gauss(0, jitter),
                                 intervals[fr.name].end)
                interval_jitter = tde.corpus.Interval(start_jitter, end_jitter)
                fs_jittered.append(tde.corpus.FragmentToken(fr.name,
                                                            interval_jitter,
                                                            fr.mark))
            fs_sampled = fs_jittered
        classes[k] = fs_sampled

    classes.update({k: [] for k in classnames_added})
    all_classes = classnames_kept + classnames_added

    # add hallucinated fragments, evenly distributed over all classes

    n_hall_fragments = int(len(list(chain.from_iterable(gold_classes.values())))
                           * fragment_add)

    if n_hall_fragments > 0:
        rands = np.random.random((n_hall_fragments,))
        bins = np.linspace(0, 1, len(all_classes) + 1)
        hist = np.histogram(rands, bins)[0]
        add_per_class = dict(zip(all_classes, hist))

        for k in classes:
            for _ in range(add_per_class[k]):
                classes[k].append(random_fragment(intervals, classes[k]))

    # remove empty classes
    classes = {k: v for k, v in classes.iteritems() if v != []}

    # reset classID indexing
    ix = {k: tde.corpus.ClassID(i) for i, k in enumerate(classes.keys())}
    classes = {ix[k]: v for k, v in classes.iteritems()}

    return classes


if __name__ == '__main__':
    def parse_args():
        parser = argparse.ArgumentParser(
            prog='make_mockclasses.py',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='Mock output from discovery algorithm.',
            epilog="""Example usage:

$ python make_mockclasses.py mycorpus.phn output.classes --jitter=0.1 --classdrop=0.2 --classadd=0.2 --fragmentdrop=0.1 --fragmentadd=0.1

will mock classes based on mycorpus.phn, jittering the interval boundaries
with 0.1 standard deviation, dropping 20% of classes, adding 20% new classes,
dropping 10% of fragments and adding 10% new fragments.

            """)
        parser.add_argument('infile', metavar='INPUT',
                            nargs=1,
                            help='input phone file')
        parser.add_argument('outfile', metavar='OUTPUT',
                            nargs=1,
                            help='output classes file')
        parser.add_argument('--jitter',
                            action='store',
                            dest='jitter',
                            default=0.0,
                            help='interval boundary jitter')
        parser.add_argument('--classdrop',
                            action='store',
                            dest='classdrop',
                            default=0.0,
                            help='fraction of classes to drop')
        parser.add_argument('--classadd',
                            action='store',
                            dest='classadd',
                            default=0.0,
                            help='fraction of classes to hallucinate')
        parser.add_argument('--fragmentdrop',
                            action='store',
                            dest='fragmentdrop',
                            default=0.0,
                            help='fraction of fragments to drop')
        parser.add_argument('--fragmentadd',
                            action='store',
                            dest='fragmentadd',
                            default=0.0,
                            help='fraction of fragments to hallucinate')
        return vars(parser.parse_args())

    args = parse_args()
    infile = args['infile'][0]
    outfile = args['outfile'][0]

    fragments = tde.reader.read_phone_file(infile)
    JITTER = float(args['jitter'])
    FRAGMENT_DROP = float(args['fragmentdrop'])
    CLASS_DROP = float(args['classdrop'])
    FRAGMENT_ADD = float(args['fragmentadd'])
    CLASS_ADD = float(args['classadd'])

    new_classes = generate_classes(fragments, JITTER,
                                   FRAGMENT_DROP, CLASS_DROP,
                                   FRAGMENT_ADD, CLASS_ADD)

    with open(outfile, 'w') as fid:
        for k in sorted(new_classes.keys()):
            fragments = new_classes[k]
            fid.write('Class {0}\n'.format(k.ID))
            for fragment in sorted(fragments, key=lambda x: x.name):
                fid.write('{0} {1:.3f} {2:.3f}\n'.format(
                    fragment.name,
                    fragment.interval.start,
                    fragment.interval.end
                ))
            fid.write('\n')
