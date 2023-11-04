# Copyright 2023 iwatake2222
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
"""
Function for additional information from CARET
"""
from __future__ import annotations
import yaml
from .caret2networkx import quote_name


def get_path_dict(filename: str) -> dict:
  """Get target path information"""
  path_dict = {}
  with open(filename, encoding='UTF-8') as file:
    yml = yaml.safe_load(file)
    path_info_list = yml['named_paths']
    for path_info in path_info_list:
      path_name = path_info['path_name']
      node_chain = path_info['node_chain']
      node_name_list = []
      for node in node_chain:
        node_name_list.append(quote_name(node['node_name']))
      path_dict[path_name] = node_name_list

  return path_dict
