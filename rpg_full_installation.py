#!/usr/bin/python

### After a user is logged in to an ORPG# account, and has verified that NONE of the files 
### on the current account are being used by anyone else and that there are NO active RPG
### playbacks in progress on the current ORPG# account, this script will clear the contents of the
### current ORPG# account, copy over the needed files from the specified RPG engineering release
### (Build) from the CM library, install the RPG software in the ORPG# account, and configure
### certain environmental variables. Certain optional steps can also be performed if needed.
###
### Created by: Stephen Castleberry (stephen.castleberry@noaa.gov) - ROC/CIMMS - 5/2015
###
### Documentation/Software References: Steve Smith, Dave Zittel, Dan Berkowitz, Lindsey Richardson, Rich Murnan, Bob Lee
###

# Import the needed libraries.
try:
	# Python version 2.X:
	from Tkinter import Tk
except ImportError:
	# Python version 3.X:
	from tkinter import Tk
import sys, os
import subprocess as sp
import tkFileDialog as tkf
import rpg_install_functions as rif

# Set constants / adaptable parameters.
n_args = 5
valid_rpg_builds = [14,15,16,161,17,18]
pdg_excludes = [14]
base_importBuilds_dir = '/import/builds_cmlnxsvr/linux'
base_importBuildsArchive_dir = '/import/archive_cmlnxsvr/linux'
mand_importFiles_spec = ['orpg_adaptation_build','orpg_bld_build','orpg_comms_build','orpg_toolsbld_build','install_rpg']
srcCode_file_spec = 'orpg_src.tar.gz'
build_v_spec = 'v1.'
user_spec = 'orpg'
rmt_port_lineSpec = 'export RMTPORT=50000'
rmt_port_scale = 6
path_ext_locSpec = 'export MANPATH=$HOME/man:/usr/local/man:/usr/share/man'
comp_envVar_lineSpec = 'export ARCH=lnux_x86'
gt_shortcut_lineSpec = 'unset SESSION_MANAGER DBUS_SESSION_BUS_ADDRESS # Allow ~rpg to run Gnome apps'
base_bt_dir = '/import/apps/data'
blockage_dirSpec = 'blockage_B12'
terrain_dirSpec = 'terrain_B10'
qc_inputs_fname = 'qc_inputs.txt'
gedit_settings_fname = 'gedit_settings.txt'
gedit_settings_maxRhelV = 5

# Set exit codes.
success_code = 0
start_code = 2 # Program is successful, but the RPG software is also signaled to start after this script ends.
abort_code = 3
error_code = 1

# Misc. formatting.
valid_rpg_builds[:] = [str(i) for i in valid_rpg_builds]

# Show explanatory usage text.
if len(sys.argv) == 1 or sys.argv[1] == 'qc_inputs=$':
	print "\n"
	print """This program will fully install a specified engineering RPG software release (Build) on the ORPG# account to which the user is currently 
logged in. All current contents of the ORPG# account will be deleted, the needed files copied over from the CM library, the RPG software 
installed (using the install_rpg script from CM), and certain environmental variables / other files configured as specified.\n"""
	print """WARNING!: Before executing this script, ensure that none of the current files on the current ORPG# account are needed by anyone. 
Make backup copies of those items elsewhere if so. Also ensure no one is running an RPG playback on the ORPG# account currently. 
These checks are ESSENTIAL since this script will execute irreversible recursive delete commands before installing the new software build.\n"""
	print """EXECUTION METHOD: (Ensure that the .txt files PATH_Ext, Compiler_Env_Vars, PDGUI_Env_Vars, GNTERM_Shortcut, """+ qc_inputs_fname.split('.')[0]+ """, 
and """+ gedit_settings_fname.split('.')[0]+ """ are all available in the same directory as this script.)\n\n"""
	print "For the Python script alone (From this script's directory):\n"
	print "./rpg_full_installation.py Build# Build_Dir_Override SrcComp_Flag Rad_Site MRPG_Start_Flag\n"
	print "When using the BASH wrapper program (PREFERRED METHOD, from this script's directory):\n"
	print ". full_install_rpg Build# Build_Dir_Override SrcComp_Flag Rad_Site MRPG_Start_Flag\n"
	print "When using the external BASH wrapper program (PREFERRED METHOD, from any directory):\n"
	print ". inrpg Build# Build_Dir_Override SrcComp_Flag Rad_Site MRPG_Start_Flag\n"
	print """To use the inrpg shortcut script from any directory, ensure it is soft-linked in your personal bin directory by first entering: 
ln -s /import/apps/scastleberry/Scripts/CSH/inrpg ~/bin/. from the command line and ensure your ~/bin directory is appended to the current ORPG# account's PATH variable.\n\n"""
	print """Build# is the engineering RPG software version to be installed. 
Valid Options: """+ ', '.join(valid_rpg_builds)+ """\n"""
	print """Build_Dir_Override, if selected, will allow the user to manually select the directory from which to install the RPG software, instead of it being automatically selected based on the Build# parameter.
Valid Options: 1 (for YES), 0 (for NO)\n"""
	print """SrcComp_Flag, if selected, will also extract the build's source code from the included file: """+ srcCode_file_spec+ """, and configure compiler environmental variables. 
Valid Options: 1 (for YES), 0 (for NO)\n"""
	print """Rad_Site, if specified, will copy over that site's blockage and terrain data (.lb files) from import to the ORPG# account, and will update the site adaptation data. 
Valid Options: xxxx (four letter radar site abbreviation, lower-case), 0 (for no site)\n"""
	print """MRPG_Start_Flag, if selected, will automatically start the RPG software, provided the BASH wrapper program execution method is used. 
Valid Options: 1 (for YES), 0 (for NO)\n"""
	print "\n"

	sys.exit(abort_code)
	
