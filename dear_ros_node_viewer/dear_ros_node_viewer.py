# Copyright 2022 Tier IV, Inc.
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
from dear_ros_node_viewer.logger_factory import LoggerFactory
from dear_ros_node_viewer.graph_manager import GraphManager
from dear_ros_node_viewer.networkx2dearpygui import Networkx2DearPyGui

logger = LoggerFactory.create(__name__)


def get_font_path(font_name: str) -> str:
    """find font_path from font_name"""
    if font_name[:4] == 'font':
        font_path = os.path.dirname(__file__) + '/' + font_name
        return font_path
    return font_name


def load_setting_json(graph_file):
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

    return app_setting, group_setting


def parse_args():
    """ Parse arguments """
    parser = argparse.ArgumentParser(
        description='Dear RosNodeViewer: Visualize ROS2 Node Graph')
    parser.add_argument(
        'graph_file', type=str, nargs='?', default='architecture.yaml',
        help='Graph file path. e.g. architecture.yaml(CARET) or rosgraph.dot(rqt_graph).\
              default=architecture.yaml')
    args = parser.parse_args()

    logger.debug('args.graph_file = %s', args.graph_file)

    return args


def main():
    """
    Main function for Dear ROS Node Viewer
    """
    args = parse_args()

    app_setting, group_setting = load_setting_json(args.graph_file)

    graph_manager = GraphManager(app_setting, group_setting)
    if '.yaml' in args.graph_file:
        try:
            graph_manager.load_graph_from_caret(args.graph_file)
        except FileNotFoundError as err:
            logger.error(err)
    elif '.dot' in args.graph_file:
        try:
            graph_manager.load_graph_from_dot(args.graph_file)
        except FileNotFoundError as err:
            logger.error(err)
    else:
        logger.error('Graph is not loaded. Unknown file format: %s', args.graph_file)
        # return   # keep going

    dpg = Networkx2DearPyGui(
        app_setting, graph_manager, app_setting['window_size'][0], app_setting['window_size'][1])
    dpg.start()
