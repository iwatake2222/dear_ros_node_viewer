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
import shutil
import pytest
import networkx as nx
from src.dear_ros_node_viewer.graph_layout import (
    place_node_by_group,
    place_node,
    normalize_layout,
    align_layout
)

# Check if graphviz is available
GRAPHVIZ_AVAILABLE = shutil.which('dot') is not None
SKIP_GRAPHVIZ = pytest.mark.skipif(
    not GRAPHVIZ_AVAILABLE,
    reason="graphviz (dot) not installed"
)



class TestPlaceNodeByGroup:
    """Tests for place_node_by_group function"""

    @SKIP_GRAPHVIZ
    def test_place_node_by_group_basic(self):
        """Test basic node placement by group"""
        graph = nx.MultiDiGraph()
        nx.add_path(graph, ['"/3"', '"/5"', '"/4"', '"/1"', '"/0"', '"/2"'])

        group_setting = {
            "__others__": {
                "direction": "horizontal",
                "offset": [0.0, 0.0, 1.0, 1.0],
                "color": [16, 64, 96]
            }
        }

        result = place_node_by_group(graph, group_setting)

        # All nodes should have pos and color attributes
        for node in result.nodes:
            assert 'pos' in result.nodes[node]
            assert 'color' in result.nodes[node]
            assert len(result.nodes[node]['pos']) == 2
            assert len(result.nodes[node]['color']) == 3

    @SKIP_GRAPHVIZ
    def test_place_node_by_group_vertical(self):
        """Test vertical direction placement"""
        graph = nx.MultiDiGraph()
        graph.add_node('"/node_a"')
        graph.add_node('"/node_b"')
        graph.add_edge('"/node_a"', '"/node_b"')

        group_setting = {
            "__others__": {
                "direction": "vertical",
                "offset": [0.0, 0.0, 1.0, 1.0],
                "color": [128, 128, 128]
            }
        }

        result = place_node_by_group(graph, group_setting)

        for node in result.nodes:
            assert 'pos' in result.nodes[node]

    @SKIP_GRAPHVIZ
    def test_place_node_by_group_with_named_group(self):
        """Test placement with named group matching"""
        graph = nx.MultiDiGraph()
        graph.add_node('"/group_a/node_1"')
        graph.add_node('"/group_a/node_2"')
        graph.add_node('"/group_b/node_1"')

        group_setting = {
            "group_a": {
                "direction": "horizontal",
                "offset": [0.0, 0.0, 0.5, 1.0],
                "color": [255, 0, 0]
            },
            "group_b": {
                "direction": "horizontal",
                "offset": [0.5, 0.0, 0.5, 1.0],
                "color": [0, 255, 0]
            },
            "__others__": {
                "direction": "horizontal",
                "offset": [0.0, 0.0, 1.0, 1.0],
                "color": [128, 128, 128]
            }
        }

        result = place_node_by_group(graph, group_setting)

        # Check that nodes in group_a have the correct color
        assert result.nodes['"/group_a/node_1"']['color'] == [255, 0, 0]
        assert result.nodes['"/group_b/node_1"']['color'] == [0, 255, 0]

    @SKIP_GRAPHVIZ
    def test_place_node_by_group_empty_graph(self):
        """Test placement with empty graph"""
        graph = nx.MultiDiGraph()

        group_setting = {
            "__others__": {
                "direction": "horizontal",
                "offset": [0.0, 0.0, 1.0, 1.0],
                "color": [128, 128, 128]
            }
        }

        result = place_node_by_group(graph, group_setting)

        assert len(result.nodes) == 0


class TestPlaceNode:
    """Tests for place_node function"""

    @SKIP_GRAPHVIZ
    def test_place_node_basic(self):
        """Test basic node placement"""
        graph = nx.MultiDiGraph()
        graph.add_node('"/group/node_a"')
        graph.add_node('"/group/node_b"')
        graph.add_edge('"/group/node_a"', '"/group/node_b"')

        layout = place_node(graph, 'group')

        assert '"/group/node_a"' in layout
        assert '"/group/node_b"' in layout
        # Positions should be normalized to [0, 1]
        for pos in layout.values():
            assert 0 <= pos[0] <= 1
            assert 0 <= pos[1] <= 1

    @SKIP_GRAPHVIZ
    def test_place_node_single_node(self):
        """Test placement with single node"""
        graph = nx.MultiDiGraph()
        graph.add_node('"/group/node_a"')

        layout = place_node(graph, 'group')

        assert '"/group/node_a"' in layout

    @SKIP_GRAPHVIZ
    def test_place_node_no_matching_nodes(self):
        """Test placement when no nodes match group"""
        graph = nx.MultiDiGraph()
        graph.add_node('"/other/node_a"')

        layout = place_node(graph, 'group')

        # No nodes should be in layout
        assert len(layout) == 0