elif len(sys.argv) != n_args + 1:
	print "\n"
	print "ERROR: Incorrect number of input arguments. Program requires "+ str(n_args)+ ", but recieved "+ str(len(sys.argv)-1)+ ".\n"
	sys.exit(error_code)
	
# Load input parameters.
rpg_build_num = sys.argv[1]
build_dir_override = sys.argv[2]
srcComp_flag = sys.argv[3]
rad_site = sys.argv[4]
mrpg_start_flag = sys.argv[5]

# Since all data that is currently in the given ORPG account will be permanently deleted, verify that the user does, in fact, wish to proceed.
print "\n"
pointOfNoReturn_choice = raw_input("CONFIRM: Proceed with RPG software installation on the current ORPG account? [y (for YES), n (for NO)]\n")
while pointOfNoReturn_choice != 'y' and pointOfNoReturn_choice != 'n':
	print "\n"
	print "ERROR: "+ str(pointOfNoReturn_choice)+ " is not a valid value for the RPG installation confirmation option.\n"
	print "The valid options are: y (for YES) or n (for NO)\n"
	pointOfNoReturn_choice = raw_input("Enter a valid option for the RPG installation confirmation option:\n") 

if pointOfNoReturn_choice == 'n':
	print "\n"
	print "Program execution canceled.\n"
	sys.exit(abort_code)

# Ensure the user is actually logged into an ORPG account.
user_obj = sp.Popen('whoami',stdout=sp.PIPE)
user = user_obj.stdout.read()
user = user.strip('\n')

if user_spec not in user:
	print "\n"
	print "ERROR: Not logged in to a valid ORPG account.\n"
	print "Current user is: "+ user+ "\n"
	print "Program execution terminated!\n"
	sys.exit(error_code)

# Acquire the RHEL version of the Linux machine currently being used.
rhel_f = open('/etc/redhat-release','r')
rhel_l = rhel_f.readlines()
rhel_f.close()
rhel_v = int(rhel_l[0].split(' ')[-2].split('.')[0])

# Get the directory of the script (needed for loading auxiliary files).
script_dir = os.path.dirname(os.path.abspath(__file__))

# Get the home ORPG# directory.
home_dir = os.environ['HOME']

# Get the ORPG number.
user_arr = user.split(user_spec)
orpg_num = int(user_arr[1])

# Get the kernel (32-bit or 64-bit) of the Linux OS being used, verify that it is recognized.
kernel_obj = os.uname()
kernel = kernel_obj[-1]

# kernel should be 'i686' (for 32-bit) or 'x86_64' (for 64-bit).
if kernel == 'i686':
	kernel = '32-bit'
elif kernel == 'x86_64':
	kernel = '64-bit'
else:
	print "\n"
	print "ERROR: Unrecognized OS kernel: "+ kernel+ "\n"
	print "Program execution terminated!\n"
	sys.exit(error_code)

