import sys
import os
from os.path import join as pjoin

input_dir = sys.argv[1]
systems = [d for d in os.listdir(input_dir) if os.path.exists(pjoin(input_dir, d, 'VERSION_0.1.2'))]

mcp, mcr, mcf, mwp, mwr, mwf, gcp, gcr, gcf, gwp, gwr, gwf, nc, cc, nw, cw, bcp, bcr, bcf, bwp, bwr, bwf, tocp, tocr, tocf, tycp, tycr, tycf, towp, towr, towf, tywp, tywr, tywf = ({},) * 34

for f in systems:
    matchfile = pjoin(input_dir, f, 'matching')
    with open(matchfile) as fin:
        for i in range(7):
            fin.readline()
        mcp[f] = fin.readline().split()[1]
        mcr[f] = fin.readline().split()[1]
        mcf[f] = fin.readline().split()[1]
        for i in range(9):
            fin.readline()
        mwp[f] = fin.readline().split()[1]
        mwr[f] = fin.readline().split()[1]
        mwf[f] = fin.readline().split()[1]

    groupfile = pjoin(input_dir, f, 'group')
    with open(groupfile) as fin:
        for i in range(7):
            fin.readline()
        gcp[f] = fin.readline().split()[1]
        gcr[f] = fin.readline().split()[1]
        gcf[f] = fin.readline().split()[1]
        for i in range(9):
            fin.readline()
        gwp[f] = fin.readline().split()[1]
        gwr[f] = fin.readline().split()[1]
        gwf[f] = fin.readline().split()[1]

    nlpfile = pjoin(input_dir, f, 'nlp')
    with open(nlpfile) as fin:
        for i in range(7):
            fin.readline()
        nc[f] = fin.readline().split()[1]
        cc[f] = fin.readline().split()[1]
        for i in range(9):
            fin.readline()
        nw[f] = fin.readline().split()[1]
        cw[f] = fin.readline().split()[1]

    boundfile = pjoin(input_dir, f, 'boundary')
    with open(boundfile) as fin:
        for i in range(7):
            fin.readline()
        bcp[f] = fin.readline().split()[1]
        bcr[f] = fin.readline().split()[1]
        bcf[f] = fin.readline().split()[1]
        for i in range(9):
            fin.readline()
        bwp[f] = fin.readline().split()[1]
        bwr[f] = fin.readline().split()[1]
        bwf[f] = fin.readline().split()[1]

    ttfile = pjoin(input_dir, f, 'token_type')
    with open(ttfile) as fin:
        for i in range(7):
            fin.readline()
        tocp[f] = fin.readline().split()[1]
        tocr[f] = fin.readline().split()[1]
        tocf[f] = fin.readline().split()[1]
        for i in range(9):
            fin.readline()
        tycp[f] = fin.readline().split()[1]
        tycr[f] = fin.readline().split()[1]
        tycf[f] = fin.readline().split()[1]
        for i in range(9):
            fin.readline()
        towp[f] = fin.readline().split()[1]
        towr[f] = fin.readline().split()[1]
        towf[f] = fin.readline().split()[1]
        for i in range(9):
            fin.readline()
        tywp[f] = fin.readline().split()[1]
        tywr[f] = fin.readline().split()[1]
        tywf[f] = fin.readline().split()[1]


print('measure, ' + ', '.join(systems))
print('matching cross talkers')
print('precision, ' + ', '.join(mcp[f] for f in systems))
print('recall, ' + ', '.join(mcr[f] for f in systems))
print('fscore, ' + ', '.join(mcf[f] for f in systems))
print('')
print('matching within talkers')
print('precision, ' + ', '.join(mwp[f] for f in systems))
print('recall, ' + ', '.join(mwr[f] for f in systems))
print('fscore, ' + ', '.join(mwf[f] for f in systems))
print('')
print('')
print('grouping cross talkers')
print('precision, ' + ', '.join(gcp[f] for f in systems))
print('recall, ' + ', '.join(gcr[f] for f in systems))
print('fscore, ' + ', '.join(gcf[f] for f in systems))
print('')
print('grouping within talkers')
print('precision, ' + ', '.join(gwp[f] for f in systems))
print('recall, ' + ', '.join(gwr[f] for f in systems))
print('fscore, ' + ', '.join(gwf[f] for f in systems))
print('')
print('')
print('boundary cross talkers')
print('precision, ' + ', '.join(bcp[f] for f in systems))
print('recall, ' + ', '.join(bcr[f] for f in systems))
print('fscore, ' + ', '.join(bcf[f] for f in systems))
print('')
print('boundary within talkers')
print('precision, ' + ', '.join(bwp[f] for f in systems))
print('recall, ' + ', '.join(bwr[f] for f in systems))
print('fscore, ' + ', '.join(bwf[f] for f in systems))
print('')
print('')
print('nlp cross talkers')
print('NED, ' + ', '.join(nc[f] for f in systems))
print('coverage, ' + ', '.join(cc[f] for f in systems))
print('')
print('nlp within talkers')
print('NED, ' + ', '.join(nw[f] for f in systems))
print('coverage, ' + ', '.join(cw[f] for f in systems))
print('')
print('')
