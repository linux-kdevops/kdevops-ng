# SPDX-License-Identifier: copyleft-next-0.3.1
# fio's JSON into the metrics of a sample, tab-separated: name, value,
# unit and which way is better. $device is the name of the device the
# job ran on, as disk_util has it. Of the write direction, the first
# entry of jobs[] gives the job: a job file that starts several jobs sets
# group_reporting, which gives fio one entry for all of them.
.jobs[0].write as $write
| (.disk_util | map(select(.name == $device))[0]
	| if . == null then error("disk_util has no " + $device) else . end) as $disk
| [
	["iops", $write.iops, "1/s", "higher"],
	["bw", $write.bw_bytes, "B/s", "higher"],
	["clat_mean", $write.clat_ns.mean, "ns", "lower"],
	["clat_p99", $write.clat_ns.percentile["99.000000"], "ns", "lower"],
	["write_ios", $disk.write_ios, "count", "lower"],
	["write_merges", $disk.write_merges, "count", "higher"]
][] | @tsv