# Validate the input.
while rpg_build_num not in valid_rpg_builds:
	print "\n"
	print "ERROR: "+ rpg_build_num+ " is not a valid RPG build number.\n"
	print "The valid RPG build number options are: \n\n"+ '\n'.join(valid_rpg_builds)+ "\n"
	rpg_build_num = raw_input("Enter a valid RPG build number:\n")

rpg_bn = int(rpg_build_num)

# Note that this check will need to be modified when RPG Build 100 comes into existence. 
# Most of us likely will be dead by then, so this issue is not my problem.
if rpg_bn >= 100:
	rpg_bn = rpg_bn / 10.0

if rpg_bn <= 18 and kernel == '32-bit':
	rpg_bn_krn_f = 32
elif rpg_bn == 18 and kernel == '64-bit':
	rpg_bn_krn_f = 1864
elif rpg_bn > 18 and kernel == '64-bit':
	rpg_bn_krn_f = 64
else:
	print "\n"
	print "ERROR: RPG Build "+ rpg_build_num+ " is not compatible with a "+ kernel+ " OS kernel.\n"
	print "Program execution terminated!\n"
	sys.exit(error_code)

while build_dir_override != '0' and build_dir_override != '1':
	print "\n"
	print "ERROR: "+ str(build_dir_override)+ " is not a valid value for the RPG build directory override option.\n"
	print "The valid options are: 1 (for YES) or 0 (for NO)\n"
	build_dir_override = raw_input("Enter a valid option for the RPG build directory override option:\n")
	
build_dir_override = int(build_dir_override)

bdo_flag = 0
if build_dir_override == 1:
	# Use the previously selected RPG Build directory as the starting search path, if possible.
	if os.path.isfile(script_dir+'/Build_Dir_Override_Prev_Dir.txt'):
		bdo_pd_f = open(script_dir+'/Build_Dir_Override_Prev_Dir.txt','r')
		bdo_pd_l = bdo_pd_f.readlines()
		bdo_pd_f.close()
		if len(bdo_pd_l) != 0:
			bdo_pd = bdo_pd_l[0].strip('\n')
			if os.path.isdir(bdo_pd):
				start_dir = bdo_pd
			else:
				start_dir = '/import'
		else:
			start_dir = '/import'
	else:
		start_dir = '/import'
	
	Tk().withdraw()
	rpg_build_dir = tkf.askdirectory(title='Select RPG Build Directory',initialdir=start_dir)
	
	if rpg_build_dir != ():
		bdo_pd_l = [rpg_build_dir,'\n']
		bdo_pd_s = '\n'.join(bdo_pd_l)
		bdo_pd_f = open(script_dir+'/Build_Dir_Override_Prev_Dir.txt','w')
		bdo_pd_f.write(bdo_pd_s)
		bdo_pd_f.close()
		bdo_flag = 1

if bdo_flag == 0:
	if rpg_bn_krn_f == 32:
		rpg_build_dir = base_importBuilds_dir+ rpg_build_num
		rpg_archive_dir = base_importBuildsArchive_dir+ rpg_build_num
	elif rpg_bn_krn_f == 1864:
		rpg_build_dir = base_importBuilds_dir+ rpg_build_num+ '_rhel7'
		rpg_archive_dir = base_importBuildsArchive_dir+ rpg_build_num+ '_rhel7'
	elif rpg_bn_krn_f == 64:
		rpg_build_dir = base_importBuilds_dir+ rpg_build_num
		rpg_archive_dir = base_importBuildsArchive_dir+ rpg_build_num


# Check if the builds_cmlnxsvr location contains the needed build files, if not, use the archive_cmlnxsvr location instead, if possible.
rpg_obf_spec = 'linux'+ rpg_build_num+ '.tar.gz'
target_build_dir = ''
target_build_src_dir = ''

(flag_l) = rif.search_dir(rpg_build_dir,mand_importFiles_spec,rpg_obf_spec,srcCode_file_spec)
d_flag_1 = flag_l[0]
rpg_bf_check = flag_l[1]
rpg_obf_check = flag_l[2]
src_check = flag_l[3]

