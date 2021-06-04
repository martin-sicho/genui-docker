"""
get_tags

Created by: Martin Sicho
On: 27.01.21, 9:31
"""

import os, hashlib, datetime
DOCKER_REPO_PREFIX = 'sichom' if not 'GENUI_DOCKER_IMAGE_PREFIX' in os.environ else os.environ['GENUI_DOCKER_IMAGE_PREFIX']
IMAGES = ('genui-base', 'genui-base-cuda', 'genui-main', 'genui-worker', 'genui-gpuworker')
NVIDIA_CUDA_VERSION = '' if not 'NVIDIA_CUDA_VERSION' in os.environ else os.environ['NVIDIA_CUDA_VERSION']

def main(args):
    # get backend version
    import importlib.util
    spec = importlib.util.spec_from_file_location("about", "./src/genui/src/genui/about.py")
    about = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(about)
    backend_version = about.get_release_info()['version_full']

    # get the frontend version
    import json
    frontend_version = None
    with open('./src/genui-gui/package.json', "rb") as package:
        frontend_version = json.load(package)['version']
    assert frontend_version

    # create snapshot ID
    snapshot_id = hashlib.sha256(datetime.datetime.now().strftime('%Y%m%d%H%M%S%f').encode()).hexdigest()[1:8]

    # generate docker tag commands
    source_tag = args[1]
    target_tags = args[2].split(',')
    if source_tag == 'latest':
        target_tags = target_tags + [backend_version]
    commands = []
    push_commands = []
    for image in IMAGES:
        push_commands.append(f'docker image push --all-tags {DOCKER_REPO_PREFIX}/{image}')
        for target_tag in target_tags:
            command = f'docker tag {DOCKER_REPO_PREFIX}/{image}:{source_tag} {DOCKER_REPO_PREFIX}/{image}:{target_tag}'
            commands.append(command)
            if target_tag == 'dev':
                snapshot_command = f'docker tag {DOCKER_REPO_PREFIX}/{image}:{source_tag} {DOCKER_REPO_PREFIX}/{image}:snapshot-{snapshot_id}'
                commands.append(snapshot_command)
                with open('BUILD.TXT', 'w', encoding='utf-8') as build_file:
                    build_file.write(snapshot_id)
            if source_tag == 'latest' and image == 'genui-main':
                commands.append(f'docker tag {DOCKER_REPO_PREFIX}/{image}:{source_tag} {DOCKER_REPO_PREFIX}/{image}:frontend-{frontend_version}')
            if NVIDIA_CUDA_VERSION and (image == 'genui-base-cuda' or image == 'genui-gpuworker'):
                commands.append(f'docker tag {DOCKER_REPO_PREFIX}/{image}:{source_tag} {DOCKER_REPO_PREFIX}/{image}:cuda-{NVIDIA_CUDA_VERSION}')
    print('\n'.join(commands + push_commands) + '\n')
if __name__ == "__main__":
    import sys
    main(sys.argv)

