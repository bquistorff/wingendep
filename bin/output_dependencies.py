#!/usr/bin/env python
#
import csv, sys, os.path

def error(message):
	sys.stderr.write(message + '\n')
	sys.exit(1)

def main(argv):
	if len(argv)!=(3+1) and len(argv)!=(4+1):
		error('usage: %s root_WPID procmon_log.csv proj_base_path [dep_fname]' % os.path.basename(argv[0]))
	
	proc_set = [argv[1]]
	log_fname = argv[2]
	proj_base = argv[3]
	if proj_base.endswith('\\'):
		proj_base=proj_base[:-1]
	
	init_read_files = set()
	ever_write_files = set()
	
	# read the string data
	with open(log_fname,  'r') as f:
		reader = csv.DictReader(f, delimiter=',')
		for line in reader:
			#create the process tree (start in Detail (PPID) column)
			if line["Operation"].startswith('Process Start') and line["Parent PID"] in proc_set:
				proc_set.append(line["PID"])
				continue
			
			#Then filter events by the WPID tree.
			if line["Operation"].startswith('ReadFile') and line["PID"] in proc_set and line["Path"].startswith(proj_base):
				fname = line["Path"][(len(proj_base)+1):]
				if fname not in ever_write_files:
					init_read_files.add(fname)
						
			if line["Operation"].startswith('WriteFile') and line["PID"] in proc_set and line["Path"].startswith(proj_base):
				fname = line["Path"][(len(proj_base)+1):]
				ever_write_files.add(fname)
	
	#remove if the files ultimately were deleted. Sets become lists
	init_read_files = [fname for fname in init_read_files if os.path.isfile(fname)]
	ever_write_files = [fname for fname in ever_write_files if os.path.isfile(fname)]
	
	#Output the information
	if len(argv)==(4+1):
		with open(argv[4], "w") as dep_file:
			if len(init_read_files)>0:
				dep_file.write('target :')
				for fname in init_read_files:
					dep_file.write(' ' + fname)
				dep_file.write('\n')
				
			if len(ever_write_files)>0:
				for fname in ever_write_files:
					dep_file.write(fname + ' ')
				dep_file.write(' : target\n')
	
	else:
		print 'Project files initially read:'
		for fname in init_read_files:
			print fname
		
		print ''
		print 'Project files ever written:'
		for fname in ever_write_files:
			print fname

if  __name__ =='__main__':
	main(sys.argv)
	