# Starting in mid-2017, the CM personnel elected to remove the source code .tar.gz file from the rhel5 
# build directories starting with RPG Build 18. Ergo, we must now do additional checks to ensure the source code for the newer builds can still 
# be copied to the given ORPG# account for rhel5 installations of Build 18 or later. 
if int(rpg_build_num) >= 18 and src_check == 0:
	rpg_build_src_dir = base_importBuilds_dir+ rpg_build_num+ '_rhel7'
	target_build_src_dir = rpg_build_src_dir
	
	(flag_l) = rif.search_dir(rpg_build_src_dir,mand_importFiles_spec,srcCode_file_spec)
	src_check = flag_l[2]

d_flag_2 = 1
if rpg_bf_check == 0 and rpg_obf_check == 0:
	(flag_l) = rif.search_dir(rpg_archive_dir,mand_importFiles_spec,rpg_obf_spec,srcCode_file_spec)
	d_flag_2 = flag_l[0]
	rpg_bf_check = flag_l[1]
	rpg_obf_check = flag_l[2]
	src_check = flag_l[3]
	
	# See the comment above...
	if int(rpg_build_num) >= 18 and src_check == 0:
		rpg_archive_src_dir = base_importBuildsArchive_dir+ rpg_build_num+ '_rhel7'
		target_build_src_dir = rpg_archive_src_dir
		
		(flag_l) = rif.search_dir(rpg_archive_src_dir,mand_importFiles_spec,srcCode_file_spec)
		src_check = flag_l[2]
			
	if rpg_bf_check == 1 or rpg_obf_check == 1:
		target_build_dir = rpg_archive_dir
else:
	target_build_dir = rpg_build_dir
	
if d_flag_1 == 0 and d_flag_2 == 0:
	print "\n"
	print "ERROR: Neither the RPG build directory: "+ rpg_build_dir+ " nor the RPG archive directory: "+ rpg_archive_dir+ " exist.\n"
	print "Program execution terminated!\n"
	sys.exit(error_code)

if not target_build_dir:	
	print "\n"
	print "ERROR: Neither the RPG build directory: "+ rpg_build_dir+ " nor the RPG archive directory: "+ rpg_archive_dir+ " contain the required files.\n"
	print "Program execution terminated!\n"
	sys.exit(error_code)

while srcComp_flag != '0' and srcComp_flag != '1':
	print "\n"
	print "ERROR: "+ str(srcComp_flag)+ " is not a valid value for the source code / compiler variable option.\n"
	print "The valid options are: 1 (for YES) or 0 (for NO)\n"
	srcComp_flag = raw_input("Enter a valid option for the source code / compiler variable option:\n")
	
srcComp_flag = int(srcComp_flag)

if srcComp_flag == 1:
	if src_check == 0 and rpg_bf_check == 1:
		print "\n"
		print "ERROR: The file "+ srcCode_file_spec+ " was not found in RPG build / archive directory: "+ target_build_dir+ "\n"
		print "Program execution terminated!\n"
		sys.exit(error_code)

rad_site = rad_site.upper()	
if rad_site != '0':
	while len(rad_site) != 4:
		print "\n"
		print "ERROR: "+ rad_site+ " is not a valid value for the radar site option.\n"
		print "The valid options are: xxxx (four letter radar site abbreviation, lower-case) or 0 (for no site)\n"
		rad_site = raw_input("Enter a valid value for the radar site option:\n")
		rad_site = rad_site.upper()
		if rad_site == '0':
			break
			
while mrpg_start_flag != '0' and mrpg_start_flag != '1':
	print "\n"
	print "ERROR: "+ str(mrpg_start_flag)+ " is not a valid value for the MRPG start option.\n"
	print "The valid options are: 1 (for YES) or 0 (for NO)\n"
	mrpg_start_flag = raw_input("Enter a valid option for the MRPG start option:\n")
	
mrpg_start_flag = int(mrpg_start_flag)

# Store the valid inputs for later use if needed.
qc_inputs = [rpg_build_num,build_dir_override,srcComp_flag,rad_site,mrpg_start_flag]
qc_inputs[:] = [str(i) for i in qc_inputs]

# Ensure all the needed .txt files are available in the script's directory.
if not os.path.isfile(script_dir+'/PATH_Ext.txt'):
	print "\n"
	print "ERROR: File: PATH_Ext.txt not found in the script's directory: "+ script_dir+ "\n"
	print "Program execution terminated!\n"
	sys.exit(error_code)
