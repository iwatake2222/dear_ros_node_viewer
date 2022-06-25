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
Class for Viewer
"""

from __future__ import annotations
from enum import Enum
import textwrap
import networkx as nx
import dearpygui.dearpygui as dpg


class Networkx2DearPyGui:
    """
    Display node graph using Dear PyGui from NetworkX graph

    Attributes
    ----------
    graph: nx.classes.digraph.DiGraph
        NetworkX Graph
    node_list: list[str]
        list of nodes in graph
    edge_list: list[str]
        list of edges in graph
    node_edge_dict: dict[str, tuple[list[str], list[str]]]
        association between nod eand edge
        {"node_name": [["/edge_out_name", ], ["/edge_in_name", ]]}
    dpg_node_id_dict: dict[str,int]
        association between node_name and dpg.node_id
    font_size: int
        current font size
    font_list: dict[int, int]
        association between font_size and dpg_font_id
    """

    COLOR_HIGHLIGHT_PUB = [64, 0, 0]
    COLOR_HIGHLIGHT_SUB = [0, 64, 0]
    COLOR_HIGHLIGHT_DEF = [64, 64, 64]
    COLOR_HIGHLIGHT_EDGE = [196, 196, 196]

    class OmitType(Enum):
        """Name omission type"""
        FULL = 1
        FIRST_LAST = 2
        LAST = 3

    graph: nx.classes.digraph.DiGraph
    node_edge_dict: dict[str, tuple[list[str], list[str]]] = {}
    dpg_node_id_dict: dict[str, int] = {}
    dpg_nodeedge_id_dict: dict[str, int] = {}    # {"nodename_edgename": id}
    dpg_nodeedgetext_id_dict: dict[str, int] = {}    # {"nodename_edgename": id}
    dpg_link_id_dict: dict[str, int] = {}
    dpg_node_theme_color: dict[str, int] = {}
    dpg_edge_theme_color: dict[str, int] = {}
    node_selected_dict: dict[str, bool] = {}

    graph_size: list[int] = [100, 100]
    font_size: int = 15
    font_list: dict[int, int] = {}

    def __init__(
            self,
            app_setting: dict,
            graph: nx.classes.digraph.DiGraph,
            window_width: int = 1920,
            window_height: int = 1080):
        """
        Parameters
        ----------
        app_setting: dict
            application settings
        graph: nx.classes.digraph.DiGraph
            NetworkX Graph
        window_width : int,  default 1920
            Windows size
        window_height : int,  default 1080
            Windows size
        """

        self.store_graph(graph)
        self.graph_size = [window_width, window_height]

        dpg.create_context()
        self._make_font_table(app_setting['font'])
        with dpg.handler_registry():
            dpg.add_mouse_wheel_handler(callback=self._cb_wheel)
        with dpg.window(
                width=window_width, height=window_height,
                no_collapse=True, no_title_bar=True, no_move=True,
                no_resize=True) as self.window_id:

            self.add_menu_in_dpg()

            with dpg.node_editor(
                    menubar=False, minimap=True,
                    minimap_location=dpg.mvNodeMiniMap_Location_BottomLeft) as self.nodeeditor_id:
                self.add_node_in_dpg()
                self.add_link_in_dpg()

        # Update node position according to the default graph size #
        self._cb_wheel(0, 0)

        # Dear PyGui stuffs #
        dpg.create_viewport(
            title='Dear ROS Node Viewer',
            width=window_width, height=window_height)
        dpg.set_viewport_resize_callback(self._cb_resize)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def add_menu_in_dpg(self):
        """ Add menu bar """
        with dpg.menu_bar():
            with dpg.menu(label="Layout"):
                dpg.add_menu_item(label="Reset", callback=self._cb_menu_layout_reset)
                dpg.add_menu_item(label="Save", callback=self._cb_menu_layout_save)
                dpg.add_menu_item(label="Load", callback=self._cb_menu_layout_load)

            with dpg.menu(label="Graph"):
                dpg.add_menu_item(label="Current ROS (experimental)",
                                  callback=self._cb_menu_graph_current)

            with dpg.menu(label="Font"):
                dpg.add_slider_int(label="Font Size",
                                   default_value=self.font_size, min_value=8, max_value=40,
                                   callback=self._cb_menu_font_size)

            with dpg.menu(label="Node Name"):
                dpg.add_menu_item(label="Full", callback=self._cb_menu_nodename_full)
                dpg.add_menu_item(label="First + Last", callback=self._cb_menu_nodename_firstlast)
                dpg.add_menu_item(label="Last Only", callback=self._cb_menu_nodename_last)

            with dpg.menu(label="Edge Name"):
                dpg.add_menu_item(label="Full", callback=self._cb_menu_edgename_full)
                dpg.add_menu_item(label="First + Last", callback=self._cb_menu_edgename_firstlast)
                dpg.add_menu_item(label="Last Only", callback=self._cb_menu_edgename_last)

    def add_node_in_dpg(self):
        """ Add nodes """
        for node_name in self.graph.nodes:
            pos = self.graph.nodes[node_name]['pos']
            pos = [
                pos[0] * self.graph_size[0],
                pos[1] * self.graph_size[1]]
            with dpg.node(
                    label=self._omit_name(node_name, self.OmitType.FIRST_LAST),
                    pos=pos) as node_id:

                self.dpg_node_id_dict[node_name] = node_id

                # Set color #
                with dpg.theme() as theme_id:
                    with dpg.theme_component(dpg.mvNode):
                        dpg.add_theme_color(
                            dpg.mvNodeCol_TitleBar,
                            self.graph.nodes[node_name]['color']
                            if 'color' in self.graph.nodes[node_name]
                            else [32, 32, 32],
                            category=dpg.mvThemeCat_Nodes)
                        theme_color = dpg.add_theme_color(
                            dpg.mvNodeCol_NodeBackground,
                            [64, 64, 64],
                            category=dpg.mvThemeCat_Nodes)
                        self.dpg_node_theme_color[node_name] = theme_color
                        dpg.bind_item_theme(node_id, theme_id)

                # Set callback #
                with dpg.item_handler_registry() as node_select_handler:
                    dpg.add_item_clicked_handler(callback=self._cb_node_clicked)
                    dpg.bind_item_handler_registry(node_id, node_select_handler)

                # Make association dictionary #
                for edge_in in self.node_edge_dict[node_name][1]:
                    with dpg.node_attribute() as attr_id:
                        text_id = dpg.add_text(
                            default_value=self._omit_name(edge_in, self.OmitType.LAST))
                        key = self.make_nodeedge_key(node_name, edge_in)
                        self.dpg_nodeedge_id_dict[key] = attr_id
                        self.dpg_nodeedgetext_id_dict[key] = text_id
                for edge_out in self.node_edge_dict[node_name][0]:
                    with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output) as attr_id:
                        text_id = dpg.add_text(
                            default_value=self._omit_name(edge_out, self.OmitType.LAST))
                        key = self.make_nodeedge_key(node_name, edge_out)
                        self.dpg_nodeedge_id_dict[key] = attr_id
                        self.dpg_nodeedgetext_id_dict[key] = text_id

    def add_link_in_dpg(self, ):
        """ Add links between nodes """
        for edge in self.graph.edges:
            if 'label' in self.graph.edges[edge]:
                label = self.graph.edges[edge]['label']
                edge_id = dpg.add_node_link(
                    self.dpg_nodeedge_id_dict[self.make_nodeedge_key(edge[1], label)],
                    self.dpg_nodeedge_id_dict[self.make_nodeedge_key(edge[0], label)])
            else:
                edge_id = dpg.add_node_link(
                    self.dpg_nodeedge_id_dict[self.make_nodeedge_key(edge[1], 'in')],
                    self.dpg_nodeedge_id_dict[self.make_nodeedge_key(edge[0], 'out')])
            self.dpg_link_id_dict[edge] = edge_id

            # Set color. color is the same color as publisher #
            with dpg.theme() as theme_id:
                with dpg.theme_component(dpg.mvNodeLink):
                    theme_color = dpg.add_theme_color(
                        dpg.mvNodeCol_Link,
                        self.graph.nodes[edge[0]]['color'],
                        category=dpg.mvThemeCat_Nodes)
                    self.dpg_edge_theme_color[edge] = theme_color
                    dpg.bind_item_theme(edge_id, theme_id)

    def make_nodeedge_key(self, node_name, edge_in):
        """create dictionary key for topic attribute in node"""
        return node_name + '###' + edge_in

    def store_graph(self, graph: nx.classes.digraph.DiGraph):
        """
        Store graph information
        """
        self.graph = graph

        # Associate edge with node #
        for node_name in self.graph.nodes:
            self.node_edge_dict[node_name] = [set([]), set([])]
        for edge in self.graph.edges:
            if 'label' in self.graph.edges[edge]:
                label = self.graph.edges[edge]['label']
                self.node_edge_dict[edge[0]][0].add(label)
                self.node_edge_dict[edge[1]][1].add(label)
            else:
                self.node_edge_dict[edge[0]][0].add('out')
                self.node_edge_dict[edge[1]][1].add('in')

        for node_name in self.graph.nodes:
            self.node_selected_dict[node_name] = False

    def _cb_resize(self, sender, app_data):
        """
        callback function for window resized (Dear PyGui)
        change node editer size
        """
        window_width = app_data[2]
        window_height = app_data[3]
        dpg.set_item_width(self.window_id, window_width)
        dpg.set_item_height(self.window_id, window_height)

    def _cb_node_clicked(self, sender, app_data):
        """
        change connedted node color
        restore node color when re-clicked
        """
        node_id = app_data[1]
        selected_node_name = [k for k, v in self.dpg_node_id_dict.items() if v == node_id][0]

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
                        self.dpg_edge_theme_color[edge_name],
                        self.graph.nodes[node_name]['color'])
                for pub_node_name in publishing_edge_subscribing_node_name_list:
                    dpg.set_value(
                        self.dpg_node_theme_color[pub_node_name],
                        self.COLOR_HIGHLIGHT_DEF)
                for edge_name in subscribing_edge_list:
                    dpg.set_value(
                        self.dpg_edge_theme_color[edge_name],
                        self.graph.nodes[node_name]['color'])  # todo. incorrect color
                for sub_node_name in subscribing_edge_publishing_node_name_list:
                    dpg.set_value(
                        self.dpg_node_theme_color[sub_node_name],
                        self.COLOR_HIGHLIGHT_DEF)

            elif selected_node_name == node_name:
                # Enable highlight for the selected node #
                self.node_selected_dict[node_name] = True
                for edge_name in publishing_edge_list:
                    dpg.set_value(
                        self.dpg_edge_theme_color[edge_name],
                        self.COLOR_HIGHLIGHT_EDGE)
                for pub_node_name in publishing_edge_subscribing_node_name_list:
                    dpg.set_value(
                        self.dpg_node_theme_color[pub_node_name],
                        self.COLOR_HIGHLIGHT_PUB)
                for edge_name in subscribing_edge_list:
                    dpg.set_value(
                        self.dpg_edge_theme_color[edge_name],
                        self.COLOR_HIGHLIGHT_EDGE)
                for sub_node_name in subscribing_edge_publishing_node_name_list:
                    dpg.set_value(
                        self.dpg_node_theme_color[sub_node_name],
                        self.COLOR_HIGHLIGHT_SUB)

    def _cb_wheel(self, sender, app_data):
        """
        callback function for mouse wheel in node editor(Dear PyGui)
        zoom in/out graph according to wheel direction
        """

        # Save current layout in normalized coordinate
        for node_name, node_id in self.dpg_node_id_dict.items():
            pos = dpg.get_item_pos(node_id)
            self.graph.nodes[node_name]['pos_changed'] = [
                pos[0] / self.graph_size[0],
                pos[1] / self.graph_size[1]]

        if app_data > 0:
            self.graph_size = list(map(lambda val: val * 1.1, self.graph_size))
        elif app_data < 0:
            self.graph_size = list(map(lambda val: val * 0.9, self.graph_size))

        # Update node position according to new graph size
        for node_name, node_id in self.dpg_node_id_dict.items():
            pos = self.graph.nodes[node_name]['pos_changed']
            pos = (pos[0] * self.graph_size[0], pos[1] * self.graph_size[1])
            dpg.set_item_pos(node_id, pos)

    def _cb_menu_layout_reset(self, sender, app_data, user_data):
        """ Reset layout """
        for node_name, node_id in self.dpg_node_id_dict.items():
            pos = self.graph.nodes[node_name]['pos']
            pos = (pos[0] * self.graph_size[0], pos[1] * self.graph_size[1])
            dpg.set_item_pos(node_id, pos)

    def _cb_menu_layout_save(self, sender, app_data, user_data):
        """ Save current layout """
        print('not implemented yet')

    def _cb_menu_layout_load(self, sender, app_data, user_data):
        """ Load layout from file """
        print('not implemented yet')

    def _cb_menu_graph_current(self, sender, app_data, user_data):
        """ Update graph using current ROS status """
        print('not implemented yet')

    def _cb_menu_font_size(self, sender, app_data, user_data):
        """ Change font size """
        self.font_size = app_data
        self._update_font()

    def _cb_menu_nodename_full(self, sender, app_data, user_data):
        """ Display full name """
        self._update_nodename(self.OmitType.FULL)

    def _cb_menu_nodename_firstlast(self, sender, app_data, user_data):
        """ Display omitted name """
        self._update_nodename(self.OmitType.FIRST_LAST)

    def _cb_menu_nodename_last(self, sender, app_data, user_data):
        """ Display omitted name """
        self._update_nodename(self.OmitType.LAST)

    def _cb_menu_edgename_full(self, sender, app_data, user_data):
        """ Display full name """
        self._update_edgename(self.OmitType.FULL)

    def _cb_menu_edgename_firstlast(self, sender, app_data, user_data):
        """ Display omitted name """
        self._update_edgename(self.OmitType.FIRST_LAST)

    def _cb_menu_edgename_last(self, sender, app_data, user_data):
        """ Display omitted name """
        self._update_edgename(self.OmitType.LAST)

    def _update_font(self):
        """
        Update font used in all nodes according to current font size
        """
        for node_id in self.dpg_node_id_dict.values():
            if self.font_size in self.font_list:
                dpg.bind_item_font(node_id, self.font_list[self.font_size])

    def _make_font_table(self, font_path):
        """Make font table"""
        with dpg.font_registry():
            for i in range(8, 40):
                try:
                    self.font_list[i] = dpg.add_font(font_path, i)
                except SystemError:
                    print('Failed to load font')

    def _update_nodename(self, omit_type: Networkx2DearPyGui.OmitType):
        """Update node name"""
        for node_name, node_id in self.dpg_node_id_dict.items():
            dpg.set_item_label(node_id, self._omit_name(node_name, omit_type))

    def _update_edgename(self, omit_type: Networkx2DearPyGui.OmitType):
        """Update edge name"""
        for nodeedge_name, text_id in self.dpg_nodeedgetext_id_dict.items():
            edgename = nodeedge_name.split('###')[-1]
            dpg.set_value(text_id, value=self._omit_name(edgename, omit_type))

    def _omit_name(self, name: str, omit_type: Networkx2DearPyGui.OmitType) -> str:
        """
        replace an original name to a name to be displayed
        """
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


if __name__ == '__main__':
    def local_main():
        """main function for this file"""
        graph = nx.DiGraph()
        nx.add_path(graph, ['3', '5', '4', '1', '0', '2'])
        nx.add_path(graph, ['3', '0', '4', '2', '1', '5'])
        layout = nx.spring_layout(graph)
        for key, val in layout.items():
            graph.nodes[key]['pos'] = list(val)
            graph.nodes[key]['color'] = [128, 128, 128]
        app_setting = {
            "font": "/usr/share/fonts/truetype/ubuntu/Ubuntu-C.ttf"
        }
        Networkx2DearPyGui(app_setting, graph)

    local_main()
