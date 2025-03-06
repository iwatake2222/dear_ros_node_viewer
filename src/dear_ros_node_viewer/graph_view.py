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
"""Class to display node graph"""
from __future__ import annotations
import networkx as nx
import dearpygui.dearpygui as dpg
from .logger_factory import LoggerFactory
from .graph_viewmodel import GraphViewModel

logger = LoggerFactory.create(__name__)


class GraphView:
  """Class to display node graph"""
  # Color definitions
  COLOR_NODE_SELECTED = [0, 0, 64]
  COLOR_NODE_BAR = [32, 32, 32]
  COLOR_NODE_BACK = [64, 64, 64]

  def __init__(
      self,
      app_setting: dict,
      group_setting: dict
      ):

    self.app_setting: dict = app_setting
    self.graph_viewmodel = GraphViewModel(app_setting, group_setting)
    self.font_size: int = 15
    self.font_list: dict[int, int] = {}
    self.dpg_window_id: int = -1
    self.dpg_id_editor: int = -1
    self.dpg_id_caret_path: int = -1

  def start(self, graph_filename: str, window_width: int = 1920, window_height: int = 1080):
    """ Start Dear PyGui context """
    dpg.create_context()
    dpg.create_viewport(
      title='Dear RosNodeViewer', width=window_width, height=window_height,)
    dpg.setup_dearpygui()

    self._make_font_table(self.app_setting['font'])
    with dpg.handler_registry():
      dpg.add_mouse_wheel_handler(callback=self._cb_wheel)
      dpg.add_key_press_handler(callback=self._cb_key_press)

    with dpg.window(
        pos=[0, 0],
        width=window_width, height=window_height,
        no_collapse=True, no_title_bar=True, no_move=True,
        no_resize=True) as self.dpg_window_id:

      self.add_menu_in_dpg()

    self.graph_viewmodel.load_graph(graph_filename)
    self.update_node_editor()

    # Update node position and font according to the default graph size and font size
    self._cb_wheel(0, 0)
    self._cb_menu_font_size(None, self.font_size, None)

    dpg.set_viewport_resize_callback(self._cb_resize)
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

  def update_node_editor(self):
    """Update node editor"""
    if self.dpg_id_editor != -1:
      dpg.delete_item(self.dpg_id_editor)

    with dpg.window(tag=self.dpg_window_id):
      with dpg.node_editor(
          menubar=False, minimap=True,
          minimap_location=dpg.mvNodeMiniMap_Location_BottomLeft) as self.dpg_id_editor:
        self.add_node_in_dpg()
        self.add_link_in_dpg()
    self.graph_viewmodel.load_layout()

    # Add CARET path
    for path_name, _ in self.graph_viewmodel.graph_manager.caret_path_dict.items():
      dpg.add_menu_item(label=path_name, callback=self._cb_menu_caret_path,
                parent=self.dpg_id_caret_path)

  def add_menu_in_dpg(self):
    """ Add menu bar """
    with dpg.menu_bar():
      with dpg.menu(label="Layout"):
        dpg.add_menu_item(label="Reset", callback=self._cb_menu_layout_reset)
        dpg.add_menu_item(label="Save", callback=self._cb_menu_layout_save, shortcut='(s)')
        dpg.add_menu_item(label="Load", callback=self._cb_menu_layout_load, shortcut='(l)')

      dpg.add_menu_item(label="Copy", callback=self._cb_menu_copy, shortcut='(c)')

      with dpg.menu(label="ROS"):
        dpg.add_menu_item(label="Load Current Gaph",
                  callback=self._cb_menu_graph_current)

      with dpg.menu(label="Font"):
        dpg.add_slider_int(label="Font Size",
                   default_value=self.font_size, min_value=8, max_value=40,
                   callback=self._cb_menu_font_size)

      with dpg.menu(label="NodeName"):
        dpg.add_menu_item(label="Full", callback=self._cb_menu_nodename_full)
        dpg.add_menu_item(label="First + Last", callback=self._cb_menu_nodename_firstlast)
        dpg.add_menu_item(label="Last Only", callback=self._cb_menu_nodename_last)

      with dpg.menu(label="EdgeName"):
        dpg.add_menu_item(label="Full", callback=self._cb_menu_edgename_full)
        dpg.add_menu_item(label="First + Last", callback=self._cb_menu_edgename_firstlast)
        dpg.add_menu_item(label="Last Only", callback=self._cb_menu_edgename_last)

      with dpg.menu(label="CARET"):
        dpg.add_menu_item(label="Show Callback", callback=self._cb_menu_caret_callbackbroup)
        with dpg.menu(label="PATH") as self.dpg_id_caret_path:
          pass

  def add_node_in_dpg(self):
    """ Add nodes and attributes """
    graph = self.graph_viewmodel.get_graph()
    for node_name in graph.nodes:
      # Calculate position in window
      pos = graph.nodes[node_name]['pos']
      pos = [
        pos[0] * self.graph_viewmodel.graph_size[0],
        pos[1] * self.graph_viewmodel.graph_size[1]]

      # Allocate node
      with dpg.node(label=node_name, pos=pos) as node_id:
        # Save node id
        self.graph_viewmodel.add_dpg_node_id(node_name, node_id)

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
            self.graph_viewmodel.add_dpg_node_color(node_name, theme_color)
            dpg.bind_item_theme(node_id, theme_id)

        # Set callback
        with dpg.item_handler_registry() as node_select_handler:
          dpg.add_item_clicked_handler(callback=self._cb_node_clicked)
          dpg.bind_item_handler_registry(node_id, node_select_handler)

        # Add text for node I/O(topics)
        self.add_node_attr_in_dpg(node_name)

    self.graph_viewmodel.update_nodename(GraphViewModel.OmitType.LAST)
    self.graph_viewmodel.update_edgename(GraphViewModel.OmitType.LAST)

  def add_node_attr_in_dpg(self, node_name):
    """ Add attributes in node """
    graph = self.graph_viewmodel.get_graph()
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
        self.graph_viewmodel.add_dpg_nodeedge_idtext(node_name, edge, attr_id, text_id)
    for edge in edge_list_pub:
      with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output) as attr_id:
        text_id = dpg.add_text(default_value=edge)
        self.graph_viewmodel.add_dpg_nodeedge_idtext(node_name, edge,
                               attr_id, text_id)

    # Add text for executor/callbackgroups
    self.add_node_callbackgroup_in_dpg(node_name)
    # Hide by default
    self.graph_viewmodel.display_callbackgroup(False)

  def add_node_callbackgroup_in_dpg(self, node_name):
    """ Add callback group information """
    graph = self.graph_viewmodel.get_graph()
    if 'callback_group_list' in graph.nodes[node_name]:
      callback_group_list = graph.nodes[node_name]['callback_group_list']
      for callback_group in callback_group_list:
        executor_name = callback_group['executor_name']
        callback_group_name = callback_group['callback_group_name']
        # callback_group_type = callback_group['callback_group_type']
        callback_group_name = self.graph_viewmodel.omit_name(
          callback_group_name, GraphViewModel.OmitType.LAST)
        callback_detail_list = callback_group['callback_detail_list']
        color = callback_group['color']
        with dpg.node_attribute() as attr_id:
          dpg.add_text('=== Callback Group [' + executor_name + '] ===', color=color)
          for callback_detail in callback_detail_list:
            # callback_name = callback_detail['callback_name']
            callback_type = callback_detail['callback_type']
            description = callback_detail['description']
            description = self.graph_viewmodel.omit_name(
              description, GraphViewModel.OmitType.LAST)
            dpg.add_text(default_value='cb_' + callback_type + ': ' + description,
                   color=color)
          self.graph_viewmodel.add_dpg_callbackgroup_id(
            callback_group['callback_group_name'], attr_id)

  def add_link_in_dpg(self):
    """ Add links between node I/O """
    graph = self.graph_viewmodel.get_graph()
    for edge in graph.edges:
      if 'label' in graph.edges[edge]:
        label = graph.edges[edge]['label']
        edge_id = dpg.add_node_link(
          self.graph_viewmodel.get_dpg_nodeedge_id(edge[0], label),
          self.graph_viewmodel.get_dpg_nodeedge_id(edge[1], label))
        self.graph_viewmodel.add_dpg_id_edge(label, edge_id)
      else:
        edge_id = dpg.add_node_link(
          self.graph_viewmodel.get_dpg_nodeedge_id(edge[0], 'out'),
          self.graph_viewmodel.get_dpg_nodeedge_id(edge[1], 'in'))

      # Set color. color is the same color as publisher
      with dpg.theme() as theme_id:
        with dpg.theme_component(dpg.mvNodeLink):
          theme_color = dpg.add_theme_color(
            dpg.mvNodeCol_Link,
            graph.nodes[edge[0]]['color'],
            category=dpg.mvThemeCat_Nodes)
          self.graph_viewmodel.add_dpg_edge_color(edge, theme_color)
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
    self.graph_viewmodel.high_light_node(node_id)

  def _cb_wheel(self, sender, app_data):
    """
    callback function for mouse wheel in node editor(Dear PyGui)
    zoom in/out graph according to wheel direction
    """
    self.graph_viewmodel.zoom_inout(app_data > 0)

  def _cb_key_press(self, sender, app_data):
    """callback function for key press"""
    if app_data == dpg.mvKey_S:
      self._cb_menu_layout_save()
    elif app_data == dpg.mvKey_L:
      self._cb_menu_layout_load()
    elif app_data == dpg.mvKey_C:
      self._cb_menu_copy()

  def _cb_menu_layout_reset(self):
    """ Reset layout """
    self.graph_viewmodel.reset_layout()

  def _cb_menu_layout_save(self):
    """ Save current layout """
    self.graph_viewmodel.save_layout()

  def _cb_menu_layout_load(self):
    """ Load layout from file """
    self.graph_viewmodel.load_layout()

  def _cb_menu_copy(self):
    self.graph_viewmodel.copy_selected_node_name(self.dpg_id_editor)

  def _cb_menu_graph_current(self):
    """ Update graph using current ROS status """
    self.graph_viewmodel.load_running_graph()
    self.update_node_editor()

  def _cb_menu_font_size(self, sender, app_data, user_data):
    """ Change font size """
    self.font_size = app_data
    if self.font_size in self.font_list:
      self.graph_viewmodel.update_font(self.font_list[self.font_size])

  def _cb_menu_nodename_full(self):
    """ Display full name """
    self.graph_viewmodel.update_nodename(GraphViewModel.OmitType.FULL)

  def _cb_menu_nodename_firstlast(self):
    """ Display omitted name """
    self.graph_viewmodel.update_nodename(GraphViewModel.OmitType.FIRST_LAST)

  def _cb_menu_nodename_last(self):
    """ Display omitted name """
    self.graph_viewmodel.update_nodename(GraphViewModel.OmitType.LAST)

  def _cb_menu_edgename_full(self):
    """ Display full name """
    self.graph_viewmodel.update_edgename(GraphViewModel.OmitType.FULL)

  def _cb_menu_edgename_firstlast(self):
    """ Display omitted name """
    self.graph_viewmodel.update_edgename(GraphViewModel.OmitType.FIRST_LAST)

  def _cb_menu_edgename_last(self):
    """ Display omitted name """
    self.graph_viewmodel.update_edgename(GraphViewModel.OmitType.LAST)

  def _cb_menu_caret_callbackbroup(self, sender, app_data, user_data):
    """ Show callback group info """
    if dpg.get_item_label(sender) == 'Show Callback':
      self.graph_viewmodel.display_callbackgroup(True)
      dpg.set_item_label(sender, 'Hide Callback')
    else:
      self.graph_viewmodel.display_callbackgroup(False)
      dpg.set_item_label(sender, 'Show Callback')

  def _cb_menu_caret_path(self, sender, app_data, user_data):
    """ High light selected CARET path """
    path_name = dpg.get_item_label(sender)
    self.graph_viewmodel.high_light_caret_path(path_name)

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
    graph = nx.MultiDiGraph()
    nx.add_path(graph, ['3', '5', '4', '1', '0', '2'])
    nx.add_path(graph, ['3', '0', '4', '2', '1', '5'])
    layout = nx.spring_layout(graph)
    for key, val in layout.items():
      graph.nodes[key]['pos'] = list(val)
      graph.nodes[key]['color'] = [128, 128, 128]
    app_setting = {
      "font": "/usr/share/fonts/truetype/ubuntu/Ubuntu-C.ttf"
    }
    GraphView(app_setting, graph)

  local_main()
