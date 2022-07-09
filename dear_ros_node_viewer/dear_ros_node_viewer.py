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

from dear_ros_node_viewer.graph_manager import GraphManager
from dear_ros_node_viewer.networkx2dearpygui import Networkx2DearPyGui


def load_setting_json(setting_file):
    """
    Load JSON setting file
    Set default values if the file doesn't exist
    """
    if not os.path.isfile(setting_file):
        print(f'Unable to find {setting_file}. Use default setting')
        setting_file = os.path.dirname(__file__) + '/setting.json'

    if os.path.isfile(setting_file):
        with open(setting_file, encoding='UTF-8') as f_setting:
            setting = json.load(f_setting)
        app_setting = setting['app_setting']
        group_setting = setting['group_setting']
    else:
        # Incase, default setting file was not found, too
        app_setting = {
            "window_size": [1920, 1080],
            "font": "/usr/share/fonts/truetype/ubuntu/Ubuntu-C.ttf",
            "ignore_unconnected_nodes": True,
            "layout_filename": "layout.json"
        }
        group_setting = {
            "__others__": {
                "direction": "horizontal",
                "offset": [-0.5, -0.5, 1.0, 1.0],
                "color": [16, 64, 96]
            }
        }

    return app_setting, group_setting


def parse_args():
    """ Parse arguments """
    parser = argparse.ArgumentParser(
        description='Dear RosNodeViewer: Visualize ROS2 Node Graph')
    parser.add_argument(
        'graph_file', type=str, nargs='?', default='architecture.yaml',
        help='Graph file path. e.g. architecture.yaml(CARET) or rosgraph.dot(rqt_graph).\
              default=architecture.yaml')
    parser.add_argument(
        '--target_path', type=str, default='all_graph',
        help='Optional: Specify path to be loaded. default=all_graph')
    parser.add_argument(
        '--setting_file', type=str, default='setting.json',
        help='default=setting.json')
    args = parser.parse_args()
    return args


def main():
    """
    Main function for Dear ROS Node Viewer
    """
    args = parse_args()

    app_setting, group_setting = load_setting_json(args.setting_file)

    graph_manager = GraphManager(app_setting, group_setting)
    if '.yaml' in args.graph_file:
        try:
            graph_manager.load_graph_from_caret(args.graph_file, args.target_path)
        except FileNotFoundError as err:
            print(err)
    elif '.dot' in args.graph_file:
        try:
            graph_manager.load_graph_from_dot(args.graph_file)
        except FileNotFoundError as err:
            print(err)
    else:
        print(f'Unknown file format: {args.graph_file}')
        # return   # keep going

    dpg = Networkx2DearPyGui(
        app_setting, graph_manager, app_setting['window_size'][0], app_setting['window_size'][1])
    dpg.start()
