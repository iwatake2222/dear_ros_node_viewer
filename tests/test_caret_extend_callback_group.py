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
Test caret_extend_callback_group module
"""
import networkx as nx

from src.dear_ros_node_viewer.caret_extend_callback_group import (
    create_dict_cbgroup2executor,
    create_callback_detail,
    create_callback_group_list,
    create_dict_node_callbackgroup,
    extend_callback_group,
)


class TestCreateDictCbgroup2Executor:
    """Tests for create_dict_cbgroup2executor function"""

    def test_basic(self):
        """Test basic executor mapping"""
        yml = {
            'executors': [
                {
                    'executor_name': 'executor_0',
                    'executor_type': 'multi_threaded_executor',
                    'callback_group_names': ['/node_a/callback_group_0']
                }
            ]
        }

        dict_cbgroup2executor, dict_cbgroup2color = create_dict_cbgroup2executor(yml)

        assert '/node_a/callback_group_0' in dict_cbgroup2executor
        assert 'executor_0' in dict_cbgroup2executor['/node_a/callback_group_0']
        assert '/node_a/callback_group_0' in dict_cbgroup2color

    def test_multiple_callback_groups(self):
        """Test executor with multiple callback groups"""
        yml = {
            'executors': [
                {
                    'executor_name': 'executor_0',
                    'executor_type': 'multi_threaded_executor',
                    'callback_group_names': [
                        '/node_a/callback_group_0',
                        '/node_b/callback_group_0'
                    ]
                }
            ]
        }

        dict_cbgroup2executor, dict_cbgroup2color = create_dict_cbgroup2executor(yml)

        assert '/node_a/callback_group_0' in dict_cbgroup2executor
        assert '/node_b/callback_group_0' in dict_cbgroup2executor
        # Multiple callback groups should have non-white color
        color = dict_cbgroup2color['/node_a/callback_group_0']
        assert len(color) == 3

    def test_single_callback_group_white_color(self):
        """Test that single callback group gets white color"""
        yml = {
            'executors': [
                {
                    'executor_name': 'executor_0',
                    'executor_type': 'single_threaded_executor',
                    'callback_group_names': ['/node_a/callback_group_0']
                }
            ]
        }

        _, dict_cbgroup2color = create_dict_cbgroup2executor(yml)

        assert dict_cbgroup2color['/node_a/callback_group_0'] == [255, 255, 255]

    def test_multiple_executors(self):
        """Test multiple executors"""
        yml = {
            'executors': [
                {
                    'executor_name': 'executor_0',
                    'executor_type': 'multi_threaded_executor',
                    'callback_group_names': ['/node_a/callback_group_0']
                },
                {
                    'executor_name': 'executor_1',
                    'executor_type': 'single_threaded_executor',
                    'callback_group_names': ['/node_b/callback_group_0']
                }
            ]
        }

        dict_cbgroup2executor, _ = create_dict_cbgroup2executor(yml)

        assert 'executor_0' in dict_cbgroup2executor['/node_a/callback_group_0']
        assert 'executor_1' in dict_cbgroup2executor['/node_b/callback_group_0']


class TestCreateCallbackDetail:
    """Tests for create_callback_detail function"""

    def test_subscription_callback(self):
        """Test creating detail for subscription callback"""
        callbacks = [
            {
                'callback_name': '/node_a/callback_0',
                'callback_type': 'subscription_callback',
                'topic_name': '/topic_1'
            }
        ]

        result = create_callback_detail(callbacks, '/node_a/callback_0')

        assert result is not None
        assert result['callback_name'] == '/node_a/callback_0'
        assert result['callback_type'] == 'sub'
        assert result['description'] == '/topic_1'

    def test_timer_callback(self):
        """Test creating detail for timer callback"""
        callbacks = [
            {
                'callback_name': '/node_a/callback_0',
                'callback_type': 'timer_callback',
                'period_ns': 20000000  # 20ms
            }
        ]

        result = create_callback_detail(callbacks, '/node_a/callback_0')

        assert result is not None
        assert result['callback_type'] == 'timer'
        assert '20.0ms' in result['description']

    def test_callback_not_found(self):
        """Test handling of non-existent callback"""
        callbacks = [
            {
                'callback_name': '/node_a/callback_0',
                'callback_type': 'subscription_callback',
                'topic_name': '/topic_1'
            }
        ]

        result = create_callback_detail(callbacks, '/nonexistent/callback')

        assert result is None

    def test_unknown_callback_type(self):
        """Test handling of unknown callback type"""
        callbacks = [
            {
                'callback_name': '/node_a/callback_0',
                'callback_type': 'unknown_callback_type',
            }
        ]

        result = create_callback_detail(callbacks, '/node_a/callback_0')

        assert result is not None
        assert result['callback_type'] == 'unknown_callback_type'


class TestCreateCallbackGroupList:
    """Tests for create_callback_group_list function"""

    def test_basic(self):
        """Test creating callback group list"""
        node = {
            'node_name': '/node_a',
            'callback_groups': [
                {
                    'callback_group_name': '/node_a/callback_group_0',
                    'callback_group_type': 'mutually_exclusive',
                    'callback_names': ['/node_a/callback_0']
                }
            ],
            'callbacks': [
                {
                    'callback_name': '/node_a/callback_0',
                    'callback_type': 'subscription_callback',
                    'topic_name': '/topic_1'
                }
            ]
        }
        dict_cbgroup2executor = {'/node_a/callback_group_0': 'executor_0, multi_'}
        dict_cbgroup2color = {'/node_a/callback_group_0': [255, 255, 255]}

        result = create_callback_group_list(node, dict_cbgroup2executor, dict_cbgroup2color)

        assert len(result) == 1
        assert result[0]['callback_group_name'] == '/node_a/callback_group_0'
        assert len(result[0]['callback_detail_list']) == 1

    def test_no_callback_groups(self):
        """Test node without callback_groups"""
        node = {
            'node_name': '/node_a',
        }
        dict_cbgroup2executor = {}
        dict_cbgroup2color = {}

        result = create_callback_group_list(node, dict_cbgroup2executor, dict_cbgroup2color)

        assert result == []

    def test_no_callbacks(self):
        """Test node without callbacks"""
        node = {
            'node_name': '/node_a',
            'callback_groups': [
                {
                    'callback_group_name': '/node_a/callback_group_0',
                    'callback_group_type': 'mutually_exclusive',
                    'callback_names': []
                }
            ]
        }
        dict_cbgroup2executor = {}
        dict_cbgroup2color = {}

        result = create_callback_group_list(node, dict_cbgroup2executor, dict_cbgroup2color)

        assert result == []

    def test_callback_group_not_in_executor(self):
        """Test callback group not registered with any executor"""
        node = {
            'node_name': '/node_a',
            'callback_groups': [
                {
                    'callback_group_name': '/node_a/callback_group_0',
                    'callback_group_type': 'mutually_exclusive',
                    'callback_names': ['/node_a/callback_0']
                }
            ],
            'callbacks': [
                {
                    'callback_name': '/node_a/callback_0',
                    'callback_type': 'subscription_callback',
                    'topic_name': '/topic_1'
                }
            ]
        }
        dict_cbgroup2executor = {}  # No executor mapping
        dict_cbgroup2color = {}

        result = create_callback_group_list(node, dict_cbgroup2executor, dict_cbgroup2color)

        # Should skip callback groups not in executor
        assert result == []


class TestCreateDictNodeCallbackgroup:
    """Tests for create_dict_node_callbackgroup function"""

    def test_basic(self):
        """Test creating node to callback group dictionary"""
        yml = {
            'executors': [
                {
                    'executor_name': 'executor_0',
                    'executor_type': 'multi_threaded_executor',
                    'callback_group_names': ['/node_a/callback_group_0']
                }
            ],
            'nodes': [
                {
                    'node_name': '/node_a',
                    'callback_groups': [
                        {
                            'callback_group_name': '/node_a/callback_group_0',
                            'callback_group_type': 'mutually_exclusive',
                            'callback_names': ['/node_a/callback_0']
                        }
                    ],
                    'callbacks': [
                        {
                            'callback_name': '/node_a/callback_0',
                            'callback_type': 'subscription_callback',
                            'topic_name': '/topic_1'
                        }
                    ]
                }
            ]
        }

        result = create_dict_node_callbackgroup(yml)

        assert '"/node_a"' in result
        assert len(result['"/node_a"']) == 1


class TestExtendCallbackGroup:
    """Tests for extend_callback_group function"""

    def test_extend_callback_group_basic(self):
        """Test extending graph with callback group info"""
        graph = nx.MultiDiGraph()
        graph.add_node('"/node_src"')
        graph.add_node('"/node_dst"')

        result = extend_callback_group('architecture.yaml', graph)

        # All nodes should have callback_group_list attribute
        for node in result.nodes:
            assert 'callback_group_list' in result.nodes[node]

    def test_extend_callback_group_preserves_nodes(self):
        """Test that extending preserves existing nodes"""
        graph = nx.MultiDiGraph()
        graph.add_node('"/node_src"')
        graph.add_node('"/node_dst"')
        graph.add_edge('"/node_src"', '"/node_dst"')

        result = extend_callback_group('architecture.yaml', graph)

        assert result.has_node('"/node_src"')
        assert result.has_node('"/node_dst"')
        assert result.has_edge('"/node_src"', '"/node_dst"')

    def test_extend_callback_group_returns_graph(self):
        """Test that function returns a graph"""
        graph = nx.MultiDiGraph()
        graph.add_node('"/node_src"')

        result = extend_callback_group('architecture.yaml', graph)

        assert isinstance(result, nx.MultiDiGraph)
