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
Test graph_manager module
"""
import os
import shutil
import tempfile
import pytest
import networkx as nx

from src.dear_ros_node_viewer.graph_manager import GraphManager

# Check if graphviz is available
GRAPHVIZ_AVAILABLE = shutil.which('dot') is not None
SKIP_GRAPHVIZ = pytest.mark.skipif(
    not GRAPHVIZ_AVAILABLE,
    reason="graphviz (dot) not installed"
)


def get_default_app_setting():
    """Helper to create default app settings for tests"""
    return {
        'display_unconnected_nodes': False,
        'ignore_node_list': [],
        'ignore_topic_list': [],
    }


def get_default_group_setting():
    """Helper to create default group settings for tests"""
    return {
        "__others__": {
            "direction": "horizontal",
            "offset": [0.0, 0.0, 1.0, 1.0],
            "color": [16, 64, 96]
        }
    }


class TestGraphManagerInit:
    """Tests for GraphManager initialization"""

    def test_init_basic(self):
        """Test basic GraphManager initialization"""
        app_setting = get_default_app_setting()
        group_setting = get_default_group_setting()

        manager = GraphManager(app_setting, group_setting)

        assert manager.app_setting == app_setting
        assert manager.group_setting == group_setting
        assert manager.dir == './'
        assert isinstance(manager.graph, nx.MultiDiGraph)
        assert manager.caret_path_dict == {}



class TestGraphManagerLoadFromCaret:
    """Tests for loading graphs from CARET files"""

    @SKIP_GRAPHVIZ
    def test_load_graph_from_caret_basic(self):
        """Test loading graph from architecture.yaml"""
        app_setting = get_default_app_setting()
        group_setting = get_default_group_setting()
        manager = GraphManager(app_setting, group_setting)

        manager.load_graph_from_caret('architecture.yaml')

        assert len(manager.graph.nodes) > 0
        assert manager.graph.has_node('"/node_src"')

    @SKIP_GRAPHVIZ
    def test_load_graph_from_caret_target_path(self):
        """Test loading graph with specific target path"""
        app_setting = get_default_app_setting()
        group_setting = get_default_group_setting()
        manager = GraphManager(app_setting, group_setting)

        manager.load_graph_from_caret('architecture.yaml', target_path='target_path_0')

        assert len(manager.graph.nodes) > 0

    @SKIP_GRAPHVIZ
    def test_load_graph_from_caret_updates_path_dict(self):
        """Test that caret_path_dict is updated after loading"""
        app_setting = get_default_app_setting()
        group_setting = get_default_group_setting()
        manager = GraphManager(app_setting, group_setting)

        manager.load_graph_from_caret('architecture.yaml')

        # Should have path information
        assert len(manager.caret_path_dict) > 0

    def test_load_graph_from_caret_file_not_found(self):
        """Test error handling for non-existent file"""
        app_setting = get_default_app_setting()
        group_setting = get_default_group_setting()
        manager = GraphManager(app_setting, group_setting)

        with pytest.raises(FileNotFoundError):
            manager.load_graph_from_caret('nonexistent.yaml')



class TestGraphManagerLoadFromDot:
    """Tests for loading graphs from DOT files"""

    @SKIP_GRAPHVIZ
    def test_load_graph_from_dot_nodeonly(self):
        """Test loading graph from node-only DOT file"""
        app_setting = get_default_app_setting()
        group_setting = get_default_group_setting()
        manager = GraphManager(app_setting, group_setting)

        manager.load_graph_from_dot('./sample/rosgraph_nodeonly.dot')

        assert len(manager.graph.nodes) > 0
        assert manager.graph.has_node('"/node_src"')

    @SKIP_GRAPHVIZ
    def test_load_graph_from_dot_nodetopic(self):
        """Test loading graph from node-topic DOT file"""
        app_setting = get_default_app_setting()
        group_setting = get_default_group_setting()
        manager = GraphManager(app_setting, group_setting)

        manager.load_graph_from_dot('./sample/rosgraph_nodetopic.dot')

        assert len(manager.graph.nodes) > 0

    @SKIP_GRAPHVIZ
    def test_load_graph_from_dot_updates_dir(self):
        """Test that directory is updated after loading"""
        app_setting = get_default_app_setting()
        group_setting = get_default_group_setting()
        manager = GraphManager(app_setting, group_setting)

        manager.load_graph_from_dot('./sample/rosgraph_nodeonly.dot')

        assert manager.dir == './sample/'



class TestGraphManagerFilterNode:
    """Tests for node filtering"""

    @SKIP_GRAPHVIZ
    def test_filter_node_basic(self):
        """Test basic node filtering"""
        app_setting = get_default_app_setting()
        app_setting['ignore_node_list'] = ['/node_src']
        group_setting = get_default_group_setting()
        manager = GraphManager(app_setting, group_setting)

        manager.load_graph_from_dot('./sample/rosgraph_nodeonly.dot')

        # /node_src should be filtered out
        assert not manager.graph.has_node('"/node_src"')

    @SKIP_GRAPHVIZ
    def test_filter_node_regex(self):
        """Test node filtering with regex pattern"""
        app_setting = get_default_app_setting()
        app_setting['ignore_node_list'] = ['/node_src.*']
        group_setting = get_default_group_setting()
        manager = GraphManager(app_setting, group_setting)

        manager.load_graph_from_dot('./sample/rosgraph_nodeonly.dot')

        # All nodes matching /node_src.* should be filtered out
        for node in manager.graph.nodes:
            assert not node.strip('"').startswith('/node_src')

    @SKIP_GRAPHVIZ
    def test_filter_node_empty_list(self):
        """Test that empty filter list doesn't remove nodes"""
        app_setting = get_default_app_setting()
        app_setting['ignore_node_list'] = []
        group_setting = get_default_group_setting()
        manager = GraphManager(app_setting, group_setting)

        manager.load_graph_from_dot('./sample/rosgraph_nodeonly.dot')

        assert len(manager.graph.nodes) > 0