if not os.path.isfile(script_dir+'/Compiler_Env_Vars.txt'):
	print "\n"
	print "ERROR: File: Compiler_Env_Vars.txt not found in the script's directory: "+ script_dir+ "\n"
	print "Program execution terminated!\n"
	sys.exit(error_code)
if not os.path.isfile(script_dir+'/PDGUI_Env_Vars.txt'):
	print "\n"
	print "ERROR: File: PDGUI_Env_Vars.txt not found in the script's directory: "+ script_dir+ "\n"
	print "Program execution terminated!\n"
	sys.exit(error_code)
if not os.path.isfile(script_dir+'/GNTERM_Shortcut.txt'):
	print "\n"
	print "ERROR: File: GNTERM_Shortcut.txt not found in the script's directory: "+ script_dir+ "\n"
	print "Program execution terminated!\n"
	sys.exit(error_code)
if not os.path.isfile(script_dir+'/'+ qc_inputs_fname):
	print "\n"
	print "ERROR: File: "+ qc_inputs_fname+ " not found in the script's directory: "+ script_dir+ "\n"
	print "Program execution terminated!\n"
	sys.exit(error_code)
if not os.path.isfile(script_dir+'/'+ gedit_settings_fname):
	print "\n"
	print "ERROR: File: "+ gedit_settings_fname+ " not found in the script's directory: "+ script_dir+ "\n"
	print "Program execution terminated!\n"
	sys.exit(error_code)

# Note the current ORPG account and the selected RPG build directory.
print "\n"
print "The current ORPG account is: ORPG"+ str(orpg_num)+ "\n"
print "The selected RPG build directory for installation is: "+ target_build_dir+ "\n"


# Remove the current contents of the ORPG# directory, copy over the needed files from CM and install the RPG software.
print "Installing RPG Build "+ rpg_build_num+ " ...\n"

# If possible, retain the current ORPG account's gedit settings.
if rhel_v <= gedit_settings_maxRhelV:
	ges_f = open(script_dir+'/'+gedit_settings_fname, 'w')
	ges_f.close()
	os.system('gconftool-2 --dump /apps/gedit-2 > '+script_dir+'/'+gedit_settings_fname)

os.system('rm -rf '+ home_dir+ '/*')
os.system('rm -rf '+ home_dir+ '/.* 2>/dev/null')

if rpg_obf_check == 1:
	temp_install_dir = home_dir+ '/INSTALL_TEMP'
	temp_install_src_dir = home_dir +'/INSTALL_TEMP_SRC'
	os.system('mkdir '+ temp_install_dir)
	os.system('cp '+ target_build_dir+ '/'+ rpg_obf_spec+ ' '+ temp_install_dir+ '/.')
	os.system('tar -xzf '+ temp_install_dir+ '/'+ rpg_obf_spec+ ' -C '+ temp_install_dir)
		
	(flag_l) = rif.search_dir(temp_install_dir,mand_importFiles_spec,srcCode_file_spec)
	d_flag = flag_l[0]
	rpg_bf_check = flag_l[1]
	src_check = flag_l[2]
	
	if int(rpg_build_num) >= 18 and src_check == 0:
		os.system('mkdir '+ temp_install_src_dir)
		os.system('cp '+ target_build_src_dir+ '/'+ rpg_obf_spec+ ' '+ temp_install_src_dir+ '/.')
		os.system('tar -xzf '+ temp_install_src_dir+ '/'+ rpg_obf_spec+ ' -C '+ temp_install_src_dir)
		
		(flag_l) = rif.search_dir(temp_install_src_dir,mand_importFiles_spec,srcCode_file_spec)
		src_check = flag_l[2]
		
	if rpg_bf_check == 1:
		os.system('cp '+ temp_install_dir+ '/*.bz2 '+ home_dir+ '/.')
		os.system('cp '+ temp_install_dir+ '/install_rpg '+ home_dir+ '/.')
		if src_check == 1 and not target_build_src_dir:
			os.system('cp '+ temp_install_dir+ '/'+ srcCode_file_spec+ ' '+ home_dir+ '/.')
		elif src_check == 1 and target_build_src_dir:
			os.system('cp '+ temp_install_src_dir+ '/'+ srcCode_file_spec+ ' '+ home_dir+ '/.')
		exec_install = sp.Popen(home_dir+ '/install_rpg',stdin=sp.PIPE,stdout=sp.PIPE,stderr=sp.PIPE)
		exec_install.communicate('')
	else:
		print "\n"
		print "ERROR: The RPG build archive file: "+ rpg_obf_spec+ " from directory: "+ target_build_dir+ " does not contain the required files.\n"
		print "Program execution terminated!\n"
		sys.exit(error_code)
	
	# If needed, also extract the source code from the included .tar.gz file.
	if srcComp_flag == 1:
		if src_check == 0:
			print "\n"
			print "ERROR: The RPG build archive file: "+ rpg_obf_spec+ " from directory: "+ target_build_dir+ " does not contain the file: "+ srcCode_file_spec+ "\n"
			print "Program execution terminated!\n"
			sys.exit(error_code)
		
		os.system('tar -xzf '+ home_dir+ '/'+ srcCode_file_spec+ ' -C '+ home_dir)
		print "Source code successfully extracted from the file: "+ srcCode_file_spec+ "\n"
		
	os.system('rm -r '+ temp_install_dir)
	
	if os.path.isdir(temp_install_src_dir):
		os.system('rm -r '+ temp_install_src_dir)
	
