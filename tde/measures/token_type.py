"""Evaluate token and type measures"""

from __future__ import division

from tde.util.printing import verb_print
from tde.util.functions import unique, iterator_length

def evaluate_token_type(disc_clsdict, wrd_corpus,
                        verbose=False, debug=False):
    n_word_tokens = iterator_length(unique(wrd_corpus.iter_fragments()))
    word_types = set(f.mark for f in wrd_corpus.iter_fragments())
    n_word_types = len(word_types)
    n_disc_fragments = iterator_length(disc_clsdict.iter_fragments())

    with verb_print('querying words', verbose, True, True, True):
        types_hit = set()
        types_seen = set()
        hits = 0
        for disc_fragment in disc_clsdict.iter_fragments():
            disc_start = disc_fragment.interval.start
            disc_end = disc_fragment.interval.end
            wrd_tokens = wrd_corpus.tokens(disc_fragment.name,
                                           disc_fragment.interval)
            types_seen.add(tuple(f.mark for f in wrd_tokens))
            if len(wrd_tokens) != 1:
                continue
            goldtok = wrd_tokens[0]
            if abs(goldtok.interval.start - disc_start) > 0.03:
                continue
            if abs(goldtok.interval.end - disc_end) > 0.03:
                continue
            types_hit.add(goldtok.mark)
            hits += 1

    token_prec = hits / n_disc_fragments
    token_rec = hits / n_word_tokens

    type_prec = len(types_hit) / len(types_seen)
    type_rec = len(types_hit) / n_word_types

    return token_prec, token_rec, type_prec, type_rec
