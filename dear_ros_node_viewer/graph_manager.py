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
"""Class to manage graph (NetworkX)"""
from __future__ import annotations
import os
import networkx as nx
from dear_ros_node_viewer.logger_factory import LoggerFactory
from dear_ros_node_viewer.caret2networkx import caret2networkx
from dear_ros_node_viewer.caret_extend_callback_group import extend_callback_group
from dear_ros_node_viewer.caret_extend_path import get_path_dict
from dear_ros_node_viewer.dot2networkx import dot2networkx
from dear_ros_node_viewer.ros2networkx import Ros2Networkx
from dear_ros_node_viewer.graph_layout import place_node_by_group, align_layout

logger = LoggerFactory.create(__name__)


class GraphManager:
    """Class to manage graph (NetworkX)"""
    def __init__(self, app_setting, group_setting):
        self.app_setting = app_setting
        self.group_setting = group_setting
        self.dir = './'
        self.graph: nx.DiGraph = nx.DiGraph()
        self.caret_path_dict: dict = {}

    def load_graph_from_caret(self, filename: str, target_path: str = 'all_graph'):
        """ load_graph_from_caret """
        self.graph = caret2networkx(filename, target_path,
                                    self.app_setting['ignore_unconnected_nodes'])
        self.graph = extend_callback_group(filename, self.graph)
        self.load_graph_postprocess(filename)
        self.caret_path_dict.update(get_path_dict(filename))

    def load_graph_from_dot(self, filename: str):
        """ load_graph_from_dot """
        self.graph = dot2networkx(filename, self.app_setting['ignore_unconnected_nodes'])
        self.load_graph_postprocess(filename)

    def load_graph_from_running_ros(self):
        """ load_graph_from_running_ros """
        ros2networkx = Ros2Networkx(node_name='temp')
        ros2networkx.save_graph('./temp.dot')
        ros2networkx.shutdown()
        self.load_graph_from_dot('./temp.dot')
        # for node in self.graph.nodes:
        #     if '"/temp"' == node:
        #         node_observer = node
        #         break
        # self.graph.remove_node(node_observer)
        # self.reset_internl_status()

    def load_graph_postprocess(self, filename):
        """ Common process after loading graph """
        self.dir = os.path.dirname(filename) + '/' if os.path.dirname(filename) != '' else './'
        self.clear_caret_path_dict()
        if len(self.graph.nodes):
            self.graph = place_node_by_group(self.graph, self.group_setting)
            self.graph = align_layout(self.graph)

    def clear_caret_path_dict(self):
        """ Clear CARET path dict """
        self.caret_path_dict.clear()
        self.caret_path_dict['<< CLEAR >>'] = []