else:	
	os.system('cp '+ target_build_dir+ '/*.bz2 '+ home_dir+ '/.')
	os.system('cp '+ target_build_dir+ '/install_rpg '+ home_dir+ '/.')
	if src_check == 1 and not target_build_src_dir:
		os.system('cp '+ target_build_dir+ '/'+ srcCode_file_spec+ ' '+ home_dir+ '/.')
	elif src_check == 1 and target_build_src_dir:
		os.system('cp '+ target_build_src_dir+ '/'+ srcCode_file_spec+ ' '+ home_dir+ '/.')
	exec_install = sp.Popen(home_dir+ '/install_rpg',stdin=sp.PIPE,stdout=sp.PIPE,stderr=sp.PIPE)
	exec_install.communicate('')
	
	# If needed, also extract the source code from the included .tar.gz file.
	if srcComp_flag == 1:
		os.system('tar -xzf '+ home_dir+ '/'+ srcCode_file_spec+ ' -C '+ home_dir)
		print "Source code successfully extracted from the file: "+ srcCode_file_spec+ "\n"

# Add auxiliary executables to the account's installation.
os.system('cp '+script_dir+'/copy_lb '+ home_dir+ '/bin/lnux_x86/.')
os.system('cp '+script_dir+'/live_lb '+ home_dir+ '/bin/lnux_x86/.')

print "RPG software installation successful.\n"


# Configure the environmental variables in the .bash_profile file accordingly.
#
print "Configuring environmental variables ...\n"

# Make a backup copy of the existing .bash_profile file.
os.system('cp '+ home_dir+ '/.bash_profile '+ home_dir+ '/bash_profile.orig')

# Get the existing data in the .bash_profile file.
bash_pf = open(home_dir+ '/.bash_profile','r')
bash_pd = bash_pf.readlines()
bash_pf.close()

# Make the mandatory changes to the environmental data.
#
# Configure the RMTPORT variable.
rmt_port_idx = bash_pd.index(rmt_port_lineSpec+'\n')
rmt_port_line = bash_pd[rmt_port_idx]
rmt_port_arr = rmt_port_line.split('=')
rmt_port_val_orig = rmt_port_arr[1]
rmt_port_val = str(long(rmt_port_val_orig) + (rmt_port_scale * orpg_num))
rmt_port_line = rmt_port_line.replace(rmt_port_val_orig,rmt_port_val)
bash_pd[rmt_port_idx] = rmt_port_line+'\n'

# Get the path extention line.
path_ext_f = open(script_dir+'/PATH_Ext.txt','r')
path_ext_d = path_ext_f.readlines()
path_ext_f.close()

# Add the path extention line to the environ. data.
path_ext_loc_idx = bash_pd.index(path_ext_locSpec+'\n') + 1
bash_pd.insert(path_ext_loc_idx,path_ext_d[0])

# Get the GNOME terminal shortcut line.
gt_shortcut_f = open(script_dir+'/GNTERM_Shortcut.txt','r')
gt_shortcut_d = gt_shortcut_f.readlines()
gt_shortcut_f.close()

# Add the GNOME terminal shortcut line to the environ. data.
gt_shortcut_loc_idx = bash_pd.index(gt_shortcut_lineSpec+'\n') + 1
bash_pd.insert(gt_shortcut_loc_idx,gt_shortcut_d[0])

