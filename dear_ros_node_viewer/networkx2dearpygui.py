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
""" Class to display node graph """
from __future__ import annotations
import networkx as nx
import dearpygui.dearpygui as dpg
from dear_ros_node_viewer.logger_factory import LoggerFactory
from dear_ros_node_viewer.graph_manager import GraphManager

logger = LoggerFactory.create(__name__)


class Networkx2DearPyGui:
    """ Display node graph using Dear PyGui from NetworkX graph """

    # Color definitions
    COLOR_NODE_SELECTED = [0, 0, 64]
    COLOR_NODE_BAR = [32, 32, 32]
    COLOR_NODE_BACK = [64, 64, 64]

    def __init__(
            self,
            app_setting: dict,
            graph_manager: GraphManager,
            window_width: int = 1920,
            window_height: int = 1080):

        self.app_setting: dict = app_setting
        self.graph_manager: GraphManager = graph_manager
        self.window_size: list[int] = [window_width, window_height]
        self.font_size: int = 15
        self.font_list: dict[int, int] = {}
        self.dpg_window_id: int = -1
        self.dpg_id_editor: int = -1

    def start(self):
        """ Start Dear PyGui context """
        dpg.create_context()
        self._make_font_table(self.app_setting['font'])
        with dpg.handler_registry():
            dpg.add_mouse_wheel_handler(callback=self._cb_wheel)
            dpg.add_key_press_handler(callback=self._cb_key_press)

        with dpg.window(
                width=self.window_size[0], height=self.window_size[1],
                no_collapse=True, no_title_bar=True, no_move=True,
                no_resize=True) as self.dpg_window_id:

            self.add_menu_in_dpg()

        self.update_node_editor()

        # Update node position and font according to the default graph size and font size
        self._cb_wheel(0, 0)
        self._cb_menu_font_size(None, self.font_size, None)

        # Dear PyGui stuffs
        dpg.create_viewport(
            title='Dear RosNodeViewer',
            width=self.window_size[0], height=self.window_size[1])
        dpg.set_viewport_resize_callback(self._cb_resize)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def update_node_editor(self, graph_manager=None):
        """ Update node editor using new Graph Manager """
        if graph_manager:
            self.graph_manager = graph_manager

        if self.dpg_id_editor != -1:
            dpg.delete_item(self.dpg_id_editor)

        with dpg.window(tag=self.dpg_window_id):
            with dpg.node_editor(
                    menubar=False, minimap=True,
                    minimap_location=dpg.mvNodeMiniMap_Location_BottomLeft) as self.dpg_id_editor:
                self.add_node_in_dpg()
                self.add_link_in_dpg()
        self.graph_manager.load_layout()

    def add_menu_in_dpg(self):
        """ Add menu bar """
        with dpg.menu_bar():
            with dpg.menu(label="Layout"):
                dpg.add_menu_item(label="Reset", callback=self._cb_menu_layout_reset)
                dpg.add_menu_item(label="Save", callback=self._cb_menu_layout_save)
                dpg.add_menu_item(label="Load", callback=self._cb_menu_layout_load)

            with dpg.menu(label="Graph"):
                dpg.add_menu_item(label="Running ROS (experimental)",
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
        """ Add nodes and attributes """
        graph = self.graph_manager.graph
        for node_name in graph.nodes:
            # Calculate position in window
            pos = graph.nodes[node_name]['pos']
            pos = [
                pos[0] * self.graph_manager.graph_size[0],
                pos[1] * self.graph_manager.graph_size[1]]

            # Allocate node
            with dpg.node(label=node_name, pos=pos) as node_id:
                # Save node id
                self.graph_manager.add_dpg_node_id(node_name, node_id)

                # Set color
                with dpg.theme() as theme_id:
                    with dpg.theme_component(dpg.mvNode):
                        dpg.add_theme_color(
                            dpg.mvNodeCol_TitleBar,
                            graph.nodes[node_name]['color']
                            if 'color' in graph.nodes[node_name]
                            else self.COLOR_NODE_BAR,
                            category=dpg.mvThemeCat_Nodes)
                        dpg.add_theme_color(
                            dpg.mvNodeCol_NodeBackgroundSelected,
                            self.COLOR_NODE_SELECTED,
                            category=dpg.mvThemeCat_Nodes)
                        theme_color = dpg.add_theme_color(
                            dpg.mvNodeCol_NodeBackground,
                            self.COLOR_NODE_BACK,
                            category=dpg.mvThemeCat_Nodes)
                        # Set color value
                        self.graph_manager.add_dpg_node_color(node_name, theme_color)
                        dpg.bind_item_theme(node_id, theme_id)

                # Set callback
                with dpg.item_handler_registry() as node_select_handler:
                    dpg.add_item_clicked_handler(callback=self._cb_node_clicked)
                    dpg.bind_item_handler_registry(node_id, node_select_handler)

                # Add text for node I/O(topics)
                self.add_node_attr_in_dpg(graph, node_name)

                # Add text for executor/callbackgroups

        self.graph_manager.update_nodename(GraphManager.OmitType.FIRST_LAST)
        self.graph_manager.update_edgename(GraphManager.OmitType.LAST)

    def add_node_attr_in_dpg(self, graph, node_name):
        """ Add attributes in node """
        edge_list_pub = []
        edge_list_sub = []
        for edge in graph.edges:
            if edge[0] == node_name:
                label = graph.edges[edge]['label'] if 'label' in graph.edges[edge] else 'out'
                if label in edge_list_pub:
                    continue
                edge_list_pub.append(label)
            if edge[1] == node_name:
                label = graph.edges[edge]['label'] if 'label' in graph.edges[edge] else 'in'
                if label in edge_list_sub:
                    continue
                edge_list_sub.append(label)

        for edge in edge_list_sub:
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input) as attr_id:
                text_id = dpg.add_text(default_value=edge)
                self.graph_manager.add_dpg_nodeedge_idtext(node_name, edge, attr_id, text_id)
        for edge in edge_list_pub:
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output) as attr_id:
                text_id = dpg.add_text(default_value=edge)
                self.graph_manager.add_dpg_nodeedge_idtext(node_name, edge, attr_id, text_id)

    def add_link_in_dpg(self, ):
        """ Add links between node I/O """
        graph = self.graph_manager.graph
        for edge in graph.edges:
            if 'label' in graph.edges[edge]:
                label = graph.edges[edge]['label']
                edge_id = dpg.add_node_link(
                    self.graph_manager.get_dpg_nodeedge_id(edge[0], label),
                    self.graph_manager.get_dpg_nodeedge_id(edge[1], label))
            else:
                edge_id = dpg.add_node_link(
                    self.graph_manager.get_dpg_nodeedge_id(edge[0], 'out'),
                    self.graph_manager.get_dpg_nodeedge_id(edge[1], 'in'))

            # Set color. color is the same color as publisher
            with dpg.theme() as theme_id:
                with dpg.theme_component(dpg.mvNodeLink):
                    theme_color = dpg.add_theme_color(
                        dpg.mvNodeCol_Link,
                        graph.nodes[edge[0]]['color'],
                        category=dpg.mvThemeCat_Nodes)
                    self.graph_manager.add_dpg_edge_color(edge, theme_color)
                    dpg.bind_item_theme(edge_id, theme_id)

    def _cb_resize(self, sender, app_data):
        """
        callback function for window resized (Dear PyGui)
        change node editer size
        """
        window_width = app_data[2]
        window_height = app_data[3]
        dpg.set_item_width(self.dpg_window_id, window_width)
        dpg.set_item_height(self.dpg_window_id, window_height)

    def _cb_node_clicked(self, sender, app_data):
        """
        change connedted node color
        restore node color when re-clicked
        """
        node_id = app_data[1]
        self.graph_manager.high_light_node(node_id)

    def _cb_wheel(self, sender, app_data):
        """
        callback function for mouse wheel in node editor(Dear PyGui)
        zoom in/out graph according to wheel direction
        """
        self.graph_manager.zoom_inout(app_data > 0)

    def _cb_key_press(self, sender, app_data):
        """callback function for key press"""
        if app_data == 67:
            # ctrl-c
            self.graph_manager.copy_selected_node_name(self.dpg_id_editor)

    def _cb_menu_layout_reset(self, sender, app_data, user_data):
        """ Reset layout """
        self.graph_manager.reset_layout()

    def _cb_menu_layout_save(self, sender, app_data, user_data):
        """ Save current layout """
        self.graph_manager.save_layout()

    def _cb_menu_layout_load(self, sender, app_data, user_data):
        """ Load layout from file """
        self.graph_manager.load_layout()

    def _cb_menu_graph_current(self, sender, app_data, user_data):
        """ Update graph using current ROS status """
        self.graph_manager.load_graph_from_running_ros()
        self.update_node_editor()

    def _cb_menu_font_size(self, sender, app_data, user_data):
        """ Change font size """
        self.font_size = app_data
        if self.font_size in self.font_list:
            self.graph_manager.update_font(self.font_list[self.font_size])

    def _cb_menu_nodename_full(self, sender, app_data, user_data):
        """ Display full name """
        self.graph_manager.update_nodename(GraphManager.OmitType.FULL)

    def _cb_menu_nodename_firstlast(self, sender, app_data, user_data):
        """ Display omitted name """
        self.graph_manager.update_nodename(GraphManager.OmitType.FIRST_LAST)

    def _cb_menu_nodename_last(self, sender, app_data, user_data):
        """ Display omitted name """
        self.graph_manager.update_nodename(GraphManager.OmitType.LAST)

    def _cb_menu_edgename_full(self, sender, app_data, user_data):
        """ Display full name """
        self.graph_manager.update_edgename(GraphManager.OmitType.FULL)

    def _cb_menu_edgename_firstlast(self, sender, app_data, user_data):
        """ Display omitted name """
        self.graph_manager.update_edgename(GraphManager.OmitType.FIRST_LAST)

    def _cb_menu_edgename_last(self, sender, app_data, user_data):
        """ Display omitted name """
        self.graph_manager.update_edgename(GraphManager.OmitType.LAST)

    def _make_font_table(self, font_path):
        """Make font table"""
        with dpg.font_registry():
            for i in range(8, 40):
                try:
                    self.font_list[i] = dpg.add_font(font_path, i)
                except SystemError:
                    logger.error('Failed to load font: %s', font_path)


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
