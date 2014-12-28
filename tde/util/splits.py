from tde.data.interval import Interval
from tde.data.fragment import FragmentToken
from tde.data.classes import ClassDict

def truncate_intervals(clsdict, corpus, mapping):
    disc = {}
    interval_errors = []
    filename_errors = []
    for class_id in clsdict:
        fragments = []
        for fragment in clsdict[class_id]:
            qname = fragment.name
            qstart = fragment.interval.start
            qend = fragment.interval.end
            try:
                finterval = mapping.largest_overlap(qname, fragment.interval)
            except KeyError:
                filename_errors.append(fragment.name)
                continue
            except ValueError:
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
    return ClassDict(disc), filename_errors, interval_errors

def check_intervals(clsdict, interval_db):
    """
    Check whether all the intervals in a ClassDict are also in an IntervalDB

    Parameters
    ----------
    clsdict : ClassDict
    interval_db : IntervalDB

    Returns
    -------
    interval_errors : list of FragmentToken
        List of fragments for which the interval could not be found.
    filename_errors : list of FragmentToken
        List of fragments for which the filename could not be found.
    """

    interval_errors = []
    filename_errors = []
    for fragment in clsdict.iter_fragments():
        try:
            finterval = interval_db.largest_overlap(fragment.name,
                                                    fragment.interval)
        except KeyError:
            import ipdb; ipdb.set_trace()
            filename_errors.append(fragment)
            continue
        except ValueError:
            import ipdb; ipdb.set_trace()
            interval_errors.append(fragment)
            continue
        # fstart, fend = finterval
        # qstart = fragment.interval.start
        # qend = fragment.interval.end
        # if qstart != fstart or qend != fend:
        #     interval_errors.append(fragment)
    return filename_errors, interval_errors
