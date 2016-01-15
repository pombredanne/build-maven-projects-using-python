#! python2

import os, shlex, ConfigParser, logging, sys, subprocess, time, re, pprint
import os.path as path
import xml.etree.ElementTree as ET
from datetime import datetime

base_dir = "C:\\"
software_dir = "software"
jdk_dir_name = "jdk1.7"
m2_dir_name = "maven\\m3"
sources_dir = "sources\\project1"
working_branch = "HEAD"

source_base_dir = path.join(base_dir, sources_dir, working_branch)

#Get Date in required format
now = datetime.now().strftime('%A.%d-%b-%Y.%H%MHrs')
try:
	file_name = __file__
except NameError, e:
	file_name = 'BuildMavenProjects.py'

#Script name
script_name = path.basename(file_name)
print "Script name is %s" % (script_name,)

log_file_name = file_name + ".log"

print "Log file name set as %s" % (log_file_name,)

#get Data from properties file
property_file = file_name + ".properties"
print 'Property File name is %s' % (property_file,)

#Setup Logging
LEVELS = {
	'debug': logging.DEBUG,
	'info': logging.INFO,
	'warning': logging.WARNING,
	'error': logging.ERROR,
	'critical': logging.CRITICAL,
}

if len(sys.argv) >= 2 and sys.argv[1] in LEVELS.keys():
	level_name = sys.argv[1]
else:
	level_name = 'info'


FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
level = LEVEL.get(level_name, logging.NOTSET)
logging.basicConfig(level=level, format=FORMAT, filename=log_file_name, filemode='w')
log = logging.getLogger(script_name)

def get_project_name(pom_dir):
	log.info("setting pom.xml path to %s", pom_path)
	if path.isfile(pom_path):
		tree = ET.parse(pom_path)
		root = tree.getroot()
		for artifactId in root.findall('{http://maven.apache.org/POM/4.0.0}artifactId'):
			log.debug("Project name retrieved as %s", artifactId.text)
			return artifactId.text


# Reading Properties file
try:
	configuration_section = 'Configuration'
	projects_list_section = 'Projects List'
	parser = ConfigParser.ConfigParser()
	parser.read(property_file)
	project_seperator = parser.get(configuration_section, 'project_names_list_seperator_char')
	maven_extra_arguments = parser.get(configuration_section, 'maven_extra_arguments')
	maven_lifecycle_arguments = parser.get(configuration_section, 'maven_lifecycle_arguments')
	maven_jvm_arguments = parser.get(configuration_section, 'maven_jvm_arguments')
	project_names = parser.get(projects_list_section, 'project_names')
except(ConfigParser.Error, IOError) as err:
	exception_info = "Cannot parse property file. Details are : " + str(err)
	log.error(exception_info)
	sys.exit(exception_info)

base_dir_exists = path.isdir(base_dir)
log.info('Base dir %s is available? %s', base_dir, str(base_dir_exists))

if base_dir_exists:

	try:
		JAVA_HOME = os.environ["JAVA_HOME"]
	except KeyError as ke:
		log.warn("JAVA_HOME is not set, checking if we can set it.")
		JAVA_HOME = os.path.join(base_dir, software_dir, jdk_dir_name)
		if path.isdir(JAVA_HOME):
			java_bin_dir = os.path.join(JAVA_HOME, 'bin')
			log.info("JAVA_HOME is being set as %s and updating systempath with %s", JAVA_HOME, java_bin_dir)
			os.environ['JAVA_HOME'] = JAVA_HOME
			os.environ['PATH'] = java_bin_dir + ';' + os.environ['PATH']

	try:
		M2_HOME = os.environ["M2_HOME"]
	except KeyError as ke:
		log.warn("M2_HOME is not set, checking if we can set it.")
		M2_HOME = os.path.join(base_dir, software_dir, m2_dir_name)
		if path.isdir(M2_HOME):
			m2_bin_dir = os.path.join(M2_HOME, 'bin')
			log.info("M2_HOME is being set as %s and updating systempath with %s", M2_HOME, m2_bin_dir)
			os.environ['M2_HOME'] = M2_HOME
			os.environ['PATH'] = m2_bin_dir + ';' + os.environ['PATH']

	if len(maven_jvm_arguments) > 0
		os.environ['MAVEN_OPTS'] = maven_jvm_arguments

	SRC_DIR = path.join(base_dir, working_branch, working_branch)

	if(path.isdir(JAVA_HOME) and path.isdir(M2_HOME) and path.isdir(SRC_DIR)):
		pom_dirs = set()
		pattern = re.compile(r".*\\target\\.*")
		for (dirpath,dirnames,filenames) in os.walk(SRC_DIR, topdown=False):
			if path.isdir(dirpath) and pattern.match(dirpath) == None
				for filename in filenames:
					if filename == 'pom.xml':
						log.info('adding pom.xml dir : %s', dirpath)
						pom_dirs.add(dirpath)
						break

		project_name_to_path = {}
		for pom_dir in pom_dirs:
			project_name_to_path[get_project_name(pom_dir)] = pom_dir
		
		log.debug('All pom dirs : %s ', pprint.pformat(pom_dirs))
		log.debug('project names to path mappings : %s', pprint.pformat(project_name_to_path))

		if len(project_seperator) > 1:
			log.info('Project seperator was set as %s which is of size %d when it should only be 1',project_seperator, len(project_seperator))
			project_seperator = ';'
		
		log.info('setting project_seperator is %s' , project_seperator)
		maven_projects_dir_in_run_order = []

		for project_name in project_names.split(project_seperator):
			clean_project_name = project_name.strip()
			pp = project_name_to_path.get(clean_project_name)
			log.info('Project Name %s, Project path %s', clean_project_name, pp)
			pp = path.relpath(pp, source_base_dir)
			log.info('Project Name %s, Project relative path %s', clean_project_name, pp)
			maven_projects_dir_in_run_order.append(pp)

		log.debug('Maven Projects dir(s) in run order are : %s', pprint.pformat(maven_projects_dir_in_run_order))
		maven_executable = path.join(M2_HOME,'bin','mvn.bat')
		maven_arguments = shlex.split(maven_extra_arguments)

		log.info('Maven executable is %s and extra arguments are %s', maven_executable, maven_arguments)
		invalid_parameters_with_args_list = ['--log-file', '--projects']
		invalid_parameters_list = ['clean', 'install']

		for parameter_arg in invalid_parameters_with_args_list:
			if parameter_arg in maven_arguments:
				removed = maven_arguments.pop(maven_arguments.index(parameter_arg))
				log.info('Removing unneeded parameter %s from arguments.', removed)

		projects_list = ','.join(maven_projects_dir_in_run_order)
		maven_arguments.extend(['--projects', projects_list])
		maven_arguments.extend(shlex.split(maven_lifecycle_arguments))

		log.info('final maven arguments are %s', maven_arguments)

		try:
			os.chdir(source_base_dir)
			pOpenParams = []
			pOpenParams.append(maven_executable)
			pOpenParams.extend(maven_arguments)

			log.debug('pOpen arguments are : %s', str(pOpenParams))

			process = subprocess.Popen(pOpenParams, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			output, error = subprocess.communicate()
			log.info(output)
			log.warn(error)

		except(IOError, OSError) as err:
			log.error("Error while running maven: %s", str(err))
	else:
		err_msg = 'Something is not right unable to setup the environment'
		log.error(err_msg)
		sys.exit(err_msg)
else:
	print("Base directory \ Drive unmapped : " + base_dir + ".... Exiting NOW!")


