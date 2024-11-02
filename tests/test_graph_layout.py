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
"""
Test graph_layout module
"""

import networkx as nx
from src.dear_ros_node_viewer.graph_layout import place_node_by_group, align_layout


def test_graph_layout():
    graph = nx.MultiDiGraph()
    nx.add_path(graph, ['"/3"', '"/5"', '"/4"', '"/1"', '"/0"', '"/2"'])

    group_setting = {
        "__others__": {
            "direction": "horizontal",
            "offset": [0.0, 0.0, 1.0, 1.0],
            "color": [16, 64, 96]
        }
    }

    graph = place_node_by_group(graph, group_setting)
    graph = align_layout(graph)
