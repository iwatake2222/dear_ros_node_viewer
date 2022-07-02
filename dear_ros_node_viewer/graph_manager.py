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
""" Class to manage graph (NetworkX) """
from __future__ import annotations
from enum import Enum
import textwrap
import numpy as np
import networkx as nx
import dearpygui.dearpygui as dpg
from dear_ros_node_viewer.caret2networkx import caret2networkx
from dear_ros_node_viewer.dot2networkx import dot2networkx


class GraphManager:
    class OmitType(Enum):
        """Name omission type"""
        FULL = 1
        FIRST_LAST = 2
        LAST = 3

    # Color definitions
    COLOR_HIGHLIGHT_PUB = [64, 0, 0]
    COLOR_HIGHLIGHT_SUB = [0, 64, 0]
    COLOR_HIGHLIGHT_DEF = [64, 64, 64]
    COLOR_HIGHLIGHT_EDGE = [196, 196, 196]

    # Instance variables
    graph_size: list[int] = [1920, 1080]
    graph: nx.DiGraph
    group_setting: dict
    node_selected_dict: dict[str, bool] = {}    # [node_name, is_selected]

    # bind list to components in PyGui
    dpg_node_id_dict: dict[str, int] = {}       # {"node_name": id}
    dpg_node_color_dict: dict[str, int] = {}    # {"node_name": id}
    dpg_nodeedge_id_dict: dict[str, int] = {}   # {"nodename_edgename": id}
    dpg_nodeedge_text_dict: dict[str, int] = {} # {"nodename_edgename": id}
    dpg_edge_color_dict: dict[str, int] = {}    # {"edge": id}


    def __init__(self,group_setting):
        self.group_setting = group_setting

    def load_graph_from_caret(self, filename: str, target_path: str = 'all_graph'):
        """ load_graph_from_caret """
        self.graph = caret2networkx(filename, target_path)
        self.graph = place_node_by_group(self.graph, self.group_setting)
        self.graph = align_layout(self.graph)
        for node_name in self.graph.nodes:
            self.node_selected_dict[node_name] = False


    def load_graph_from_dot(self, filename: str):
        """ load_graph_from_dot """
        self.graph = dot2networkx(filename)
        self.graph = place_node_by_group(self.graph, self.group_setting)
        self.graph = align_layout(self.graph)
        for node_name in self.graph.nodes:
            self.node_selected_dict[node_name] = False

    def load_graph_from_running_ros(self):
        """ load_graph_from_running_ros """
        pass


    def add_dpg_node_id(self, node_name, dpg_id):
        """ Add association b/w node_name and dpg_id """
        self.dpg_node_id_dict[node_name] = dpg_id

    def add_dpg_node_color(self, node_name, dpg_id):
        """ Add association b/w node_name and dpg_id """
        self.dpg_node_color_dict[node_name] = dpg_id

    def add_dpg_nodeedge_idtext(self, node_name, edge_name, attr_id, text_id):
        """ Add association b/w node_attr and dpg_id """
        key = self.make_nodeedge_key(node_name, edge_name)
        self.dpg_nodeedge_id_dict[key] = attr_id
        self.dpg_nodeedge_text_dict[key] = text_id

    def add_dpg_edge_color(self, edge_name, edge_id):
        """ Add association b/w edge and dpg_id """
        self.dpg_edge_color_dict[edge_name] = edge_id

    def get_dpg_nodeedge_id(self, node_name, edge_name):
        """ Get association for a selected name """
        key = self.make_nodeedge_key(node_name, edge_name)
        return self.dpg_nodeedge_id_dict[key]

    def make_nodeedge_key(self, node_name, edge_name):
        """create dictionary key for topic attribute in node"""
        return node_name + '###' + edge_name

    def high_light_node(self, dpg_id_node):
        """ High light the selected node and connected nodes """
        selected_node_name = [k for k, v in self.dpg_node_id_dict.items() if v == dpg_id_node][0]

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
                for edge_name in publishing_edge_list:
                    dpg.set_value(
                        self.dpg_edge_color_dict[edge_name],
                        self.graph.nodes[node_name]['color'])
                for pub_node_name in publishing_edge_subscribing_node_name_list:
                    dpg.set_value(
                        self.dpg_node_color_dict[pub_node_name],
                        self.COLOR_HIGHLIGHT_DEF)
                for edge_name in subscribing_edge_list:
                    dpg.set_value(
                        self.dpg_edge_color_dict[edge_name],
                        self.graph.nodes[node_name]['color'])  # todo. incorrect color
                for sub_node_name in subscribing_edge_publishing_node_name_list:
                    dpg.set_value(
                        self.dpg_node_color_dict[sub_node_name],
                        self.COLOR_HIGHLIGHT_DEF)

            elif selected_node_name == node_name:
                # Enable highlight for the selected node #
                self.node_selected_dict[node_name] = True
                for edge_name in publishing_edge_list:
                    dpg.set_value(
                        self.dpg_edge_color_dict[edge_name],
                        self.COLOR_HIGHLIGHT_EDGE)
                for pub_node_name in publishing_edge_subscribing_node_name_list:
                    dpg.set_value(
                        self.dpg_node_color_dict[pub_node_name],
                        self.COLOR_HIGHLIGHT_PUB)
                for edge_name in subscribing_edge_list:
                    dpg.set_value(
                        self.dpg_edge_color_dict[edge_name],
                        self.COLOR_HIGHLIGHT_EDGE)
                for sub_node_name in subscribing_edge_publishing_node_name_list:
                    dpg.set_value(
                        self.dpg_node_color_dict[sub_node_name],
                        self.COLOR_HIGHLIGHT_SUB)

    def zoom_inout(self, is_zoom_in):
        """ Zoom in/out """
        previous_graph_size = self.graph_size
        if is_zoom_in:
            self.graph_size = list(map(lambda val: val * 1.1, self.graph_size))
        else:
            self.graph_size = list(map(lambda val: val * 0.9, self.graph_size))
        scale = self.graph_size[0] / previous_graph_size[0], self.graph_size[1] / previous_graph_size[1]

        for _, node_id in self.dpg_node_id_dict.items():
            pos = dpg.get_item_pos(node_id)
            pos = (pos[0] * scale[0], pos[1] * scale[1])
            dpg.set_item_pos(node_id, pos)

    def reset_layout(self):
        """ Reset node layout """
        for node_name, node_id in self.dpg_node_id_dict.items():
            pos = self.graph.nodes[node_name]['pos']
            pos = (pos[0] * self.graph_size[0], pos[1] * self.graph_size[1])
            dpg.set_item_pos(node_id, pos)

    def update_font(self, font):
        """ Update font used in all nodes according to current font size """
        for node_id in self.dpg_node_id_dict.values():
                dpg.bind_item_font(node_id, font)

    def update_nodename(self, omit_type: OmitType):
        """ Update node name """
        for node_name, node_id in self.dpg_node_id_dict.items():
            dpg.set_item_label(node_id, self.omit_name(node_name, omit_type))

    def update_edgename(self, omit_type: OmitType):
        """ Update edge name """
        for nodeedge_name, text_id in self.dpg_nodeedge_text_dict.items():
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