# Get the PDGUI lines.
if int(rpg_build_num) not in pdg_excludes:
	pdg_ev_f = open(script_dir+'/PDGUI_Env_Vars.txt','r')
	pdg_ev_d = pdg_ev_f.read()
	pdg_ev_f.close()

	# Add the PDGUI lines to the environ. data.
	bash_pd.append(pdg_ev_d)

# If needed, also add the compiler flags to the environ. data.
if srcComp_flag == 1:
	# Get the compiler flag lines.
	comp_ev_f = open(script_dir+'/Compiler_Env_Vars.txt','r')
	comp_ev_d = comp_ev_f.read()
	comp_ev_f.close()
	
	# Add the compiler flag lines to the environ. data.
	comp_envVar_loc_idx = bash_pd.index(comp_envVar_lineSpec+'\n') + 1
	bash_pd.insert(comp_envVar_loc_idx,comp_ev_d)
	print "Compiler environmental variables successfully added.\n"

# Add the updated environ. data to the .bash_profile file.
bash_pd = ''.join(bash_pd)
bash_pf = open(home_dir+ '/.bash_profile','w')
bash_pf.write(bash_pd)
bash_pf.close()

# Make a backup copy of the newly modified .bash_profile file.
os.system('cp '+ home_dir+ '/.bash_profile '+ home_dir+ '/bash_profile.orpg'+ str(orpg_num)+ '.restore')

# Note that the environmental data was updated.
print "Environmental data successfully configured.\n"

# Note the current state of the home ORPG# directory.
cur_orpg_files = os.listdir(home_dir)
cur_orpg_files.sort()
print "The home directory: "+ home_dir+ " now contains the following items: \n\n"+ '\n'.join(cur_orpg_files)+ "\n"

# If needed, also copy over the most recent blockage and terrain data for the specified radar site.
if rad_site != '0':
	blockage_dir = base_bt_dir+ '/'+ blockage_dirSpec
	terrain_dir = base_bt_dir+ '/'+ terrain_dirSpec
	
	b_check = 0
	b_files = os.listdir(blockage_dir)
	b_files.sort()
	for b in b_files:
		if rad_site in b:
			b_check = 1
			break
	
	t_check = 0
	t_files = os.listdir(terrain_dir)
	t_files.sort()
	for t in t_files:
		if rad_site in t:
			t_check = 1
			break

	if b_check == 1:
		os.system('cp '+ blockage_dir+ '/'+ rad_site+ '_blockage.lb '+ home_dir+ '/cfg/bin/blockage.lb')
	else:
		print "No blockage data available in "+ blockage_dir+ " for site: "+ rad_site+ ".\n"
		
	if t_check == 1:
		os.system('cp '+ terrain_dir+ '/'+ rad_site+ '_terrain.lb '+ home_dir+ '/cfg/bin/terrain.lb')
	else:
		print "No terrain data available in "+ terrain_dir+ " for site: "+ rad_site+ ".\n"
	
	if b_check == 1 and t_check == 1:
		print "Blockage and terrain data copied to: "+ home_dir+ "/cfg/bin for site: "+ rad_site+ "\n"
				
# Get the RPG Build version number for the ORPG's currently installed software, if possible.
rpg_bv = ''
for c in cur_orpg_files:
	if build_v_spec in c:
		c_l = c.split('_')
		for b in c_l:
			if build_v_spec in b:
				rpg_bv = b
				break
		break

# Notify that the installation procedure is now complete.
if rpg_bv != '':
	print "RPG installation procedure for Build "+ rpg_build_num+ " ("+ rpg_bv+ ") on ORPG"+ str(orpg_num)+ " completed.\n"
else:
	print "RPG installation procedure for Build "+ rpg_build_num+ " on ORPG"+ str(orpg_num)+ " completed.\n"

# Store the quality controlled input parameters in a temporary .txt file to be used by the BASH wrapper program if needed.
qc_inputs.append('\n')
qci_s = '\n'.join(qc_inputs)
qci_f = open(script_dir+'/'+qc_inputs_fname,'w')
qci_f.write(qci_s)
qci_f.close()


if mrpg_start_flag == 1:
	sys.exit(start_code)
else:
	sys.exit(success_code)



