#
# K2HR3 OpenStack Notification Listener
#
# Copyright 2018 Yahoo Japan Corporation
#
# K2HR3 is K2hdkc based Resource and Roles and policy Rules, gathers
# common management information for the cloud.
# K2HR3 can dynamically manage information as "who", "what", "operate".
# These are stored as roles, resources, policies in K2hdkc, and the
# client system can dynamically read and modify these information.
#
# For the full copyright and license information, please view
# the license file that was distributed with this source code.
#
# AUTHOR:   Hirotaka Wakabayashi
# CREATE:   Tue Sep 11 2018
# REVISION:
#
#

#===============================================================
# Configuration for python_helper.sh
#===============================================================
# This file is loaded into the python_helper.sh script.
# The python_helper.sh script is a Github Actions helper script that
# builds and packages the target repository.
# This file is mainly created to define variables that differ depending
# on the Python Version.
# It also contains different information(such as packages to install)
# for each repository.
#
# In the initial state, you need to set the following variables:
#   INSTALL_PKG_LIST  : A list of packages to be installed for build and
#                       packaging
#   INSTALLER_BIN     : Package management command
#   INSTALL_QUIET_ARG : Output suppression parameters during installation
#   IS_PUBLISHER      : Set to 1 when publishing a package.
#                       Set this value to only one of the target python
#                       versions.
#
# Set these variables according to the CI_PYTHON_VERSION variable.
# The value of the CI_PYTHON_VERSION variable matches the name of
# the Container used in Github Actions.
# Check the ".github/workflow/***.yml" file for the value.
#

#---------------------------------------------------------------
# Default values
#---------------------------------------------------------------
INSTALL_PKG_LIST=""
INSTALLER_BIN=""
INSTALL_QUIET_ARG=""

IS_PUBLISHER=0

#---------------------------------------------------------------
# Variables for each Python Version
#---------------------------------------------------------------
if [ -z "${CI_PYTHON_VERSION}" ]; then
	#
	# Unknown Python version : Nothing to do
	#
	:
elif [ "${CI_PYTHON_VERSION}" = "3.9" ]; then
	INSTALL_PKG_LIST="git"
	INSTALLER_BIN="apt-get"
	INSTALL_QUIET_ARG="-qq"
	# NOTE:
	# The value of FORCE_PUBLISHER environment MUST be same as CI_PYTHON_VERSION variable.
	IS_PUBLISHER=1

elif [ "${CI_PYTHON_VERSION}" = "3.10" ]; then
	INSTALL_PKG_LIST="git"
	INSTALLER_BIN="apt-get"
	INSTALL_QUIET_ARG="-qq"
	IS_PUBLISHER=0

elif [ "${CI_PYTHON_VERSION}" = "3.11" ]; then
	INSTALL_PKG_LIST="git"
	INSTALLER_BIN="apt-get"
	INSTALL_QUIET_ARG="-qq"
	IS_PUBLISHER=0
fi

#---------------------------------------------------------------
# Enable/Disable processing
#---------------------------------------------------------------
# [NOTE]
# Specify the phase of processing to use.
# The phases that can be specified are the following values, and
# the default is set for Python processing.
# Setting this value to 1 enables the corresponding processing,
# setting it to 0 disables it.
#
#	<variable name>		<default value>
#	RUN_PRE_INSTALL			0
#	RUN_INSTALL				1
#	RUN_POST_INSTALL		0
#	RUN_PRE_AUDIT			0
#	RUN_AUDIT				1
#	RUN_POST_AUDIT			0
#	RUN_CPPCHECK			1
#	RUN_SHELLCHECK			1
#	RUN_CHECK_OTHER			0
#	RUN_PRE_BUILD			0
#	RUN_BUILD				1
#	RUN_POST_BUILD			0
#	RUN_PRE_TEST			0
#	RUN_TEST				1
#	RUN_POST_TEST			0
#	RUN_PRE_PUBLISH			1
#	RUN_PUBLISH				1
#	RUN_POST_PUBLISH		0
#
RUN_CPPCHECK=0
RUN_POST_PUBLISH=0

#---------------------------------------------------------------
# Variables for each process
#---------------------------------------------------------------
# [NOTE]
# Specify the following variables that can be specified in some
# processes.
# Each value has a default value for Python processing.
#
#	CPPCHECK_TARGET					"."
#	CPPCHECK_BASE_OPT				"--quiet --error-exitcode=1 --inline-suppr -j 4 --std=c++03 --xml"
#	CPPCHECK_ENABLE_VALUES			"warning style information missingInclude"
#	CPPCHECK_IGNORE_VALUES			"unmatchedSuppression"
#	CPPCHECK_BUILD_DIR				"/tmp/cppcheck"
#
#	SHELLCHECK_TARGET_DIRS			"."
#	SHELLCHECK_BASE_OPT				"--shell=sh"
#	SHELLCHECK_EXCEPT_PATHS			"/node_modules/ /build/ /src/build/"
#	SHELLCHECK_IGN					"SC1117 SC1090 SC1091"
#	SHELLCHECK_INCLUDE_IGN			"SC2034 SC2148"
#
SHELLCHECK_EXCEPT_PATHS="/k2hr3_osnl/"

#---------------------------------------------------------------
# Override function for processing
#---------------------------------------------------------------
#
# [NOTE]
# It is allowed to override the contents of each processing.
# Each processing is implemented by a function that can be
# overridden. Those default functions are implemented for Python
# processing.
# If you want to change the processing, you can implement and
# override the following functions in this file. Those function
# should return 0 or 1 as a return value.
# For messages such as errors, you can use PRNERR, PRNWARN, PRNMSG,
# and PRNINFO defined in python_helper.sh.
#
#	<function name>		<which processing>			<implemented or not>
#	run_pre_install		: before installing npm packages	yes
#	run_install			: installing npm packages			yes
#	run_post_install	: after installing npm packages		no
#	run_pre_audit		: before audit checking				no
#	run_audit			: audit checking					yes
#	run_post_audit		: after audit checking				no
#	run_cppcheck		: run cppcheck						yes
#	run_shellcheck		: run shellcheck					yes
#	run_othercheck		: run other checking				no
#	run_pre_build		: before building					no
#	run_build			: building							yes
#	run_post_build		: after building					no
#	run_pre_test		: before testing					no
#	run_test			: testing							yes
#	run_post_test		: after testing						no
#	run_pre_publish		: before publishing package			yes
#	run_publish			: publishing package				yes
#	run_post_publish	: after publishing package			no
#

run_post_publish()
{
	return 0
}

#
# Local variables:
# tab-width: 4
# c-basic-offset: 4
# End:
# vim600: noexpandtab sw=4 ts=4 fdm=marker
# vim<600: noexpandtab sw=4 ts=4
#