def place_node_by_group(graph, group_setting):
    """
    Place all nodes
    Nodes belonging to the same group are placed in the same area.
    The area is specified in group_setting.group_setting
    """

    # for node_name in graph.nodes:
    #     graph.nodes[node_name]['pos'] = [0, 0]
    #     graph.nodes[node_name]['color'] = [128, 128, 128]

    # Add "__other__" if a node doesn't belong to any group to make process easier #
    mapping_list = {}
    for node_name in graph.nodes:
        is_other_node = True
        for group_name in group_setting.keys():
            if group_name in node_name:
                is_other_node = False
        if is_other_node:
            mapping_list[node_name] = '"' + '__others__' + node_name.strip('"') + '"'
        else:
            mapping_list[node_name] = node_name
    graph = nx.relabel_nodes(graph, mapping_list)

    # Place nodes and add properties into graph #
    for group_name, graph_property in group_setting.items():
        layout = place_node(graph, group_name)
        direction = graph_property['direction']
        offset = graph_property['offset']
        color = graph_property['color']

        for node_name in graph.nodes:
            if group_name in node_name:
                pos = layout[node_name]
                pos[1] = 1 - pos[1]     # 0.0 is top, 1.0 is bottom
                if direction == 'horizontal':
                    graph.nodes[node_name]['pos'] = \
                        [offset[0] + pos[1] * offset[2], offset[1] + pos[0] * offset[3]]
                else:
                    graph.nodes[node_name]['pos'] = \
                        [offset[0] + pos[0] * offset[2], offset[1] + pos[1] * offset[3]]
                graph.nodes[node_name]['color'] = color

    # Remove "__other__" #
    mapping_list_swap = {v: k for k, v in mapping_list.items()}
    graph = nx.relabel_nodes(graph, mapping_list_swap)

    return graph


