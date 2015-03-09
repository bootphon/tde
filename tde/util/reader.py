"""Functions for reading corpus and class files.
"""
import re
from collections import defaultdict


from tde.data.corpus import Corpus
from tde.data.fragment import FragmentToken
from tde.data.segment_annotation import SegmentAnnotation
from tde.data.interval import Interval, IntervalDB
from tde.data.classes import ClassID, ClassDict


class ReadError(Exception):
    pass


def read_split_single(s):
    mapping = defaultdict(list)
    for line in s.split('\n'):
        if line == '':
            continue
        name, start, end = line.strip().split(' ')
        mapping[name].append((float(start), float(end)))
    return IntervalDB({k: sorted(v) for k, v in mapping.iteritems()})


def read_split_multiple(s):
    return [read_split_single(s0) for s0 in s.split('\n\n')]


def load_split(fname, multiple=False):
    with open(fname) as fid:
        s = fid.read()
    if multiple:
        r = read_split_multiple(s)
    else:
        r = read_split_single(s)
    return r

def load_classfile(fname):
    with open(fname, 'r') as fid:
        contents = fid.read()
    return read_classfile(contents)


def read_classfile(contents):
    """Read in class file.

    Parameters
    ----------
    contents : string

    Returns
    -------
    r : dict from ClassID to list of FragmentToken

    """
    classp = re.compile(r"^Class (?P<classID>\d+)(?: (?P<mark>.+))?$")
    r = {}
    curr = []  # list of FragmentTokens without mark
    curr_class = None

    for lineno, line in enumerate(contents.split('\n')):
        m = re.match(classp, line)
        if m:  # on a line with a class label
            if curr_class is None:
                curr_class = ClassID(int(m.group('classID')),
                                     m.group('mark'))
            else:
                raise ValueError('new class while reading class')
        else:  # on an interval line or a whitespace line
            if len(line.strip()) > 0:
                split = line.strip().split(' ')
                name = split[0]
                start = float(split[1])
                end = float(split[2])
                interval = Interval(start, end)
                curr.append(FragmentToken(name, interval, None))
            else:  # whitespace line, reset
                if curr_class is None:
                    continue
                    # if lineno == 0:
                    #     continue
                    # print lineno, line
                    # raise ValueError('attempting to end reading class '
                    #                  'while not reading class in line {0}'
                    #                  .format(lineno))
                r[curr_class] = tuple(curr)
                curr = []
                curr_class = None
    if not curr_class is None:
        r[curr_class] = tuple(curr)
    return r


def read_annotation(contents):
    ID_prev = None
    interval_prev = None
    r = []
    tokenlist_curr = []
    for line_idx, line in enumerate(contents.split('\n')):
        if line == '':
            continue
        try:
            ID_curr, start, stop, mark = line.strip().split(' ')
        except ValueError:
            raise ReadError('badly formatted line {1}: {0}'
                            .format(line, line_idx))
        try:
            start = float(start)
            stop = float(stop)
        except ValueError:
            raise ReadError('could not convert string to float in line {1}: {0}'
                            .format(line, line_idx))
        try:
            interval_curr = Interval(start, stop)
        except ValueError:
            raise ReadError('invalid interval in line {0}: ({1:.3f} {2:.3f})'
                            .format(line_idx, start, stop))

        token = FragmentToken(ID_curr, interval_curr, mark)

        if ID_prev is None:
            tokenlist_curr = [token]
            ID_prev = ID_curr
        elif ID_prev == ID_curr:
            if interval_prev.is_left_adjacent_to(interval_curr):
                tokenlist_curr.append(token)
            else:
                r.append(tokenlist_curr)
                tokenlist_curr = [token]
        else:  # ID_prev != ID_curr
            r.append(tokenlist_curr)
            tokenlist_curr = [token]
            ID_prev = ID_curr
        interval_prev = interval_curr
    r.append(tokenlist_curr)
    return r


def load_annotation(filename):
    """Read in a file with annotations in the Buckeye style.

    The phone file must be formatted with the following, space-separated
    columns:

    identifier start stop symbol

    Parameters
    ----------
    filename : string

    Returns
    -------
    r : list of list of FragmentToken

    """
    with open(filename, 'r') as fid:
        contents = fid.read()
    return read_annotation(contents)


def load_corpus_txt(filename):
    """Read file with phone annotation and convert into Corpus object.

    The phone file must be formatted with the following, space-separated
    columns:
    identifier start stop symbol

    Parameters
    ----------
    filename : string

    Returns
    -------
    c : Corpus

    """
    return tokenlists_to_corpus(load_annotation(filename))


def tokenlists_to_corpus(tokenlists):
    """Convert a list of tokens to Corpus object

    Parameters
    ----------
    tokenlists : list of list of FragmentToken

    Returns :
    c : Corpus

    """
    fas = []  # FileAnnotations
    for tokenlist in tokenlists:
        fname = tokenlist[0].name
        fas.append(SegmentAnnotation(fname, tokenlist))
    return Corpus(fas)


def load_classes_txt(filename, corpus, split=None):
    """Load class file, i.e. the output of a detector and calculate the
    corresponding annotation according to `corpus`.

    The class file must be formatted as follows:
    Class <ID1> (<symbol>)
    name 0.000 1.000
    ...

    Class <ID2> (<symbol>)
    name 1.200 3.400
    ...


    Parameters
    ----------
    filename : string
    corpus : Corpus
        Contains the annotation by which to annotate the classes.

    Returns
    -------
    n : dict from ClassID to tuple of FragmentToken
        Annotated classes.

    """
    raw = load_classfile(filename)  # without annotation
    # add mark annotation
    return annotate_classes(raw, corpus, split=split)


def annotate_classes(clsdict, corpus, split=None):
    new = {}  # with annotation
    errors = []
    check_split = not (split is None)
    for classID, tokenlist in clsdict.iteritems():
        newtokens = []
        for token in tokenlist:
            filename = token.name
            interval = token.interval
            if check_split and not split.is_covered(filename, interval):
                errors.append(token)
            else:
                annot = tuple(corpus.annotation(filename, interval))
                newtokens.append(FragmentToken(filename, interval, annot))
        if len(newtokens) > 0:
            newtokens = tuple(newtokens)
            new[classID] = newtokens
    return ClassDict(new), errors