class TestGraphManagerFilterTopic:
    """Tests for topic filtering"""

    @SKIP_GRAPHVIZ
    def test_filter_topic_basic(self):
        """Test basic topic filtering"""
        app_setting = get_default_app_setting()
        app_setting['ignore_topic_list'] = ['/topic_src']
        group_setting = get_default_group_setting()
        manager = GraphManager(app_setting, group_setting)

        manager.load_graph_from_dot('./sample/rosgraph_nodeonly.dot')

        # Edges with /topic_src should be filtered out
        for edge in manager.graph.edges:
            edge_data = manager.graph.edges[edge]
            if 'label' in edge_data:
                assert edge_data['label'].strip('"') != '/topic_src'

    @SKIP_GRAPHVIZ
    def test_filter_topic_regex(self):
        """Test topic filtering with regex pattern"""
        app_setting = get_default_app_setting()
        app_setting['ignore_topic_list'] = ['/topic_src.*']
        group_setting = get_default_group_setting()
        manager = GraphManager(app_setting, group_setting)

        manager.load_graph_from_dot('./sample/rosgraph_nodeonly.dot')

        # Edges with topics matching /topic_src.* should be filtered out
        for edge in manager.graph.edges:
            edge_data = manager.graph.edges[edge]
            if 'label' in edge_data:
                label = edge_data['label'].strip('"')
                assert not label.startswith('/topic_src')



class TestGraphManagerClearCaretPathDict:
    """Tests for clear_caret_path_dict method"""

    @SKIP_GRAPHVIZ
    def test_clear_caret_path_dict(self):
        """Test clearing CARET path dictionary"""
        app_setting = get_default_app_setting()
        group_setting = get_default_group_setting()
        manager = GraphManager(app_setting, group_setting)

        # Load to populate path dict
        manager.load_graph_from_caret('architecture.yaml')
        initial_count = len(manager.caret_path_dict)
        assert initial_count > 0

        # Clear and reload
        manager.clear_caret_path_dict()

        # Should have only the << CLEAR >> entry
        assert '<< CLEAR >>' in manager.caret_path_dict



class TestGraphManagerPostprocess:
    """Tests for load_graph_postprocess method"""

    @SKIP_GRAPHVIZ
    def test_postprocess_sets_node_positions(self):
        """Test that postprocess sets node positions"""
        app_setting = get_default_app_setting()
        group_setting = get_default_group_setting()
        manager = GraphManager(app_setting, group_setting)

        manager.load_graph_from_dot('./sample/rosgraph_nodeonly.dot')

        # All nodes should have pos attribute
        for node in manager.graph.nodes:
            assert 'pos' in manager.graph.nodes[node]

    @SKIP_GRAPHVIZ
    def test_postprocess_sets_node_colors(self):
        """Test that postprocess sets node colors"""
        app_setting = get_default_app_setting()
        group_setting = get_default_group_setting()
        manager = GraphManager(app_setting, group_setting)

        manager.load_graph_from_dot('./sample/rosgraph_nodeonly.dot')

        # All nodes should have color attribute
        for node in manager.graph.nodes:
            assert 'color' in manager.graph.nodes[node]



class TestGraphManagerDisplayUnconnectedNodes:
    """Tests for display_unconnected_nodes option"""

    @SKIP_GRAPHVIZ
    def test_display_unconnected_true(self):
        """Test with display_unconnected_nodes=True"""
        app_setting = get_default_app_setting()
        app_setting['display_unconnected_nodes'] = True
        group_setting = get_default_group_setting()
        manager = GraphManager(app_setting, group_setting)

        manager.load_graph_from_caret('architecture.yaml')

        # Should have nodes even if they're unconnected
        assert len(manager.graph.nodes) > 0

    @SKIP_GRAPHVIZ
    def test_display_unconnected_false(self):
        """Test with display_unconnected_nodes=False"""
        app_setting = get_default_app_setting()
        app_setting['display_unconnected_nodes'] = False
        group_setting = get_default_group_setting()
        manager = GraphManager(app_setting, group_setting)

        manager.load_graph_from_caret('architecture.yaml')

        # Isolated nodes should be removed
        isolated_nodes = list(nx.isolates(manager.graph))
        assert len(isolated_nodes) == 0
