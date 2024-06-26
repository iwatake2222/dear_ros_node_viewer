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
import random
import networkx as nx
import yaml
from .caret2networkx import quote_name
from .logger_factory import LoggerFactory

logger = LoggerFactory.create(__name__)


def create_dict_cbgroup2executor(yml: yaml) -> tuple[dict, dict]:
  """Create dictionary of CallbackGroupName->Executor, CallbackGroupName->Color"""
  dict_cbgroup2executor = {}
  dict_cbgroup2color = {}
  executors = yml['executors']
  for executor in executors:
    executor_name = executor['executor_name']
    executor_type = executor['executor_type']
    callback_group_names = executor['callback_group_names']
    color = [255, 255, 255]
    if len(callback_group_names) > 1:
      color = [random.randint(96, 255), random.randint(96, 255), random.randint(0, 128)]
    for callback_group_name in callback_group_names:
      dict_cbgroup2executor[callback_group_name] = executor_name + ', ' + executor_type[:6]
      dict_cbgroup2color[callback_group_name] = color
  return dict_cbgroup2executor, dict_cbgroup2color


def create_callback_detail(callbacks: list[dict], callback_name: str) -> dict:
  """
  Create detail information of callback

  Note
  ---
  example:
  {
    "callback_name": "callback_name",
    "callback_type": "subscription_callback",
    "description": "/topic_sub3pub1"
  }
  """
  callback_detail = {}
  for callback in callbacks:
    callback_type = callback['callback_type']
    if callback_name == callback['callback_name']:
      callback_detail = {}
      callback_detail['callback_name'] = callback_name
      if callback_type == 'subscription_callback':
        callback_detail['callback_type'] = 'sub'
        callback_detail['description'] = callback['topic_name']
      elif callback_type == 'timer_callback':
        callback_detail['callback_type'] = 'timer'
        period_ms = float(callback['period_ns']) / 1e6
        callback_detail['description'] = str(period_ms) + 'ms'
      else:
        logger.warning("unexpected callback type")
        callback_detail['callback_type'] = callback_type
        callback_detail['description'] = ''
      return callback_detail
  logger.error('callback_name not found: %s', callback_name)
  return None


def create_callback_group_list(node, dict_cbgroup2executor, dict_cbgroup2color):
  """
  Create information of callback group for a node

  Note
  ---
  example:
  [
    {
      "callback_group_name": "callback_group_name",
      "callback_group_type": "callback_group_type",
      "executor_name": "executor_name",
      "color": [255, 0, 0],
      "callback_detail_list": [
        {
          "callback_name": "callback_name",
          "callback_type": "subscription_callback",
          "description": "/topic_sub3pub1"
        },
      ]
    }
  ]
  """

  callback_group_list = []
  if 'callback_groups' not in node or 'callbacks' not in node:
    return callback_group_list

  callback_groups = node['callback_groups']
  callbacks = node['callbacks']
  for callback_group in callback_groups:
    callback_group_info = {}
    callback_group_name = callback_group['callback_group_name']
    callback_group_type = callback_group['callback_group_type']
    callback_names = callback_group['callback_names']
    callback_group_info['callback_group_name'] = callback_group_name
    callback_group_info['callback_group_type'] = callback_group_type
    if callback_group_name in dict_cbgroup2executor:
      callback_group_info['executor_name'] = dict_cbgroup2executor[callback_group_name]
      callback_group_info['color'] = dict_cbgroup2color[callback_group_name]
    else:
      is_display_none_excutor = False
      if is_display_none_excutor:
        callback_group_info['executor_name'] = 'None'
        callback_group_info['color'] = [255, 255, 255]
      else:
        continue
    callback_group_info['callback_detail_list'] = []
    for callback_name in callback_names:
      callback_detail = create_callback_detail(callbacks, callback_name)
      if callback_detail:
        max_callback_detail_list = 50
        if len(callback_group_info['callback_detail_list']) < max_callback_detail_list:
          callback_group_info['callback_detail_list'].append(callback_detail)
        elif len(callback_group_info['callback_detail_list']) == max_callback_detail_list:
          logger.warning(f'Too many callbacks exist in {node["node_name"]}. The following callback is ignored. {callback_detail}')
          callback_detail = {
            'callback_name': 'Too many callbacks',
            'callback_type': '',
            'description': 'Too many callbacks'}
          callback_group_info['callback_detail_list'].append(callback_detail)
    callback_group_list.append(callback_group_info)
  return callback_group_list


def create_dict_node_callbackgroup(yml):
  """
  Create dictionary Node->CallbackGroupInfo

  Note
  ---
  example:
  {
    "node_name": [callback_group_list]
  }
  """
  dict_cbgroup2executor, dict_cbgroup2color = create_dict_cbgroup2executor(yml)
  dict_node_cbgroup = {}
  nodes = yml['nodes']
  for node in nodes:
    node_name = quote_name(node['node_name'])
    callback_group_list = create_callback_group_list(node, dict_cbgroup2executor,
                             dict_cbgroup2color)
    dict_node_cbgroup[node_name] = callback_group_list
  return dict_node_cbgroup


def extend_callback_group(filename: str,
              graph: nx.classes.digraph.DiGraph) -> nx.classes.digraph.DiGraph:
  """Add callback group info to a graph"""
  with open(filename, encoding='UTF-8') as file:
    yml = yaml.safe_load(file)
    dict_node_cbgroup = create_dict_node_callbackgroup(yml)
    # import json
    # with open('caret_executor.json', encoding='UTF-8', mode='w') as f_caret_executor:
    #     json.dump(dict_node_cbgroup, f_caret_executor, ensure_ascii=True, indent=4)
  for node_name in graph.nodes:
    graph.nodes[node_name]['callback_group_list'] = dict_node_cbgroup[node_name]
  return graph
