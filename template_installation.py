# intenend for python3

# external modules
import jsonschema

# builtin modules
import logging
import os
import shutil
import sys
import subprocess
import re
import base64
import json


def print_section(name: str) -> None:
    DEBUG_LINE = '#'*40
    print('')
    print(DEBUG_LINE)
    print(f'# {name}')
    print(DEBUG_LINE)


def check_git() -> None:
    logger = logging.getLogger()

    # git ?
    path_git = shutil.which('git')
    if path_git:
        logger.info('Git is installed')
    else:
        logger.critical('Git does not seem to be present in the system')
        sys.exit(1)


def check_docker() -> None:
    logger = logging.getLogger()

    # docker ?
    path_docker = shutil.which('docker')
    if path_docker:
        logger.info('Docker is installed')
    else:
        logger.critical('Docker does not seem to be present in the system')
        sys.exit(1)

    # docker version ok ?
    result = subprocess.run(['docker', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    version_output = result.stdout.strip()
    logger.debug(version_output)
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
    logger.info(f'Docker version {docker_version}<{maximum_docker_version} is ok')


def clone_server(repo_path: str) -> None:
    logger = logging.getLogger()

    # python-ismrmrd-server : this has the client / server fonctionality
    print_section('CHECK or CLONE `python-ismrmrd-server`')
    git_adress = 'https://github.com/kspaceKelvin/python-ismrmrd-server'
    if os.path.exists(repo_path):
        logger.info(f'Found `python-ismrmrd-server` dir, do not clone it again : {repo_path}')
    else:
        logger.info('`python-ismrmrd-server` not found, cloning it...')
        subprocess.run(['git', 'clone', git_adress], check=True)


def build_server(repo_dockerfile_path: str) -> None:
        logger = logging.getLogger()

        result = subprocess.run(['docker', 'images', 'python-ismrmrd-server'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        output = result.stdout.strip()
        if 'python-ismrmrd-server' in output:
            logger.info('docker image `python-ismrmrd-server` already built')
            return

        # build docker image for python-ismrmrd-server
        # this image is the starting point, that will be refined latter
        logger.info('building docker image `python-ismrmrd-server`')
        subprocess.run(['docker', 'build', '--tag', 'python-ismrmrd-server', '--file', repo_dockerfile_path, './'], check=True)


def check_from_siemens(from_siemens_dir: str) -> None:
    logger = logging.getLogger()
    
    json_name = 'OpenReconSchema_1.1.0.json'
    path_json = os.path.join(from_siemens_dir, json_name)

    if os.path.exists(from_siemens_dir):
        logger.info(f'`from_siemens` dir found : {from_siemens_dir}')
    else:
        os.mkdir(from_siemens_dir)
        logger.critical(f'`from_siemens` dir created : you need to add inside the {json_name} file')
        sys.exit(1)

    if os.path.exists(path_json):
        logger.info(f'`{json_name}` found : {path_json}')
    else:
        logger.critical(f'`{json_name}` NOT found : please get form Siemens (magnetom.net) and copy in the dir `{from_siemens_dir}`')


def main():

    # setup logging
    logging.basicConfig(
        level=logging.DEBUG,
        format=f"%(levelname)8s:%(funcName)15s: %(message)s",
    )
    logger = logging.getLogger()

    print_section('START')
    logger.info(f'Start of {os.path.basename(__file__)}')

    # check if all system programs are here
    print_section('SYSTEM DEPENDENCIES')
    check_git()
    check_docker()

    # python-ismrmrd-server : clone & build docker image
    print_section('CLONE & BUILD SERVER')
    cwd = os.getcwd()
    logger.info(f'Current working directory : {cwd}')
    repo_path            = os.path.join(cwd, 'python-ismrmrd-server')
    repo_dockerfile_path = os.path.join(repo_path, 'docker', 'Dockerfile')
    clone_server(repo_path)
    build_server(repo_dockerfile_path)

    # from_siemens
    print_section('`from_siemens` dir and its content')
    from_siemens_dir = os.path.join(cwd, 'from_siemens')
    check_from_siemens(from_siemens_dir)

    # END
    print_section('All done !')
    sys.exit(0)


if __name__ == '__main__':
    main()