class TestNormalizeLayout:
    """Tests for normalize_layout function"""

    def test_normalize_layout_basic(self):
        """Test basic layout normalization"""
        layout = {
            'node_a': (0, 0),
            'node_b': (100, 100),
            'node_c': (50, 50)
        }

        result = normalize_layout(layout)

        # All positions should be in [0, 1] range
        for pos in result.values():
            assert 0 <= pos[0] <= 1
            assert 0 <= pos[1] <= 1

        # Check specific normalized values
        assert result['node_a'] == [0.0, 0.0]
        assert result['node_b'] == [1.0, 1.0]
        assert result['node_c'] == [0.5, 0.5]

    def test_normalize_layout_empty(self):
        """Test normalization of empty layout"""
        layout = {}
        result = normalize_layout(layout)
        assert result == {}

    def test_normalize_layout_single_node(self):
        """Test normalization with single node"""
        layout = {'node_a': (50, 50)}
        result = normalize_layout(layout)
        # Single node should be at (0, 0) after normalization
        assert result['node_a'] == [0.0, 0.0]

    def test_normalize_layout_same_position(self):
        """Test normalization when all nodes at same position"""
        layout = {
            'node_a': (50, 50),
            'node_b': (50, 50),
        }
        result = normalize_layout(layout)
        # Should return without error
        assert 'node_a' in result
        assert 'node_b' in result

    def test_normalize_layout_negative_values(self):
        """Test normalization with negative values"""
        layout = {
            'node_a': (-100, -100),
            'node_b': (100, 100),
        }
        result = normalize_layout(layout)

        assert result['node_a'] == [0.0, 0.0]
        assert result['node_b'] == [1.0, 1.0]


class TestAlignLayout:
    """Tests for align_layout function"""

    def test_align_layout_basic(self):
        """Test basic layout alignment"""
        graph = nx.MultiDiGraph()
        graph.add_node('"/node_a"', pos=[0.0, 0.0])
        graph.add_node('"/node_b"', pos=[1.0, 1.0])

        result = align_layout(graph)

        # Center should be at (0, 0)
        pos_a = result.nodes['"/node_a"']['pos']
        pos_b = result.nodes['"/node_b"']['pos']

        # The center of min and max should be 0
        center_x = (pos_a[0] + pos_b[0]) / 2
        center_y = (pos_a[1] + pos_b[1]) / 2
        assert abs(center_x) < 0.001
        assert abs(center_y) < 0.001

    def test_align_layout_already_centered(self):
        """Test alignment when already centered at origin"""
        graph = nx.MultiDiGraph()
        graph.add_node('"/node_a"', pos=[-0.5, -0.5])
        graph.add_node('"/node_b"', pos=[0.5, 0.5])

        result = align_layout(graph)

        # Should remain centered
        pos_a = result.nodes['"/node_a"']['pos']
        pos_b = result.nodes['"/node_b"']['pos']
        center_x = (pos_a[0] + pos_b[0]) / 2
        center_y = (pos_a[1] + pos_b[1]) / 2
        assert abs(center_x) < 0.001
        assert abs(center_y) < 0.001

    def test_align_layout_single_node(self):
        """Test alignment with single node at origin"""
        graph = nx.MultiDiGraph()
        graph.add_node('"/node_a"', pos=[0.0, 0.0])

        result = align_layout(graph)

        # Single node at origin should remain unchanged
        assert result.nodes['"/node_a"']['pos'] == [0.0, 0.0]

    def test_align_layout_preserves_relative_positions(self):
        """Test that alignment preserves relative positions"""
        graph = nx.MultiDiGraph()
        graph.add_node('"/node_a"', pos=[0.0, 0.0])
        graph.add_node('"/node_b"', pos=[2.0, 0.0])
        graph.add_node('"/node_c"', pos=[1.0, 1.0])

        result = align_layout(graph)

        # Check relative distances are preserved
        pos_a = result.nodes['"/node_a"']['pos']
        pos_b = result.nodes['"/node_b"']['pos']

        # Distance between a and b should still be 2.0
        distance = pos_b[0] - pos_a[0]
        assert abs(distance - 2.0) < 0.001
