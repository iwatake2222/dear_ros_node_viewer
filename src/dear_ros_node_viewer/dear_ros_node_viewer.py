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
Main function for Dear ROS Node Viewer
"""

from __future__ import annotations
import os
import argparse
import json
from .logger_factory import LoggerFactory
from .graph_view import GraphView

logger = LoggerFactory.create(__name__)


def get_font_path(font_name: str) -> str:
  """find font_path from font_name"""
  if font_name[:4] == 'font':
    font_path = os.path.dirname(__file__) + '/' + font_name
    return font_path
  return font_name


def load_setting_json(graph_file, disable_ignore_filter, displace_new_node):
  """
  Load JSON setting file
  Set default values if the file doesn't exist
  """
  if os.path.dirname(graph_file):
    setting_file = os.path.dirname(graph_file) + '/setting.json'
  else:
    setting_file = './setting.json'
  if not os.path.isfile(setting_file):
    logger.info('Unable to find %s. Use default setting', setting_file)
    setting_file = os.path.dirname(__file__) + '/setting.json'

  if os.path.isfile(setting_file):
    with open(setting_file, encoding='UTF-8') as f_setting:
      setting = json.load(f_setting)
    app_setting = setting['app_setting']
    group_setting = setting['group_setting']
  else:
    # Incase, default setting file was not found, too
    logger.info('Unable to find %s. Use fixed default setting', setting_file)
    app_setting = {
      "window_size": [1920, 1080],
      "font": "font/roboto/Roboto-Medium.ttf",
      "ignore_unconnected_nodes": True,
    }
    group_setting = {
      "__others__": {
        "direction": "horizontal",
        "offset": [-0.5, -0.5, 1.0, 1.0],
        "color": [16, 64, 96]
      }
    }

  app_setting['font'] = get_font_path(app_setting['font'])

  if disable_ignore_filter:
    if 'ignore_node_list' in app_setting:
      app_setting['ignore_node_list'] = []
    if 'ignore_topic_list' in app_setting:
      app_setting['ignore_topic_list'] = []

  if displace_new_node:
    for group, setting in group_setting.items():
      group_setting[group]["offset"][0] = setting["offset"][0] - 20
      group_setting[group]["offset"][1] = setting["offset"][1] - 20


  return app_setting, group_setting


def parse_args():
  """ Parse arguments """
  parser = argparse.ArgumentParser(
    description='Dear RosNodeViewer: Visualize ROS2 Node Graph')
  parser.add_argument(
    'graph_file', type=str, nargs='?', default='architecture.yaml',
    help='Graph file path. e.g. architecture.yaml(CARET) or rosgraph.dot(rqt_graph).\
        default=architecture.yaml')
  parser.add_argument('--disable_ignore_filter', action="store_true")
  parser.add_argument('--displace_new_node', action="store_true")
  args = parser.parse_args()

  logger.debug(f'args.graph_file = {args.graph_file}')
  logger.debug(f'args.disable_ignore_filter = {args.disable_ignore_filter}')
  logger.debug(f'args.displace_new_node = {args.displace_new_node}')

  return args


def main():
  """
  Main function for Dear ROS Node Viewer
  """
  args = parse_args()

  app_setting, group_setting = load_setting_json(args.graph_file, args.disable_ignore_filter, args.displace_new_node)
  graph_filename = args.graph_file

  dpg = GraphView(app_setting, group_setting)
  dpg.start(graph_filename, app_setting['window_size'][0], app_setting['window_size'][1])
