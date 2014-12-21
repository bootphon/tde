from collections import defaultdict

from .corpus import Interval, FragmentToken, ClassDict

class FileNameError(Exception):
    pass

def load_split(fname):
    mapping = defaultdict(list)
    for line in open(fname):
        name, start, end = line.strip().split(' ')
        mapping[name].append((float(start), float(end)))
    return {k: sorted(v) for k, v in mapping.iteritems()}


def largest_overlap(mapping, query_fname, query_start, query_end):
    """Return the interval in mapping that has the largest overlap
    with the query interval.
    """
    try:
        sublist = mapping[query_fname]
    except KeyError:
        raise FileNameError(query_fname)
    if query_start > query_end:
        raise ValueError('interval start is larger than interval end: '
                         '{2} [{0:.3f}, {1:.3f}]'.format(query_start,
                                                         query_end,
                                                         query_fname))
    if query_start < 0.0 or query_end < 0.0:
        raise ValueError('interval start and end must be greater than zero'
                         ', not: {2} [{0:.3f}, {1:.3f}]'.format(query_start,
                                                                query_end,
                                                                query_fname))
    best_interval = None
    best_overlap = 0
    for found_start, found_end in sublist:
        if found_start <= query_start < found_end:
            # nonzero overlap
            overlap = min(query_end, found_end) - max(query_start, found_start)
            if overlap > best_overlap:
                best_interval = (max(found_start, query_start),
                                 min(found_end, query_end))
                best_overlap = overlap
        elif query_start <= found_start < query_end:
            overlap = min(query_end, found_end) - max(query_start, found_start)
            if overlap > best_overlap:
                best_interval = (max(found_start, query_start),
                                 min(found_end, query_end))
                best_overlap = overlap
    if best_interval is None:
        raise KeyError('no interval found for {0} [{1:.3f}, {2:.3f}]'.format(
            query_fname, query_start, query_end))
    return best_interval

def truncate_intervals(clsdict, corpus, mapping):
    disc = {}
    interval_errors = []
    filename_errors = []
    bad_intervals = []
    for class_id in clsdict:
        fragments = []
        for fragment in clsdict[class_id]:
            qname = fragment.name
            qstart = fragment.interval.start
            qend = fragment.interval.end
            try:
                finterval = largest_overlap(mapping, qname,
                                            qstart, qend)
            except FileNameError as e:
                filename_errors.append(e.message)
                continue
            except ValueError:
                bad_intervals.append(fragment)
                continue
            except KeyError:
                interval_errors.append(fragment)
            fstart, fend = finterval
            if qstart != fstart or qend != fend:
                newstart = max(qstart, fstart)
                newend = min(qend, fend)
                newinterval = Interval(newstart, newend)
                newmark = corpus.annotation(qname, newinterval)
                fragment = FragmentToken(qname,
                                         newinterval,
                                         newmark)
            fragments.append(fragment)
        disc[class_id] = tuple(fragments)
    return ClassDict(disc), interval_errors, filename_errors, bad_intervals

def check_intervals(clsdict, mapping):
    interval_errors = []
    filename_errors = []
    bad_intervals = []
    for fragment in clsdict.iter_fragments():
        qname = fragment.name
        qstart = fragment.interval.start
        qend = fragment.interval.end
        try:
            finterval = largest_overlap(mapping, qname,
                                        qstart, qend)
        except FileNameError as e:
            filename_errors.append(e.message)
            continue
        except ValueError:
            bad_intervals.append(fragment)
            continue
        except KeyError:
            interval_errors.append(fragment)
            continue
        fstart, fend = finterval
        if qstart != fstart or qend != fend:
            interval_errors.append((fragment, fstart, fend))
    return interval_errors, filename_errors, bad_intervals
