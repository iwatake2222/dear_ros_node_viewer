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
__init__
"""

from dear_ros_node_viewer.dear_ros_node_viewer import main
from dear_ros_node_viewer.caret2networkx import caret2networkx
from dear_ros_node_viewer.dot2networkx import dot2networkx
from dear_ros_node_viewer.ros2networkx import Ros2Networkx
from dear_ros_node_viewer.graph_layout import place_node_by_group, align_layout
from dear_ros_node_viewer.graph_manager import GraphManager
from dear_ros_node_viewer.networkx2dearpygui import Networkx2DearPyGui


__copyright__    = 'Copyright 2022 Tier IV, Inc.'
__version__      = '0.1.0'
__license__      = 'Apache License 2.0'
__author__       = 'takeshi-iwanari'
__author_email__ = 'takeshi.iwanari@tier4.jp'
__url__          = 'https://github.com/takeshi-iwanari/dear_ros_node_viewer'
__all__ = [
    'main',
    'caret2networkx',
    'dot2networkx',
    'Ros2Networkx',
    'place_node_by_group',
    'align_layout',
    'GraphManager',
    'Networkx2DearPyGui'
]

print('Dear ROS Node Viewer version ' + __version__)