def place_node(graph: nx.classes.digraph.DiGraph, group_name: str, prog: str = 'dot'):
    """
    Place nodes belonging to group.
    Normalized position [x, y] is set to graph.nodes[node]['pos']

    Parameters
    ----------
    graph: nx.classes.digraph.DiGraph
        NetworkX Graph
    group_name: str
        group name
    prog: str  (default: 'dot')
        Name of the GraphViz command to use for layout.
        Options depend on GraphViz version but may include:
        'dot', 'twopi', 'fdp', 'sfdp', 'circo'

    Returns
    -------
    layout: dict[str,tuple[int,int]]
        Dictionary of normalized positions keyed by node.
    """

    graph_modified = nx.DiGraph()
    for node_name in graph.nodes:
        if group_name in node_name:
            graph_modified.add_node(node_name)
    for edge in graph.edges:
        if group_name in edge[0] and group_name in edge[1]:
            graph_modified.add_edge(edge[0], edge[1])
    layout = nx.nx_pydot.pydot_layout(graph_modified, prog=prog)
    layout = normalize_layout(layout)
    return layout


def normalize_layout(layout: dict[str, tuple[int, int]]):
    """
    Normalize positions to [0.0, 1.0] (left-top = (0, 0))

    Parameters
    ----------
    layout: dict[str,tuple[int,int]]
        Dictionary of positions keyed by node.

    Returns
    -------
    layout: dict[str,tuple[int,int]]
        Dictionary of normalized positions keyed by node.
    """

    if len(layout) == 0:
        return layout
    for key, val in layout.items():
        layout[key] = list(val)
    layout_np = np.array(list(layout.values()))
    layout_min, layout_max = layout_np.min(0), layout_np.max(0)
    norm_w = (layout_max[0] - layout_min[0])
    norm_h = (layout_max[1] - layout_min[1])
    if norm_w == 0 or norm_h == 0:
        return layout
    for pos in layout.values():
        pos[0] = (pos[0] - layout_min[0]) / norm_w
        pos[1] = (pos[1] - layout_min[1]) / norm_h
    return layout


def align_layout(graph):
    """
    Set (max+min) / 2 as origin(0, 0)

    Note:
        This logis is not mandatory. I added this just to make zoom a little better
        Without this, zoom in/out is processed based on (0,0)=left-top
        When Dear PyGui support zoomable node editor, this logic is not needed
    """
    layout_np = np.array(list(map(lambda val: val['pos'], graph.nodes.values())))
    layout_min, layout_max = layout_np.min(0), layout_np.max(0)
    offset_x = (layout_max[0] + layout_min[0]) / 2
    offset_y = (layout_max[1] + layout_min[1]) / 2
    # offset_x -= 2 / (layout_max[0] - layout_min[0])
    # offset_y -= 2 / (layout_max[1] - layout_min[1])
    if offset_x == 0 or offset_y == 0:
        return graph
    for node_name in graph.nodes:
        graph.nodes[node_name]['pos'][0] -= offset_x
        graph.nodes[node_name]['pos'][1] -= offset_y
    return graph
