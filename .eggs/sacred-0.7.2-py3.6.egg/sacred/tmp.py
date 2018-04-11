import os
from shutil import copy2
import json
from pkg_resources import parse_version

from run import Run
from utils import join_paths




def docker_dir(dir_name, _run, additional_files=(), additional_dependencies=(),
               required_packages=()):
    command = join_paths(_run.main_function.prefix,
                         _run.main_function.signature.name)
    dependencies = _run.experiment_info['dependencies']
    if additional_dependencies:
        dependencies += list(additional_dependencies)
    re_sources = {k: open(v, 'r')
                  for k, v in _run.experiment_info['sources'].items()}
    make_docker_dir(dir_name, dependencies, re_sources, _run.config,
                    _run.experiment_info['mainfile'], command,
                    get_truncated_python_version(_run.host_info),
                    additional_files, required_packages)
