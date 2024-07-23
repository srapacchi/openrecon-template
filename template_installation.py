# intenend for python3

import logging
import os
import shutil
import sys
import subprocess
import re

# setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format=f"%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)
DEBUG_LINE = '#'*40

logger.debug(DEBUG_LINE)
logger.debug(DEBUG_LINE)
logger.info(f'Start of {os.path.basename(__file__)}')

# check if all system programs are here
logger.debug(DEBUG_LINE)
logger.info(f'Checking system dependencies...')

# git ?
path_git = shutil.which('git')
if path_git:
    logger.info('Git is installed')
else:
    logger.critical('Git does not seem to be present in the system')
    sys.exit(1)

# docker ?
path_docker = shutil.which('docker')
if path_docker:
    logger.info('Docker is installed')
else:
    logger.critical('Docker does not seem to be present in the system')
    sys.exit(1)

# docker version ok ?
result = subprocess.run(['docker', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
version_output = result.stdout.strip()
print(version_output)
pattern = r"Docker version (\d+\.\d+\.\d+),"
matches = re.findall(pattern, version_output)
if not len(matches):
    logger.critical('Could not find Docker version')
    sys.exit(1)
docker_version = matches[0].split('.')[0] # 20.21.22 -> 20
maximum_docker_version = 25
if int(docker_version) >= maximum_docker_version:
    logger.critical(f'Docker version {docker_version} is too high. Maximum is {maximum_docker_version}')
    sys.exit(1)
logger.info('Docker version is ok')

logger.info('... all depencies checked')
logger.debug(DEBUG_LINE)

# setup paths
cwd = os.getcwd()
logger.info(f'Current working directory : {cwd}')
path_PIS = os.path.join(cwd, 'python-ismrmrd-server')

# python-ismrmrd-server : this has the client / server fonctionality
PIS_git_adress = 'https://github.com/kspaceKelvin/python-ismrmrd-server'
PIS_name = 'python-ismrmrd-server'
if os.path.exists(path_PIS):
    logger.info(f'Found {PIS_name}, do not clone it again ')
else:
    logger.info(f'{PIS_name} not found, cloning it...')
    result = subprocess.run(['git', 'clone', PIS_git_adress])


logger.info('All done !')
sys.exit(0)
