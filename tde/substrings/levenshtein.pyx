import numpy as np
cimport numpy as np
cimport cython
ITYPE=np.uint32
ctypedef np.uint32_t ITYPE_t

cdef inline ITYPE_t int_min(ITYPE_t a, ITYPE_t b): return a if a <= b else b
cdef inline ITYPE_t int_min3(ITYPE_t a, ITYPE_t b, ITYPE_t c):
    return int_min(int_min(a, b), c)

@cython.boundscheck(False)
def distance(np.ndarray[ITYPE_t, ndim=1] XA, np.ndarray[ITYPE_t, ndim=1] XB):
    cdef ITYPE_t mA, mB, i, j
    mA = XA.shape[0]
    mB = XB.shape[0]
    cdef np.ndarray[ITYPE_t, ndim=2] H = np.zeros((mA+1, mB+1), dtype=ITYPE)
    H[:, 0] = np.arange(0, mA+1)
    H[0, :] = np.arange(0, mB+1)

    for i in xrange(1, mA+1):
        for j in xrange(1, mB+1):
            if XA[i-1] == XB[j-1]:
                H[i, j] = H[i-1, j-1]
            else:
                H[i, j] = int_min3(H[i-1, j] + 1,
                                   H[i, j-1] + 1,
                                   H[i-1, j-1] + 1)
    return H[mA, mB]
