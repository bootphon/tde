"""Functions for reading corpus and class files.
"""
import re

import numpy as np

from corpus import FragmentToken, Corpus, SegmentAnnotation, Interval, ClassID

class ReadError(Exception):
    pass

def abuts_left(i1, i2, tol=1e-3):
    """Determine whether i1 is directly to the left of i2.

    Parameters
    ----------
    i1, i2 : Interval

    Returns
    -------
    b : boolean
        True iff i1 is directly to the left of i2.
    """
    return np.isclose(i1.end, i2.start, atol=tol)


def read_phone_file(filename):
    """Read in a file with phone annotations.

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
    ID_prev = None
    interval_prev = None
    r = []
    tokenlist_curr = []
    for line_idx, line in enumerate(open(filename)):
        try:
            ID_curr, start, stop, phone = line.strip().split(' ')
        except ValueError:
            raise ReadError('badly formatted line {1}: {0}'
                            .format(line, line_idx))
        try:
            start = float(start)
            stop = float(stop)
            interval_curr = Interval(start, stop)
        except ValueError:
            raise ReadError('could not convert string to float in line {1}: {0}'
                            .format(line, line_idx))
        token = FragmentToken(ID_curr, interval_curr, phone)

        if ID_prev is None:
            tokenlist_curr = [token]
            ID_prev = ID_curr
        elif ID_prev == ID_curr:
            if abuts_left(interval_prev, interval_curr):
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


def corpus_annotation_from_phone_file(filename):
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
    tokenlists = read_phone_file(filename)
    fas = []  # FileAnnotations
    for tokenlist in tokenlists:
        fname = tokenlist[0].name
        fas.append(SegmentAnnotation(fname, tokenlist))
    return Corpus(fas)


def load_classes(filename, corpus):
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
    raw = read_classfile(filename)  # without annotation

    # add mark annotation
    new = {}  # with annotation
    for classID, tokenlist in raw.iteritems():
        newtokens = []
        for token in tokenlist:
            filename = token.name
            interval = token.interval
            annot = corpus.annotation(filename, interval)
            newtokens.append(FragmentToken(filename, interval, annot))
        newtokens = tuple(newtokens)
        new[classID] = newtokens
    return new


def read_classfile(filename):
    """Read in class file.

    Parameters
    ----------
    filename : string

    Returns
    -------
    r : dict from ClassID to list of FragmentToken

    """
    classp = re.compile(r"^Class (?P<classID>\d+)(?: (?P<mark>.+))?$")
    r = {}
    curr = []  # list of FragmentTokens without mark
    curr_class = None

    for lineno, line in enumerate(open(filename, 'r')):
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
                curr.append(FragmentToken(name, interval))
            else:  # whitespace line, reset
                if curr_class is None:
                    if lineno == 0:
                        continue
                    print lineno, line
                    raise ValueError('attempting to end reading class '
                                     'while not reading class in line {0}'
                                     .format(lineno))
                r[curr_class] = curr
                curr = []
                curr_class = None
    return r
