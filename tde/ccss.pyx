## cython ccss.pyx
## gcc -shared -pthread -fPIC -fwrapv -O3 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -I/usr/lib/python2.7/site-packages/numpy/core/include -o ccss.so ccss.c


import numpy as np
cimport numpy as np
cimport cython
ITYPE = np.long
ctypedef np.long_t ITYPE_t


cdef int triangle(int n):
    cdef long  r = 0
    cdef int i
    for i in xrange(1, n):
        r += i
    return r


@cython.boundscheck(False)
def allcommonsubstrings(np.ndarray[ITYPE_t, ndim=1] XA,
                        np.ndarray[ITYPE_t, ndim=1] XB,
                        int minlength, int maxlength,
                        int same=0):
    cdef int mA, mB, i, j, mT, sA, sB, b, score, start, end, max
    mA = XA.shape[0]
    mB = XB.shape[0]
    cdef np.ndarray[ITYPE_t, ndim=2] r
    cdef ITYPE_t[:] starters
    cdef np.ndarray[ITYPE_t, ndim=1] tmp
    cdef ITYPE_t[:, :] diag

    cdef np.ndarray[ITYPE_t, ndim=2] m = np.zeros((mA+1, mB+1), dtype=ITYPE)

    for i in xrange(1, mA+1):
        for j in xrange(1, mB+1):
            if same and i == j:
                continue
            if XA[i-1] == XB[j-1]:
                m[i, j] = m[i-1, j-1] + 1

    tmp = np.argsort(m, axis=None)
    tmp = tmp[np.where(np.ravel(m)[tmp] >= minlength-1)]

    mT = tmp.shape[0]
    starters = np.empty((mT,), dtype=ITYPE)
    for i in xrange(mT):
        starters[i] = tmp[mT-i-1]

    if starters.shape[0] == 0:
        return None

    max = m[np.unravel_index(starters[0], dims=(mA+1, mB+1))]
    r = np.empty((mT*triangle(max), 3), dtype=ITYPE)
    i = 0
    while True:
        sA, sB = np.unravel_index(starters[0], dims=(mA+1, mB+1))
        score = m[sA, sB]

        # diagonal over m leading up to starter
        diag = np.empty((score+1, 2), dtype=ITYPE)
        for j in xrange(score+1):
            diag[j, 0] = sA - score + j
            diag[j, 1] = sB - score + j

        for start in xrange(score-minlength+1):
            for end in xrange(start + minlength, score+1):
                if end - start > maxlength:
                    continue
                r[i, 0] = diag[start, 0]
                r[i, 1] = diag[start, 1]
                r[i, 2] = end - start
                i += 1
        starters = np.fromiter((x for x in starters
                                if not x in np.ravel_multi_index(diag.T,
                                                                 dims=(mA+1, mB+1))),
                               dtype=ITYPE)
        if starters.shape[0] == 0:
            break

    return r[:i, :]
