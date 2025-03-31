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
"""Class to manage graph (NetworkX)"""
from __future__ import annotations
import os
import re
import networkx as nx
from .logger_factory import LoggerFactory
from .caret2networkx import caret2networkx
from .caret_extend_callback_group import extend_callback_group
from .caret_extend_path import get_path_dict
from .dot2networkx import dot2networkx
from .ros2networkx import Ros2Networkx
from .graph_layout import place_node_by_group, align_layout

logger = LoggerFactory.create(__name__)


class GraphManager:
  """Class to manage graph (NetworkX)"""
  def __init__(self, app_setting, group_setting):
    self.app_setting = app_setting
    self.group_setting = group_setting
    self.dir = './'
    self.graph: nx.DiGraph = nx.MultiDiGraph()
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
    self.filter_topic()     # delete topic before node
    self.filter_node()
    if len(self.graph.nodes):
      self.graph = place_node_by_group(self.graph, self.group_setting)
      # self.graph = align_layout(self.graph)

  def filter_node(self):
    """Remove nodes which match filter setting"""
    remove_node_list = []
    for node_name in self.graph.nodes:
      node_name_org = node_name.strip('"')
      for pattern in self.app_setting['ignore_node_list']:
        if re.fullmatch(pattern, node_name_org):
          remove_node_list.append(node_name)
          break
    self.graph.remove_nodes_from(remove_node_list)
    logger.info('%s nodes are removed by filter', len(remove_node_list))

    if self.app_setting['ignore_unconnected_nodes']:
      isolated_node_list = list(nx.isolates(self.graph))
      logger.info('%s nodes are removed due to isolated', len(isolated_node_list))
      self.graph.remove_nodes_from(isolated_node_list)

  def filter_topic(self):
    """Remove topics which match filter setting"""
    remove_edge_list = []
    for edge in self.graph.edges:
      topic_name = self.graph.edges[edge]['label']
      topic_name = topic_name.strip('"')
      for pattern in self.app_setting['ignore_topic_list']:
        if re.fullmatch(pattern, topic_name):
          remove_edge_list.append(edge)
          break
    self.graph.remove_edges_from(remove_edge_list)
    logger.info('%s topics are removed by filter', len(remove_edge_list))

  def clear_caret_path_dict(self):
    """ Clear CARET path dict """
    self.caret_path_dict.clear()
    self.caret_path_dict['<< CLEAR >>'] = []
