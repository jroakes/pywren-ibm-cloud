#
# Copyright 2018 PyWren Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys
from pywren_ibm_cloud.serialize import default_preinstalls


def get_runtime_preinstalls(storage_handler, runtime):
    """
    Download runtime information from storage at deserialize
    """
    if runtime in default_preinstalls.modules:
        runtime_meta = default_preinstalls.modules[runtime]
        preinstalls = runtime_meta['preinstalls']
    else:
        runtime_meta = storage_handler.get_runtime_info(runtime)
        preinstalls = runtime_meta['preinstalls']

    if not runtime_valid(runtime_meta):
        raise Exception(("The indicated runtime: {} "
                         + "is not approprite for this python version.")
                        .format(runtime))

    return preinstalls

def version_str(version_info):
    return "{}.{}".format(version_info[0], version_info[1])


def runtime_valid(runtime_meta):
    """
    Basic checks
    """
    this_version_str = version_str(sys.version_info)
    return this_version_str == runtime_meta['python_ver']
