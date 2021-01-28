"""
get_tags

Created by: Martin Sicho
On: 27.01.21, 9:31
"""

import os
DOCKER_REPO_PREFIX = 'sichom' if not 'GENUI_DOCKER_IMAGE_PREFIX' in os.environ else os.environ['GENUI_DOCKER_IMAGE_PREFIX']
IMAGES = ('genui-base', 'genui-main', 'genui-worker', 'genui-gpuworker')

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

    # generate docker tag commands
    source_tag = args[1]
    target_tags = args[2].split(',')
    target_tags = target_tags + [backend_version]
    commands = []
    push_commands = []
    for image in IMAGES:
        push_commands.append(f'docker image push --all-tags {DOCKER_REPO_PREFIX}/{image}')
        for target_tag in target_tags:
            command = f'docker tag {DOCKER_REPO_PREFIX}/{image}:{source_tag} {DOCKER_REPO_PREFIX}/{image}:{target_tag}'
            commands.append(command)
            if image == 'genui-main':
                commands.append(f'docker tag {DOCKER_REPO_PREFIX}/{image}:{source_tag} {DOCKER_REPO_PREFIX}/{image}:frontend-{frontend_version}')
    print('\n'.join(commands + push_commands) + '\n')
if __name__ == "__main__":
    import sys
    main(sys.argv)

