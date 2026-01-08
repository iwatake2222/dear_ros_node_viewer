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
Test caret2networkx module
"""
import os
import tempfile
import pytest
import networkx as nx

from src.dear_ros_node_viewer.caret2networkx import (
    caret2networkx,
    quote_name,
    parse_all_graph,
    parse_target_path,
    make_graph_from_topic_association,
)


class TestQuoteName:
    """Tests for quote_name function"""

    def test_quote_name_basic(self):
        """Test basic name quoting"""
        assert quote_name('abc') == '"abc"'

    def test_quote_name_with_slash(self):
        """Test name quoting with slash (ROS node name format)"""
        assert quote_name('/node_name') == '"/node_name"'

    def test_quote_name_empty(self):
        """Test empty string quoting"""
        assert quote_name('') == '""'

    def test_quote_name_special_chars(self):
        """Test name with special characters"""
        assert quote_name('/ns/node_123') == '"/ns/node_123"'


class TestParseAllGraph:
    """Tests for parse_all_graph function"""

    def test_parse_all_graph_basic(self):
        """Test parsing all graph from YAML structure"""
        yml = {
            'nodes': [
                {
                    'node_name': '/node_a',
                    'publishes': [{'topic_name': '/topic_1'}],
                    'subscribes': [{'topic_name': '/topic_2'}]
                },
                {
                    'node_name': '/node_b',
                    'publishes': [{'topic_name': '/topic_2'}],
                }
            ]
        }
        node_name_list = []
        topic_pub_dict = {}
        topic_sub_dict = {}

        parse_all_graph(yml, node_name_list, topic_pub_dict, topic_sub_dict)

        assert '"/node_a"' in node_name_list
        assert '"/node_b"' in node_name_list
        assert '/topic_1' in topic_pub_dict
        assert '/topic_2' in topic_sub_dict
        assert '"/node_a"' in topic_pub_dict['/topic_1']

    def test_parse_all_graph_no_publishes(self):
        """Test parsing node without publishes"""
        yml = {
            'nodes': [
                {
                    'node_name': '/node_a',
                    'subscribes': [{'topic_name': '/topic_1'}]
                }
            ]
        }
        node_name_list = []
        topic_pub_dict = {}
        topic_sub_dict = {}

        parse_all_graph(yml, node_name_list, topic_pub_dict, topic_sub_dict)

        assert '"/node_a"' in node_name_list
        assert len(topic_pub_dict) == 0
        assert '/topic_1' in topic_sub_dict

    def test_parse_all_graph_no_subscribes(self):
        """Test parsing node without subscribes"""
        yml = {
            'nodes': [
                {
                    'node_name': '/node_a',
                    'publishes': [{'topic_name': '/topic_1'}]
                }
            ]
        }
        node_name_list = []
        topic_pub_dict = {}
        topic_sub_dict = {}

        parse_all_graph(yml, node_name_list, topic_pub_dict, topic_sub_dict)

        assert '"/node_a"' in node_name_list
        assert '/topic_1' in topic_pub_dict
        assert len(topic_sub_dict) == 0

    def test_parse_all_graph_multiple_publishers(self):
        """Test multiple nodes publishing to same topic"""
        yml = {
            'nodes': [
                {
                    'node_name': '/node_a',
                    'publishes': [{'topic_name': '/topic_1'}],
                },
                {
                    'node_name': '/node_b',
                    'publishes': [{'topic_name': '/topic_1'}],
                }
            ]
        }
        node_name_list = []
        topic_pub_dict = {}
        topic_sub_dict = {}

        parse_all_graph(yml, node_name_list, topic_pub_dict, topic_sub_dict)

        assert len(topic_pub_dict['/topic_1']) == 2
        assert '"/node_a"' in topic_pub_dict['/topic_1']
        assert '"/node_b"' in topic_pub_dict['/topic_1']


class TestParseTargetPath:
    """Tests for parse_target_path function"""

    def test_parse_target_path_basic(self):
        """Test parsing target path from YAML structure"""
        yml = {
            'named_paths': [
                {
                    'path_name': 'path_0',
                    'node_chain': [
                        {
                            'node_name': '/node_a',
                            'publish_topic_name': '/topic_1',
                            'subscribe_topic_name': 'UNDEFINED'
                        },
                        {
                            'node_name': '/node_b',
                            'publish_topic_name': 'UNDEFINED',
                            'subscribe_topic_name': '/topic_1'
                        }
                    ]
                }
            ]
        }
        node_name_list = []
        topic_pub_dict = {}
        topic_sub_dict = {}

        parse_target_path(yml, node_name_list, topic_pub_dict, topic_sub_dict)

        assert '"/node_a"' in node_name_list
        assert '"/node_b"' in node_name_list
        assert '/topic_1' in topic_pub_dict
        assert '/topic_1' in topic_sub_dict

    def test_parse_target_path_empty(self):
        """Test parsing empty named_paths"""
        yml = {'named_paths': []}
        node_name_list = []
        topic_pub_dict = {}
        topic_sub_dict = {}

        parse_target_path(yml, node_name_list, topic_pub_dict, topic_sub_dict)

        assert len(node_name_list) == 0


class TestMakeGraphFromTopicAssociation:
    """Tests for make_graph_from_topic_association function"""

    def test_make_graph_basic(self):
        """Test creating graph from topic associations"""
        topic_pub_dict = {'/topic_1': ['"/node_a"']}
        topic_sub_dict = {'/topic_1': ['"/node_b"']}

        graph = make_graph_from_topic_association(topic_pub_dict, topic_sub_dict)

        assert graph.has_node('"/node_a"')
        assert graph.has_node('"/node_b"')
        assert graph.has_edge('"/node_a"', '"/node_b"')

    def test_make_graph_no_subscriber(self):
        """Test graph creation when topic has no subscriber"""
        topic_pub_dict = {'/topic_1': ['"/node_a"']}
        topic_sub_dict = {}

        graph = make_graph_from_topic_association(topic_pub_dict, topic_sub_dict)

        # Node should not be added if there's no subscriber
        assert not graph.has_node('"/node_a"')

    def test_make_graph_multiple_connections(self):
        """Test graph with multiple publishers and subscribers"""
        topic_pub_dict = {'/topic_1': ['"/node_a"', '"/node_b"']}
        topic_sub_dict = {'/topic_1': ['"/node_c"', '"/node_d"']}

        graph = make_graph_from_topic_association(topic_pub_dict, topic_sub_dict)

        # Each publisher should connect to each subscriber
        assert graph.has_edge('"/node_a"', '"/node_c"')
        assert graph.has_edge('"/node_a"', '"/node_d"')
        assert graph.has_edge('"/node_b"', '"/node_c"')
        assert graph.has_edge('"/node_b"', '"/node_d"')

    def test_make_graph_edge_label(self):
        """Test that edges have correct topic labels"""
        topic_pub_dict = {'/topic_1': ['"/node_a"']}
        topic_sub_dict = {'/topic_1': ['"/node_b"']}

        graph = make_graph_from_topic_association(topic_pub_dict, topic_sub_dict)

        edge_data = graph.get_edge_data('"/node_a"', '"/node_b"')
        assert edge_data is not None
        assert edge_data[0]['label'] == '/topic_1'


class TestCaret2Networkx:
    """Tests for caret2networkx function"""

    def test_caret2networkx_all_graph(self):
        """Test loading architecture.yaml with all_graph mode"""
        graph = caret2networkx('architecture.yaml')
        assert graph.has_node('"/node_src"')
        assert graph.has_node('"/node_dst"')
        assert isinstance(graph, nx.MultiDiGraph)

    def test_caret2networkx_target_path(self):
        """Test loading architecture.yaml with target_path mode"""
        graph = caret2networkx('architecture.yaml', target_path='target_path_0')
        assert graph.has_node('"/node_src"')
        assert graph.has_node('"/node_dst"')

    def test_caret2networkx_display_unconnected(self):
        """Test loading with display_unconnected_nodes option"""
        graph = caret2networkx('architecture.yaml', display_unconnected_nodes=True)
        # All nodes should be present even if unconnected
        assert len(graph.nodes) >= 1

    def test_caret2networkx_file_not_found(self):
        """Test error handling for non-existent file"""
        with pytest.raises(FileNotFoundError):
            caret2networkx('nonexistent_file.yaml')

    def test_caret2networkx_invalid_yaml(self):
        """Test error handling for invalid YAML file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('invalid: yaml: content: [')
            temp_path = f.name

        try:
            with pytest.raises(Exception):
                caret2networkx(temp_path)
        finally:
            os.unlink(temp_path)

    def test_caret2networkx_empty_nodes(self):
        """Test handling YAML with empty nodes list"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('nodes: []\n')
            temp_path = f.name

        try:
            graph = caret2networkx(temp_path)
            assert len(graph.nodes) == 0
        finally:
            os.unlink(temp_path)

    def test_caret2networkx_returns_multidigraph(self):
        """Test that function returns MultiDiGraph (allows multiple edges)"""
        graph = caret2networkx('architecture.yaml')
        assert isinstance(graph, nx.MultiDiGraph)
