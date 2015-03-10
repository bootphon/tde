KWARGS=""
NCORES=1


while getopts "m:j:o:" options; do
    case "${options}" in
	m)
            MEASURE="${OPTARG}"
	    KWARGS="${KWARGS} -m ${MEASURE}"
            ;;
	j)
            NCORES="${OPTARG}"
	    KWARGS="${KWARGS} -j ${NCORES}"
            ;;
        o)
            OUTDIR="${OPTARG}/"
            ;;
	v)
	    KWARGS="{KWARGS} -v"
	    ;;
    esac
done

shift $((OPTIND-1))

echo $@

for i in "${@}"; do
    echo "python bin/english_eval2.py ${i} ${OUTDIR}res_${i##*/} ${KWARGS}"
    echo "#!/bin/sh" > "qsub_${i##*/}"
    # echo "export PATH=/home/roland/anaconda/bin:\$PATH" >> "qsub_${i##*/}"
    echo "module load python-anaconda" >> "qsub_${i##*/}"
    echo "python english_eval2.py ${i} ${OUTDIR}res_${i##*/} ${KWARGS}" >> "qsub_${i##*/}"
    qsub -N eval2 -j y -cwd -pe openmpi_ib $NCORES -q cpu  -S /bin/bash "qsub_${i##*/}"
done
