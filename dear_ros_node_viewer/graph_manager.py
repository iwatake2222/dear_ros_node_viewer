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
""" Class to manage graph (NetworkX) """
from __future__ import annotations
import os
from enum import Enum
import textwrap
import json
import networkx as nx
import dearpygui.dearpygui as dpg
from dear_ros_node_viewer.logger_factory import LoggerFactory
from dear_ros_node_viewer.caret2networkx import caret2networkx
from dear_ros_node_viewer.dot2networkx import dot2networkx
from dear_ros_node_viewer.ros2networkx import Ros2Networkx
from dear_ros_node_viewer.graph_layout import place_node_by_group, align_layout

logger = LoggerFactory.create(__name__)


class GraphManager:
    """ Binding Graph and GUI components"""

    # Color definitions
    COLOR_HIGHLIGHT_SELECTED = [0, 0, 64]
    COLOR_HIGHLIGHT_PUB = [0, 64, 0]
    COLOR_HIGHLIGHT_SUB = [64, 0, 0]
    COLOR_HIGHLIGHT_DEF = [64, 64, 64]
    COLOR_HIGHLIGHT_EDGE = [196, 196, 196]

    class OmitType(Enum):
        """Name omission type"""
        FULL = 1
        FIRST_LAST = 2
        LAST = 3

    def __init__(self, app_setting, group_setting):
        self.app_setting = app_setting
        self.group_setting = group_setting
        self.dir = './'
        self.graph_size: list[int] = [1920, 1080]
        self.graph: nx.DiGraph = nx.DiGraph()
        self.node_selected_dict: dict[str, bool] = {}    # [node_name, is_selected]

        # bind list to components in PyGui
        self.dpg_bind = {
            'node_id': {},        # {"node_name": id}
            'node_color': {},        # {"node_name": id}
            'nodeedge_id': {},    # {"nodename_edgename": id}
            'nodeedge_text': {},  # {"nodename_edgename": id}
            'edge_color': {},     # {"edge": id}
        }

    def load_graph_from_caret(self, filename: str, target_path: str = 'all_graph'):
        """ load_graph_from_caret """
        self.graph = caret2networkx(filename, target_path,
                                    self.app_setting['ignore_unconnected_nodes'])
        self.load_graph_postprocess(filename)

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
        self.graph = place_node_by_group(self.graph, self.group_setting)
        self.graph = align_layout(self.graph)
        self._reset_internl_status()

    def _reset_internl_status(self):
        """ Reset internal status """
        self.node_selected_dict.clear()
        for node_name in self.graph.nodes:
            self.node_selected_dict[node_name] = False
        self.dpg_bind['node_id'].clear()
        self.dpg_bind['node_color'].clear()
        self.dpg_bind['nodeedge_id'].clear()
        self.dpg_bind['nodeedge_text'].clear()
        self.dpg_bind['edge_color'].clear()

    def add_dpg_node_id(self, node_name, dpg_id):
        """ Add association b/w node_name and dpg_id """
        self.dpg_bind['node_id'][node_name] = dpg_id

    def add_dpg_node_color(self, node_name, dpg_id):
        """ Add association b/w node_name and dpg_id """
        self.dpg_bind['node_color'][node_name] = dpg_id

    def add_dpg_nodeedge_idtext(self, node_name, edge_name, attr_id, text_id):
        """ Add association b/w node_attr and dpg_id """
        key = self._make_nodeedge_key(node_name, edge_name)
        self.dpg_bind['nodeedge_id'][key] = attr_id
        self.dpg_bind['nodeedge_text'][key] = text_id

    def add_dpg_edge_color(self, edge_name, edge_id):
        """ Add association b/w edge and dpg_id """
        self.dpg_bind['edge_color'][edge_name] = edge_id

    def get_dpg_nodeedge_id(self, node_name, edge_name):
        """ Get association for a selected name """
        key = self._make_nodeedge_key(node_name, edge_name)
        return self.dpg_bind['nodeedge_id'][key]

    def _make_nodeedge_key(self, node_name, edge_name):
        """create dictionary key for topic attribute in node"""
        return node_name + '###' + edge_name

    def high_light_node(self, dpg_id_node):
        """ High light the selected node and connected nodes """
        selected_node_name = [k for k, v in self.dpg_bind['node_id'].items() if v == dpg_id_node][0]
        is_re_clicked = self.node_selected_dict[selected_node_name]
        for node_name, _ in self.node_selected_dict.items():
            publishing_edge_list = [e for e in self.graph.edges if node_name in e[0]]
            publishing_edge_subscribing_node_name_list = \
                [e[1] for e in self.graph.edges if e[0] == node_name]
            subscribing_edge_list = [e for e in self.graph.edges if node_name in e[1]]
            subscribing_edge_publishing_node_name_list = \
                [e[0] for e in self.graph.edges if e[1] == node_name]
            if self.node_selected_dict[node_name]:
                # Disable highlight for all the other nodes#
                self.node_selected_dict[node_name] = False
                dpg.set_value(
                    self.dpg_bind['node_color'][node_name],
                    self.COLOR_HIGHLIGHT_DEF)
                for edge_name in publishing_edge_list:
                    dpg.set_value(
                        self.dpg_bind['edge_color'][edge_name],
                        self.graph.nodes[node_name]['color'])
                for pub_node_name in publishing_edge_subscribing_node_name_list:
                    dpg.set_value(
                        self.dpg_bind['node_color'][pub_node_name],
                        self.COLOR_HIGHLIGHT_DEF)
                for edge_name in subscribing_edge_list:
                    dpg.set_value(
                        self.dpg_bind['edge_color'][edge_name],
                        self.graph.nodes[node_name]['color'])  # todo. incorrect color
                for sub_node_name in subscribing_edge_publishing_node_name_list:
                    dpg.set_value(
                        self.dpg_bind['node_color'][sub_node_name],
                        self.COLOR_HIGHLIGHT_DEF)
                break

        if not is_re_clicked:
            # Enable highlight for the selected node #
            publishing_edge_list = [e for e in self.graph.edges if selected_node_name in e[0]]
            publishing_edge_subscribing_node_name_list = \
                [e[1] for e in self.graph.edges if e[0] == selected_node_name]
            subscribing_edge_list = [e for e in self.graph.edges if selected_node_name in e[1]]
            subscribing_edge_publishing_node_name_list = \
                [e[0] for e in self.graph.edges if e[1] == selected_node_name]
            self.node_selected_dict[selected_node_name] = True
            dpg.set_value(
                self.dpg_bind['node_color'][selected_node_name],
                self.COLOR_HIGHLIGHT_SELECTED)
            for edge_name in publishing_edge_list:
                dpg.set_value(
                    self.dpg_bind['edge_color'][edge_name],
                    self.COLOR_HIGHLIGHT_EDGE)
            for pub_node_name in publishing_edge_subscribing_node_name_list:
                dpg.set_value(
                    self.dpg_bind['node_color'][pub_node_name],
                    self.COLOR_HIGHLIGHT_PUB)
            for edge_name in subscribing_edge_list:
                dpg.set_value(
                    self.dpg_bind['edge_color'][edge_name],
                    self.COLOR_HIGHLIGHT_EDGE)
            for sub_node_name in subscribing_edge_publishing_node_name_list:
                dpg.set_value(
                    self.dpg_bind['node_color'][sub_node_name],
                    self.COLOR_HIGHLIGHT_SUB)

    def zoom_inout(self, is_zoom_in):
        """ Zoom in/out """
        previous_graph_size = self.graph_size
        if is_zoom_in:
            self.graph_size = list(map(lambda val: val * 1.1, self.graph_size))
        else:
            self.graph_size = list(map(lambda val: val * 0.9, self.graph_size))
        scale = (self.graph_size[0] / previous_graph_size[0],
                 self.graph_size[1] / previous_graph_size[1])

        for _, node_id in self.dpg_bind['node_id'].items():
            pos = dpg.get_item_pos(node_id)
            pos = (pos[0] * scale[0], pos[1] * scale[1])
            dpg.set_item_pos(node_id, pos)

    def reset_layout(self):
        """ Reset node layout """
        for node_name, node_id in self.dpg_bind['node_id'].items():
            pos = self.graph.nodes[node_name]['pos']
            pos = (pos[0] * self.graph_size[0], pos[1] * self.graph_size[1])
            dpg.set_item_pos(node_id, pos)

    def load_layout(self):
        """ Load node layout """
        filename = self.dir + 'layout.json'
        if not os.path.exists(filename):
            logger.info('%s does not exist. Use auto layout', filename)
            return
        with open(filename, encoding='UTF-8') as f_layout:
            pos_dict = json.load(f_layout)
        for node_name, pos in pos_dict.items():
            if node_name in self.graph.nodes:
                self.graph.nodes[node_name]['pos'] = pos
        self.reset_layout()

    def save_layout(self):
        """ Save node layout """
        pos_dict = {}
        for node_name, node_id in self.dpg_bind['node_id'].items():
            pos = dpg.get_item_pos(node_id)
            pos = (pos[0] / self.graph_size[0], pos[1] / self.graph_size[1])
            pos_dict[node_name] = pos

        filename = self.dir + '/layout.json'
        with open(filename, encoding='UTF-8', mode='w') as f_layout:
            json.dump(pos_dict, f_layout, ensure_ascii=True, indent=4)

    def update_font(self, font):
        """ Update font used in all nodes according to current font size """
        for node_id in self.dpg_bind['node_id'].values():
            dpg.bind_item_font(node_id, font)

    def update_nodename(self, omit_type: OmitType):
        """ Update node name """
        for node_name, node_id in self.dpg_bind['node_id'].items():
            dpg.set_item_label(node_id, self._omit_name(node_name, omit_type))

    def update_edgename(self, omit_type: OmitType):
        """ Update edge name """
        for nodeedge_name, text_id in self.dpg_bind['nodeedge_text'].items():
            edgename = nodeedge_name.split('###')[-1]
            dpg.set_value(text_id, value=self._omit_name(edgename, omit_type))

    def _omit_name(self, name: str, omit_type: OmitType) -> str:
        """ replace an original name to a name to be displayed """
        display_name = name.strip('"')
        if omit_type == self.OmitType.FULL:
            display_name = textwrap.fill(display_name, 60)
        elif omit_type == self.OmitType.FIRST_LAST:
            display_name = display_name.split('/')
            if '' in display_name:
                display_name.remove('')
            if len(display_name) > 1:
                display_name = '/' + display_name[0] + '/' + display_name[-1]
            else:
                display_name = '/' + display_name[0]
            display_name = textwrap.fill(display_name, 50)
        else:
            display_name = display_name.split('/')
            display_name = '/' + display_name[-1]
            display_name = textwrap.fill(display_name, 40)

        return display_name

    def copy_selected_node_name(self, dpg_id_nodeeditor):
        """Copy selected node names to clipboard"""
        def get_key(dic, val):
            for key, value in dic.items():
                if val == value:
                    return key
            return None

        node_name_list = ''
        for node_id in dpg.get_selected_nodes(dpg_id_nodeeditor):
            node_name = get_key(self.dpg_bind['node_id'], node_id)
            # node_name = node_name.strip('"')
            node_name_list += node_name + ',\n'
            print(node_name)
        print('---')

        dpg.set_clipboard_text(node_name_list)
