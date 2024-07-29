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
import datetime
import json
import base64


def print_section(name: str) -> None:
    DEBUG_LINE = '#'*40
    print('')
    print(DEBUG_LINE)
    print(f'# {name}')
    print(DEBUG_LINE)


def check_zip() -> None:
    logger = logging.getLogger()

    # zip ?
    path_git = shutil.which('zip')
    if path_git:
        logger.info('`zip` is installed')
    else:
        logger.critical('`zip` does not seem to be present in the system')
        sys.exit(1)


def check_git() -> None:
    logger = logging.getLogger()

    # git ?
    path_git = shutil.which('git')
    if path_git:
        logger.info('`git` is installed')
    else:
        logger.critical('`git` does not seem to be present in the system')
        sys.exit(1)


def check_docker() -> None:
    logger = logging.getLogger()

    # docker ?
    path_docker = shutil.which('docker')
    if path_docker:
        logger.info('`docker` is installed')
    else:
        logger.critical('`Docker` does not seem to be present in the system')
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

    # python-ismrmrd-server : this has the client / server functionality
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
    
    file_names = [
        'OpenReconSchema_1.1.0.json',
        'i2i.py',
        'i2i_json_ui.json',
    ]

    if os.path.exists(from_siemens_dir):
        logger.info(f'`from_siemens` dir found : {from_siemens_dir}')
    else:
        os.mkdir(from_siemens_dir)
        logger.critical(f'`from_siemens` dir created : you need to add inside 3 files : {", ".join(file_names)}, ')
        sys.exit(1)

    for file in file_names:
        pth = os.path.join(from_siemens_dir, file)
        if os.path.exists(pth):
            logger.info(f'`{file}` found : {pth}')
        else:
            logger.critical(f'`{file}` NOT found : please get form Siemens (magnetom.net) and copy in the dir `{from_siemens_dir}`')


