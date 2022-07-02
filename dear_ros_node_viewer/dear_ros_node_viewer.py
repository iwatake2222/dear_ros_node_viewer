# Copyright 2022 takeshi-iwanari
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
import numpy as np
import networkx as nx

from dear_ros_node_viewer.graph_manager import GraphManager
from dear_ros_node_viewer.networkx2dearpygui import Networkx2DearPyGui


def load_setting_json(setting_file):
    """
    Load JSON setting file
    Set default values if the file doesn't exist
    """
    if os.path.isfile(setting_file):
        with open(setting_file, encoding='UTF-8') as f_setting:
            setting = json.load(f_setting)
        app_setting = setting['app_setting']
        group_setting = setting['group_setting']
    else:
        app_setting = {
            "font": "/usr/share/fonts/truetype/ubuntu/Ubuntu-C.ttf"
        }
        group_setting = {
            "__others__": {
                "offset": [0.0, 0.0, 1.0, 1.0],
                "color": [0, 0, 0]
            }

        }
    return app_setting, group_setting


def main():
    """
    Main function for Dear ROS Node Viewer
    """
    parser = argparse.ArgumentParser(
        description='Visualize Node Diagram using Architecture File Created by CARET')
    parser.add_argument(
        '--graph_file', type=str, default='architecture.yaml',
        help='graph file path (architecture.yaml(CARETw) or rosgraph.dot(rqt_graph))')
    parser.add_argument(
        '--target_path', type=str, default='all_graph',
        help='Specify path to be loaded. default=all_graph')
    parser.add_argument(
        '--setting_file', type=str, default='setting.json',
        help='default=setting.json')
    args = parser.parse_args()

    app_setting, group_setting = load_setting_json(args.setting_file)

    graph_manager = GraphManager(group_setting)
    if '.yaml' in args.graph_file:
        graph_manager.load_graph_from_caret(args.graph_file, args.target_path)
    elif '.dot' in args.graph_file:
        graph_manager.load_graph_from_dots(args.graph_file)
    else:
        print('Unknown file format: {args.graph_file}')
        return


    dpg = Networkx2DearPyGui(
        app_setting, graph_manager, app_setting['window_size'][0], app_setting['window_size'][1])
    dpg.start()

