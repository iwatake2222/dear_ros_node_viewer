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
Test dot2networkx module
"""
import os
import tempfile
import pytest
import networkx as nx

from src.dear_ros_node_viewer.dot2networkx import (
    dot2networkx,
    dot2networkx_nodeonly,
    dot2networkx_nodetopic,
)


class TestDot2NetworkxNodeonly:
    """Tests for dot2networkx_nodeonly function"""

    def test_nodeonly_basic(self):
        """Test basic node-only DOT parsing"""
        graph = dot2networkx('./sample/rosgraph_nodeonly.dot')
        assert graph.has_node('"/node_src"')
        assert graph.has_node('"/node_dst"')
        assert isinstance(graph, nx.MultiDiGraph)

    def test_nodeonly_edges(self):
        """Test that edges are correctly parsed"""
        graph = dot2networkx('./sample/rosgraph_nodeonly.dot')
        # Check that there are edges in the graph
        assert len(graph.edges) > 0

    def test_nodeonly_display_unconnected(self):
        """Test display_unconnected_nodes parameter"""
        graph = dot2networkx('./sample/rosgraph_nodeonly.dot', display_unconnected_nodes=True)
        assert len(graph.nodes) >= 1


class TestDot2NetworkxNodetopic:
    """Tests for dot2networkx_nodetopic function"""

    def test_nodetopic_basic(self):
        """Test basic node-topic DOT parsing"""
        graph = dot2networkx('./sample/rosgraph_nodetopic.dot')
        assert graph.has_node('"/node_src"')
        assert graph.has_node('"/node_dst"')

    def test_nodetopic_edges(self):
        """Test that edges are correctly parsed from node-topic format"""
        graph = dot2networkx('./sample/rosgraph_nodetopic.dot')
        # Check that there are edges in the graph
        assert len(graph.edges) > 0


class TestDot2Networkx:
    """Tests for main dot2networkx function"""

    def test_dot2networkx_nodeonly(self):
        """Test loading node-only DOT file"""
        graph = dot2networkx('./sample/rosgraph_nodeonly.dot')
        assert graph.has_node('"/node_src"')

    def test_dot2networkx_nodetopic(self):
        """Test loading node-topic DOT file"""
        graph = dot2networkx('./sample/rosgraph_nodetopic.dot')
        assert graph.has_node('"/node_src"')

    def test_dot2networkx_file_not_found(self):
        """Test error handling for non-existent file"""
        with pytest.raises(Exception):
            dot2networkx('nonexistent_file.dot')

    def test_dot2networkx_invalid_dot(self):
        """Test error handling for invalid DOT file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dot', delete=False) as f:
            f.write('invalid dot { content }}}')
            temp_path = f.name

        try:
            with pytest.raises(Exception):
                dot2networkx(temp_path)
        finally:
            os.unlink(temp_path)

    def test_dot2networkx_empty_graph(self):
        """Test handling empty DOT graph"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dot', delete=False) as f:
            f.write('digraph G { }')
            temp_path = f.name

        try:
            graph = dot2networkx(temp_path)
            assert len(graph.nodes) == 0
        finally:
            os.unlink(temp_path)

    def test_dot2networkx_returns_multidigraph(self):
        """Test that function returns MultiDiGraph"""
        graph = dot2networkx('./sample/rosgraph_nodeonly.dot')
        assert isinstance(graph, nx.MultiDiGraph)

    def test_dot2networkx_simple_graph(self):
        """Test parsing a simple DOT graph"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dot', delete=False) as f:
            f.write('''digraph G {
                n1 [label="/node_a", shape=ellipse];
                n2 [label="/node_b", shape=ellipse];
                n1 -> n2 [label="/topic_1"];
            }''')
            temp_path = f.name

        try:
            graph = dot2networkx(temp_path)
            assert graph.has_node('"/node_a"')
            assert graph.has_node('"/node_b"')
        finally:
            os.unlink(temp_path)

    def test_dot2networkx_with_box_shape(self):
        """Test parsing DOT graph with box shapes (topics)"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dot', delete=False) as f:
            f.write('''digraph G {
                n1 [label="/node_a", shape=ellipse];
                t1 [label="/topic_1", shape=box];
                n2 [label="/node_b", shape=ellipse];
                n1 -> t1;
                t1 -> n2;
            }''')
            temp_path = f.name

        try:
            graph = dot2networkx(temp_path)
            # Should have node_a and node_b connected through topic
            assert graph.has_node('"/node_a"')
            assert graph.has_node('"/node_b"')
        finally:
            os.unlink(temp_path)


class TestDot2NetworkxNodeonlyInternal:
    """Tests for internal dot2networkx_nodeonly function"""

    def test_nodeonly_missing_label(self):
        """Test handling nodes without label attribute"""
        graph_org = nx.MultiDiGraph()
        graph_org.add_node('n1')  # No label attribute
        graph_org.add_node('n2', label='"/node_b"')

        graph = dot2networkx_nodeonly(graph_org)

        # Node without label should be skipped
        assert not graph.has_node('n1')

    def test_nodeonly_edge_missing_label(self):
        """Test handling edges without label attribute"""
        graph_org = nx.MultiDiGraph()
        graph_org.add_node('n1', label='"/node_a"')
        graph_org.add_node('n2', label='"/node_b"')
        graph_org.add_edge('n1', 'n2')  # No label attribute

        graph = dot2networkx_nodeonly(graph_org)

        # Edge without label should be skipped
        assert not graph.has_edge('"/node_a"', '"/node_b"')


class TestDot2NetworkxNodetopicInternal:
    """Tests for internal dot2networkx_nodetopic function"""

    def test_nodetopic_publisher_subscriber(self):
        """Test correct publisher-subscriber relationship parsing"""
        graph_org = nx.MultiDiGraph()
        graph_org.add_node('n1', label='"/node_a"', shape='ellipse')
        graph_org.add_node('t1', label='"/topic_1"', shape='box')
        graph_org.add_node('n2', label='"/node_b"', shape='ellipse')
        graph_org.add_edge('n1', 't1')  # node_a publishes to topic_1
        graph_org.add_edge('t1', 'n2')  # topic_1 subscribed by node_b

        graph = dot2networkx_nodetopic(graph_org)

        assert graph.has_node('"/node_a"')
        assert graph.has_node('"/node_b"')
        assert graph.has_edge('"/node_a"', '"/node_b"')

    def test_nodetopic_missing_shape(self):
        """Test handling nodes without shape attribute"""
        graph_org = nx.MultiDiGraph()
        graph_org.add_node('n1', label='"/node_a"')  # No shape
        graph_org.add_node('n2', label='"/node_b"', shape='ellipse')
        graph_org.add_edge('n1', 'n2')

        graph = dot2networkx_nodetopic(graph_org)

        # Edge should be skipped due to missing shape
        assert len(graph.edges) == 0
