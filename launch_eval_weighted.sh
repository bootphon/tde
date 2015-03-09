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
    echo "python bin/weighted_english_eval.py ${i} ${OUTDIR}res_${i##*/} ${KWARGS}"
    echo "export PATH=/home/roland/anaconda/bin:$PATH; python bin/weighted_english_eval.py ${i} ${OUTDIR}res_${i##*/} ${KWARGS}" > "qsub_${i##*/}"
    qsub -N eval2 -j y -cwd -q cpu  -S /bin/bash "qsub_${i##*/}"
done
