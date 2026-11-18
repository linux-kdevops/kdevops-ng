# SPDX-License-Identifier: copyleft-next-0.3.1
# fio's JSON into the facts of a sample, tab-separated: when the job
# started, as UTC, how long fio ran, in whole seconds as a record counts
# them, and the exit status, which is zero where every job's error is.
# timestamp_ms is when fio wrote the document, so the job's own start,
# job_start, is the start, and the run lasted to the timestamp.
[
	(.jobs[0].job_start / 1000 | floor | todate),
	((.timestamp_ms - .jobs[0].job_start) / 1000 | round),
	([.jobs[].error] | max)
] | @tsv
