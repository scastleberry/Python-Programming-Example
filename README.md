# Python-Programming-Example
# This repository contains an example Python script, small Python function library, and BASH wrapper script I created to facilitate the installation of a new radar software build on a Linux account.

##############################

# Please note that the main text below is from the README file that I created for the users at the ROC to use to know how to use this software; that is, it was developed and written originally for a specific audience. Due to the auxiliary files and paths needed, please don't try to actually run this code here (as it will not work), as it is being used here simply as a demonstation of some of the Python programming I have done in the past. 

# The overall flow of this software (in a nutshell) is as follows:
# 
# There are three core files involved: full_install_rpg (a wrapper BASH script - needed to source Linux environmental variables after the Python script completes), rpg_full_installation.py (the main Python script that does most of the work), and finally rpg_install_functions.py (is a small library of subroutines that are used one or more times throughout the main script).
#
# To begin, the user logs into the Linux account under which they want to install a new radar software build (called an RPG build), and uses the Linux command line throughout the process.
#
# The user, if needed, reads the text of this README file below to understand the files needed for this software to operate correctly, and its caveats. Additionally, running the main Python script (either alone or via the wrapper) with no input arguements from the command line will display help text describing to the user how to run the software correctly.
#
# Then, the script started from the command line via running the wrapper script full_install_rpg and supplying it with the specified options as the user dictates.
#
# The text below is the full README file that was supplied with this software. Please note that this file was designed to be used in a Linux text editor, or viewed in MS Word in Web Layout view.

Documentation for running the automated RPG build installation software on a Linux ORPG# account:

Description:
	After a user is logged in to an ORPG# account, and has verified that NONE of the files 
	on the current account are being used by anyone else and that there are NO active RPG
	playbacks in progress on the current ORPG# account, this script will clear the contents of the
	current ORPG# account, copy over the needed files from the specified RPG engineering release
	(Build) from the CM library, install the RPG software in the ORPG# account, and configure
	certain environmental variables. Certain optional steps can also be performed if needed.
	
Author:
	Stephen Castleberry (stephen.castleberry@noaa.gov) - ROC/CIMMS - 5/2015
	
Documentation/Software References:
	Steve Smith, Dave Zittel, Dan Berkowitz, Lindsey Richardson, Rich Murnan, Bob Lee
	
Files Required:
	Ensure the following files are ALL in the same directory (where you are running the installation program from):

	full_install_rpg		- A wrapper BASH script to run the main Python script, and then source the new environment and return to the home ORPG# 
					  directory upon a successful completion.
	rpg_full_installation.py	- The main Python program that performs the error checking and procedures for the RPG installation process.
	rpg_install_functions.py	- A library of various functions called by the main Python script in the RPG installation process.
	copy_lb				- An auxiliary script written by D. Zittel used to copy the file product_data_base.lb to another file.
	live_lb				- An auxiliary script written by D. Zittel used to start live radar data collection for the ORPG.
	PATH_Ext.txt			- A text file containing a line to add to the environ. variables profile to enable use of programs like CVT.
	PDGUI_Env_Vars.txt		- A text file containing lines to add to the environ. variables profile to enable use of OPUP and PDGUI.
	Compiler_Env_Vars.txt		- A text file containing lines to add to the environ. variables profile to enable compiling of new / updated RPG software modules.
	GNTERM_Shortcut.txt		- A text file containing a line to add to the environ. variables profile to enable a GNOME Terminal shortcut alias.
	qc_inputs.txt			- A text file containing the valid, quality controlled inputs to the .py script that is needed in the event of a successful execution
					  when using the BASH wrapper script execution method. This file MAY OR MAY NOT contain data, and in most cases will be changed each 
					  time the main .py script / BASH script is/are executed. DO NOT ATTEMPT TO CHANGE OR MODIFY THIS FILE!
	gedit_settings.txt		- A text file containing the current ORPG account's gedit configuration settings / preferences. This file MAY OR MAY NOT contain data, 
					  and in some cases will be changed each time the main .py script is executed. DO NOT ATTEMPT TO CHANGE OR MODIFY THIS FILE!
	Build_Dir_Override_Prev_Dir.txt	- A text file containing the previously manually selected RPG build directory path in the case of the user electing to overrride the 
					  automatic selection of the RPG Build directory location. The next time the user runs the software with the manual override option, 
					  the software will attempt to use the path specified in this file as the starting selection location path. This file MAY OR MAY NOT exist, 
					  and MAY OR MAY NOT contain data, and in some cases will be changed when the main .py script / BASH script is/are executed. DO NOT ATTEMPT 
					  TO CHANGE OR MODIFY THIS FILE!
	
Execution Methods (Executed from the directory containing all the aforementioned files, and when logged in to an ORPG# account.):

	Using the external BASH wrapper script (PREFERRED METHOD, from any directory):	. inrpg Build# Build_Dir_Override SrcComp_Flag Rad_Site MRPG_Start_Flag
	
	Using the BASH wrapper script (PREFERRED METHOD, from this script's directory):	. full_install_rpg Build# Build_Dir_Override SrcComp_Flag Rad_Site MRPG_Start_Flag
	
	Using the Python script directly:						./rpg_full_installation.py Build# Build_Dir_Override SrcComp_Flag Rad_Site MRPG_Start_Flag
	
		In this method, provided the program executes successfully, you will need to manually change back to the home ORPG# directory, source the updated 
		environ. variables (usually the .bash_profile), and if needed, start the RPG software.
		
	* In both methods, omitting the five (5) input arguments (Build#, Build_Dir_Override, SrcComp_Flag, Rad_Site, and MRPG_Start_Flag) will display explanatory 
	  usage text for running the software.
	* If using the BASH file method, if the program doesn't fail, the new environ. data will be sourced and the user will be returned to the home ORPG# directory 
	  upon completion. Also, if a valid radar site is specified and/or the MRPG start option is selected, the radar site is changed and/or the RPG software is started. 
	* NOTE: This script may not function at certain times of the day for certain builds (when the nightly builds are being compiled). In this case, wait until the 
	  nightly build cycle is complete before attempting to install the software, or try using a different build number.
  	* In order to use the inrpg shortcut script from any directory, ensure it is soft-linked in your personal bin directory by first entering: 
  	  ln -s /import/apps/scastleberry/Scripts/CSH/inrpg ~/bin/. from the command line and ensure your ~/bin directory is appended to the current ORPG# account's PATH variable.
	  
Input Parameters:

	Build#			- The engineering RPG software build version to be installed
			  	  Valid Options: 14, 15, 16, 17, 18
			  
	Build_Dir_Override	- Option to allow the user to manually select the directory from which to install the RPG software, instead of it being automatically 
				  selected based on the Build# parameter.
				  Valid Options: 1 (for YES), 0 (for NO)
			  
	SrcComp_Flag		- Option to extract the build's source code from the included file: orpg_src.tar.gz, and configure compiler environmental variables
			  	  Valid Options: 1 (for YES), 0 (for NO)
			  
	Rad_Site		- Option to copy over the specified site's blockage and terrain data (.lb files) from import to the ORPG# account and update the site adaptation data
			  	  Valid Options: xxxx (four letter radar site abbreviation, lower-case), 0 (for no site)
			  
  	MRPG_Start_Flag 	- Option to automatically start the MRPG software, provided the BASH wrapper script execution method is used
  			  	  Valid Options: 1 (for YES), 0 (for NO)
		
