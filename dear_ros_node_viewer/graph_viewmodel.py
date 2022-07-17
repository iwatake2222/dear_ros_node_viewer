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
""" ViewModel in MVVM """
from __future__ import annotations
import os
from enum import Enum
import textwrap
import json
import dearpygui.dearpygui as dpg
from dear_ros_node_viewer.logger_factory import LoggerFactory

logger = LoggerFactory.create(__name__)


class GraphViewModel:
    """ViewModel"""

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

    def __init__(self):
        self.dir = './'
        self.graph_size: list[int] = [1920, 1080]

    def high_light_node(self, graph, dpg_bind, node_selected_dict, dpg_id_node):
        """ High light the selected node and connected nodes """
        selected_node_name = [k for k, v in dpg_bind['node_id'].items() if v == dpg_id_node][0]
        is_re_clicked = node_selected_dict[selected_node_name]
        for node_name, _ in node_selected_dict.items():
            publishing_edge_list = [e for e in graph.edges if node_name in e[0]]
            publishing_edge_subscribing_node_name_list = \
                [e[1] for e in graph.edges if e[0] == node_name]
            subscribing_edge_list = [e for e in graph.edges if node_name in e[1]]
            subscribing_edge_publishing_node_name_list = \
                [e[0] for e in graph.edges if e[1] == node_name]
            if node_selected_dict[node_name]:
                # Disable highlight for all the other nodes#
                node_selected_dict[node_name] = False
                dpg.set_value(
                    dpg_bind['node_color'][node_name],
                    self.COLOR_HIGHLIGHT_DEF)
                for edge_name in publishing_edge_list:
                    dpg.set_value(
                        dpg_bind['edge_color'][edge_name],
                        graph.nodes[node_name]['color'])
                for pub_node_name in publishing_edge_subscribing_node_name_list:
                    dpg.set_value(
                        dpg_bind['node_color'][pub_node_name],
                        self.COLOR_HIGHLIGHT_DEF)
                for edge_name in subscribing_edge_list:
                    dpg.set_value(
                        dpg_bind['edge_color'][edge_name],
                        graph.nodes[node_name]['color'])  # todo. incorrect color
                for sub_node_name in subscribing_edge_publishing_node_name_list:
                    dpg.set_value(
                        dpg_bind['node_color'][sub_node_name],
                        self.COLOR_HIGHLIGHT_DEF)
                break

        if not is_re_clicked:
            # Enable highlight for the selected node #
            publishing_edge_list = [e for e in graph.edges if selected_node_name in e[0]]
            publishing_edge_subscribing_node_name_list = \
                [e[1] for e in graph.edges if e[0] == selected_node_name]
            subscribing_edge_list = [e for e in graph.edges if selected_node_name in e[1]]
            subscribing_edge_publishing_node_name_list = \
                [e[0] for e in graph.edges if e[1] == selected_node_name]
            node_selected_dict[selected_node_name] = True
            dpg.set_value(
                dpg_bind['node_color'][selected_node_name],
                self.COLOR_HIGHLIGHT_SELECTED)
            for edge_name in publishing_edge_list:
                dpg.set_value(
                    dpg_bind['edge_color'][edge_name],
                    self.COLOR_HIGHLIGHT_EDGE)
            for pub_node_name in publishing_edge_subscribing_node_name_list:
                dpg.set_value(
                    dpg_bind['node_color'][pub_node_name],
                    self.COLOR_HIGHLIGHT_PUB)
            for edge_name in subscribing_edge_list:
                dpg.set_value(
                    dpg_bind['edge_color'][edge_name],
                    self.COLOR_HIGHLIGHT_EDGE)
            for sub_node_name in subscribing_edge_publishing_node_name_list:
                dpg.set_value(
                    dpg_bind['node_color'][sub_node_name],
                    self.COLOR_HIGHLIGHT_SUB)

    def zoom_inout(self, dpg_bind, is_zoom_in):
        """ Zoom in/out """
        previous_graph_size = self.graph_size
        if is_zoom_in:
            self.graph_size = list(map(lambda val: val * 1.1, self.graph_size))
        else:
            self.graph_size = list(map(lambda val: val * 0.9, self.graph_size))
        scale = (self.graph_size[0] / previous_graph_size[0],
                 self.graph_size[1] / previous_graph_size[1])

        for _, node_id in dpg_bind['node_id'].items():
            pos = dpg.get_item_pos(node_id)
            pos = (pos[0] * scale[0], pos[1] * scale[1])
            dpg.set_item_pos(node_id, pos)

    def reset_layout(self, graph, dpg_bind):
        """ Reset node layout """
        for node_name, node_id in dpg_bind['node_id'].items():
            pos = graph.nodes[node_name]['pos']
            pos = (pos[0] * self.graph_size[0], pos[1] * self.graph_size[1])
            dpg.set_item_pos(node_id, pos)

    def load_layout(self, graph, dpg_bind, dir_graph):
        """ Load node layout """
        filename = dir_graph + 'layout.json'
        if not os.path.exists(filename):
            logger.info('%s does not exist. Use auto layout', filename)
            return
        with open(filename, encoding='UTF-8') as f_layout:
            pos_dict = json.load(f_layout)
        for node_name, pos in pos_dict.items():
            if node_name in graph.nodes:
                graph.nodes[node_name]['pos'] = pos
        self.reset_layout(graph, dpg_bind)

    def save_layout(self, dpg_bind, dir_graph):
        """ Save node layout """
        pos_dict = {}
        for node_name, node_id in dpg_bind['node_id'].items():
            pos = dpg.get_item_pos(node_id)
            pos = (pos[0] / self.graph_size[0], pos[1] / self.graph_size[1])
            pos_dict[node_name] = pos

        filename = dir_graph + '/layout.json'
        with open(filename, encoding='UTF-8', mode='w') as f_layout:
            json.dump(pos_dict, f_layout, ensure_ascii=True, indent=4)

    def update_font(self, dpg_bind, font):
        """ Update font used in all nodes according to current font size """
        for node_id in dpg_bind['node_id'].values():
            dpg.bind_item_font(node_id, font)

    def update_nodename(self, dpg_bind, omit_type: OmitType):
        """ Update node name """
        for node_name, node_id in dpg_bind['node_id'].items():
            dpg.set_item_label(node_id, self.omit_name(node_name, omit_type))

    def update_edgename(self, dpg_bind, omit_type: OmitType):
        """ Update edge name """
        for nodeedge_name, text_id in dpg_bind['nodeedge_text'].items():
            edgename = nodeedge_name.split('###')[-1]
            dpg.set_value(text_id, value=self.omit_name(edgename, omit_type))

    def omit_name(self, name: str, omit_type: OmitType) -> str:
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

    def copy_selected_node_name(self, dpg_bind, dpg_id_nodeeditor):
        """Copy selected node names to clipboard"""
        def get_key(dic, val):
            for key, value in dic.items():
                if val == value:
                    return key
            return None

        node_name_list = ''
        for node_id in dpg.get_selected_nodes(dpg_id_nodeeditor):
            node_name = get_key(dpg_bind['node_id'], node_id)
            # node_name = node_name.strip('"')
            node_name_list += node_name + ',\n'
            print(node_name)
        print('---')

        dpg.set_clipboard_text(node_name_list)

    def display_callbackgroup(self, dpg_bind, onoff: bool):
        """Switch visibility of callback group in a node"""
        callbackgroup_id = dpg_bind['callbackgroup_id']
        for _, value in callbackgroup_id.items():
            if onoff:
                dpg.show_item(value)
            else:
                dpg.hide_item(value)
