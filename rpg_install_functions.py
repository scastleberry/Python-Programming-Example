#!/usr/bin/python

### This file contains a library of sundry functions used for the file processing that occurs in the automated RPG installation software, 
### as well as for other RPG file processing scripts.
###
### Created by: Stephen Castleberry (stephen.castleberry@noaa.gov) - ROC/CIMMS - 9/2016
###


# unique_vals:
#
# Finds and returns a sorted list of all unique elements in the input list.
#
# INPUT:
#	source_l: A list of values that may contain duplicate entries.
#
# OUTPUT:
#	unique_l: A sorted list of all the uniqe elements from the input source list.
#
def unique_vals(source_l):
	# Error-check inputs.
	if not type(source_l) is list:
		return([])
	
	unique_l = list(set(source_l))
	unique_l.sort()
	
	return(unique_l)
	
# End unique_vals


# zeros:
#
# Creates a list of integer zeros with the length specified.
#
# INPUT:
#	list_length: A scalar integer specifying the length of the list of zeros to create
#
# OUTPUT:
#	z_list: A list of length list_length of integer zeros
#
def zeros(list_length):
	import numpy as np
	
	# Error-check inputs.
	if not type(list_length) is int:
		return([])
	
	z_list = np.zeros(list_length)
	z_list = z_list.tolist()
	z_list[:] = [int(i) for i in z_list]
	
	return(z_list)
	
# End zeros


# search_dir:
#
# Searches the input directory for files named according to the input specification(s).
#
# INPUT:
# 	target_dir: a string specifying the full path to the directory to be searched
# 	mandatory_file_list: a list of strings, each of which must occur in the filename of a discreet file within the target_dir
# 	args: optional; any additional individual strings for which to search the filenames of the files in the target_dir
#
# OUTPUT:
#	flag_l: a list of numeric flags (integers) specifying whether or not the target_dir exists, the mandatory files were found, 
#		and if the optional file(s) were found
#
def search_dir(target_dir,mandatory_file_list,*args):
	import os
	import numpy as np
			
	td_flag = 0
	mf_flag = 0
	a_flags = zeros(len(args))
	
	flag_l = [td_flag,mf_flag] + a_flags
	
	mf_check = zeros(len(mandatory_file_list))
	for m in range(len(mandatory_file_list)):
		m_e = mandatory_file_list[m]
		if type(m_e) is str:
			mf_check[m] = 1
	
	a_check = zeros(len(args))
	for a in range(len(args)):
		a_e = args[a]
		if type(a_e) is str:
			a_check[a] = 1

	# Error-check inputs.
	if not type(target_dir) is str or not np.all(mf_check) or not np.all(a_check):
		return(flag_l)
	
	if os.path.isdir(target_dir):
		td_flag = 1
		td_files = os.listdir(target_dir)
		td_files.sort()
		td_f_check_l = zeros(len(mandatory_file_list))

		for t in td_files:
			for m in range(len(mandatory_file_list)):
				mf = mandatory_file_list[m]
				if mf in t:
					td_f_check_l[m] = 1
					break
			for a in range(len(args)):
				a_e = args[a]
				if a_e in t:
					a_flags[a] = 1
		
		if np.all(td_f_check_l):
			mf_flag = 1

	flag_l = [td_flag,mf_flag] + a_flags
	return(flag_l)

# End search_dir