def create_pdf(file_path: str, lines_of_text: list[str]) -> None:
    pdf_header = b'%PDF-1.4\n'
    
    objects = []
    objects.append(b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n') # Object 1: Catalog
    objects.append(b'2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n') # Object 2: Pages
    objects.append(b'3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n') # Object 3: Page
    
    # Object 4: Page content
    content_stream = "BT /F1 24 Tf 100 750 Td" 
    for line in lines_of_text:
        content_stream += f" ({line}) Tj 0 -30 Td"
    content_stream += " ET"
    objects.append(f'4 0 obj\n<< /Length {len(content_stream)} >>\nstream\n{content_stream}\nendstream\nendobj\n'.encode())
    objects.append(b'5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n') # Object 5: Font
    
    pdf_body = b''.join(objects)
    
    # Cross-reference table
    xref_offset = len(pdf_header)
    xref = b'xref\n0 6\n0000000000 65535 f \n'
    xref_entry_offsets = [xref_offset]
    for obj in objects:
        xref_entry_offsets.append(xref_entry_offsets[-1] + len(obj))
    for offset in xref_entry_offsets:
        xref += f'{offset:010} 00000 n \n'.encode()
    
    trailer = f'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref_entry_offsets[-1]}\n%%EOF'.encode()
    
    # Write
    with open(file_path, 'wb') as f:
        f.write(pdf_header)
        f.write(pdf_body)
        f.write(xref)
        f.write(trailer)


def main():

    #############
    ### setup ###
    #############

    # setup logging
    logging.basicConfig(
        level=logging.DEBUG,
        format=f"%(levelname)8s:%(funcName)15s: %(message)s",
    )
    logger = logging.getLogger()

    print_section('START')
    logger.info(f'Start of {os.path.basename(__file__)}')
    logger.warning('Untill the BUILD part, there is a "skip if already done" feature')

    # check if all system programs are here
    print_section('SYSTEM DEPENDENCIES')
    check_zip()
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

    #############
    ### build ###
    #############

    print_section('BUILD')
    logger.warning('From now on, all steps will not have a "skip if already done" feature')

    # prep build dir
    build_path = os.path.join(cwd, 'build')
    if os.path.exists(build_path):
        logger.info(f'`build` dir found : {build_path}')
    else:
        os.mkdir(build_path)
        logger.info(f'`build` dir created : {build_path}')

    # prep some paths
    siemens_schema_json_path = os.path.join(from_siemens_dir, 'OpenReconSchema_1.1.0.json'   )
    siemens_ui_json_path     = os.path.join(from_siemens_dir, 'i2i_json_ui.json'             )
    siemens_py_path          = os.path.join(from_siemens_dir, 'i2i.py'                       )
    build_ui_json_path       = os.path.join(build_path      , 'i2i_json_ui.json'             )
    build_py_path            = os.path.join(build_path      , 'i2i.py'                       )
    build_pdf_path           = os.path.join(build_path      , 'i2i.pdf'                      )

    # get SDK JSON content and modify it for this demo
    logger.info(f'load UI JSON content : {siemens_ui_json_path}')
    with open(siemens_ui_json_path, 'r') as fid:
        json_content = json.load(fid)

    # prep info
    cmdline  = 'CMD [ "python3", "/opt/code/python-ismrmrd-server/main.py", "-v", "-H=0.0.0.0", "-p=9002", "-l=/tmp/python-ismrmrd-server.log", "--defaultConfig=i2i"]'
    version                         = '1.2.3' # major.minor.patch
    vendor                          = 'openrecon-template'
    name                            = 'i2i-openrecon-template'
    manufacturer_address            = 'AdressOf openrecon-template'
    mad_in                          = 'TheInternet'
    gtin                            = 'myGTIN'
    udi                             = 'myUDI'
    safety_advices                  = ''
    special_operating_instructions  = ''
    additional_relevant_information = ''

    # other file/path
    dockerfile_basename = f'OpenRecon_{vendor}_{name}:V{version}'.lower()
    zip_basename        = f'OpenRecon_{vendor}_{name}_V{version}'
    build_docker_path   = os.path.join(build_path, f'{zip_basename}.Dockerfile')
    build_zip_path      = os.path.join(build_path, f'{zip_basename}.zip')

    # update content
    json_content['general']['name'       ]['en'] = name
    json_content['general']['version'    ]       = version
    json_content['general']['vendor'     ]       = vendor
    json_content['general']['information']['en'] = name + '_' + version
    json_content['general']['id'         ]       = name
    json_content['general']['regulatory_information']['device_trade_name'              ] = name
    json_content['general']['regulatory_information']['production_identifier'          ] = name + '_' + version
    json_content['general']['regulatory_information']['manufacturer_address'           ] = manufacturer_address
    json_content['general']['regulatory_information']['made_in'                        ] = mad_in
    json_content['general']['regulatory_information']['manufacture_date'               ] = datetime.datetime.today().strftime('%Y-%m-%d_%Hh%Mm%S')
    json_content['general']['regulatory_information']['material_number'                ] = name + '_' + version
    json_content['general']['regulatory_information']['gtin'                           ] = gtin
    json_content['general']['regulatory_information']['udi'                            ] = udi
    json_content['general']['regulatory_information']['safety_advices'                 ] = safety_advices
    json_content['general']['regulatory_information']['special_operating_instructions' ] = special_operating_instructions
    json_content['general']['regulatory_information']['additional_relevant_information'] = additional_relevant_information
    # for more info, check `OpenReconJsonConfig.pdf`

    # load JSON Schema, to check if our updated JSON is ok
    logger.info(f'load JSON Schema : {siemens_schema_json_path}')
    with open(file=siemens_schema_json_path, mode='r') as fid:
        schema_content = json.load(fp=fid)
    validator = jsonschema.Draft7Validator(schema=schema_content)
    errors = list(validator.iter_errors(instance=json_content))
    if errors:
        logger.error('our Json vs. Schema errors :')
        for error in errors:
                logger.error(error)
        sys.exit(1)
    logger.info(f'No error in out JSON compared against the Schema')

    # write the updated json in the `build` dir
    logger.info(f'write update UI JSON content : {build_ui_json_path}')
    with open(file=build_ui_json_path, mode='w') as fid:
        json.dump(obj=json_content, fp=fid, indent=4)
    encoded_json_content = base64.b64encode((json.dumps(obj=json_content,indent=2)).encode('utf-8')).decode('utf-8')

    # copy the python module MRD `client` to execute
    logger.info(f'copy : SRC={siemens_py_path} DST={build_py_path}')
    shutil.copy(src=siemens_py_path,dst=build_py_path)
    logger.info(f'the `build` .py file will be latter added in the Docker image : {build_py_path}')

    # write the Dockerfile content
    logger.info(f'Write `build` Dockerfile : {build_docker_path}')
    with open(file=build_docker_path, mode='w') as fid:
        
        fid.writelines([
            '# import python-ismrmrd-server as starting point \n',
            f'FROM python-ismrmrd-server \n',
            '\n'])
        
        fid.writelines([
            '# mandatory for OpenRecon (see OR documentation) \n',
            f'LABEL "com.siemens-healthineers.magneticresonance.openrecon.metadata:1.1.0"="{encoded_json_content}" \n',
            '\n'])
        
        fid.writelines([
            '# copy the .py module \n',
            f'COPY {os.path.relpath(build_py_path, cwd)}  /opt/code/python-ismrmrd-server \n',
            '\n'])
        
        
        fid.writelines([
            '# new CMD line \n',
            f'{cmdline} \n',
            '\n'])
        
    # build Docker image
    # result = subprocess.run(['docker', 'images', name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    # output = result.stdout.strip()
    # if name in output:
    #     logger.info(f'docker image `{name}` already built')
    # else:
    logger.info(f'building docker image `{dockerfile_basename}` from Docker file {build_docker_path}')
    subprocess.run(['docker', 'build', '--tag', dockerfile_basename, '--file', build_docker_path, cwd], check=True)

    # save docker image in a .tar
    build_tar_path = os.path.join(build_path, f'{zip_basename}.tar')
    logger.info(f'(1/2) saving image `{dockerfile_basename}` in a .tar {build_tar_path}')
    subprocess.run(['docker', 'save', '-o', build_tar_path, dockerfile_basename], check=True)
    logger.info(f'(2/2) saving image DONE')

    # generate PDF
    lines = [
        f'vendor={vendor}',
        f'name={name}',
        f'version={version}',
    ]
    build_pdf_path = os.path.join(build_path, f'{zip_basename}.pdf')
    logger.info(f'write PDF file : {build_pdf_path}')
    create_pdf(file_path=build_pdf_path, lines_of_text=lines)

    # save everything in a ZIP file
    logger.info(f'(1/2) zip all files : {build_zip_path}')
    subprocess.run(['zip', zip_basename+'.zip', zip_basename+'.tar', zip_basename+'.pdf'], check=True, cwd=build_path)
    logger.info(f'(1/2) zip all files DONE')

    # END
    print_section('All done !')
    sys.exit(0)


if __name__ == '__main__':
    main()
