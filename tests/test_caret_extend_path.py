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
Test caret_extend_path module
"""
import os
import tempfile
import pytest

from src.dear_ros_node_viewer.caret_extend_path import get_path_dict


class TestGetPathDict:
    """Tests for get_path_dict function"""

    def test_get_path_dict_basic(self):
        """Test basic path dictionary extraction"""
        path_dict = get_path_dict('architecture.yaml')

        assert isinstance(path_dict, dict)
        assert len(path_dict) > 0

    def test_get_path_dict_has_target_paths(self):
        """Test that path dictionary contains expected paths"""
        path_dict = get_path_dict('architecture.yaml')

        # architecture.yaml has target_path_0, target_path_1, target_path_2
        assert 'target_path_0' in path_dict
        assert 'target_path_1' in path_dict
        assert 'target_path_2' in path_dict

    def test_get_path_dict_node_list(self):
        """Test that path contains node list"""
        path_dict = get_path_dict('architecture.yaml')

        # Each path should have a list of nodes
        for path_name, node_list in path_dict.items():
            assert isinstance(node_list, list)
            assert len(node_list) > 0

    def test_get_path_dict_quoted_node_names(self):
        """Test that node names are properly quoted"""
        path_dict = get_path_dict('architecture.yaml')

        for path_name, node_list in path_dict.items():
            for node_name in node_list:
                # Node names should be quoted
                assert node_name.startswith('"')
                assert node_name.endswith('"')

    def test_get_path_dict_target_path_0_nodes(self):
        """Test specific nodes in target_path_0"""
        path_dict = get_path_dict('architecture.yaml')

        node_list = path_dict['target_path_0']
        # target_path_0 should contain: /node_src, /node_src_0, /node_sub3pub1, /node_dst
        assert '"/node_src"' in node_list
        assert '"/node_dst"' in node_list

    def test_get_path_dict_file_not_found(self):
        """Test error handling for non-existent file"""
        with pytest.raises(FileNotFoundError):
            get_path_dict('nonexistent_file.yaml')

    def test_get_path_dict_empty_named_paths(self):
        """Test handling of empty named_paths"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('named_paths: []\n')
            temp_path = f.name

        try:
            path_dict = get_path_dict(temp_path)
            assert path_dict == {}
        finally:
            os.unlink(temp_path)

    def test_get_path_dict_single_path(self):
        """Test handling of single path"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('''named_paths:
- path_name: single_path
  node_chain:
  - node_name: /node_a
    publish_topic_name: /topic_1
    subscribe_topic_name: UNDEFINED
  - node_name: /node_b
    publish_topic_name: UNDEFINED
    subscribe_topic_name: /topic_1
''')
            temp_path = f.name

        try:
            path_dict = get_path_dict(temp_path)
            assert 'single_path' in path_dict
            assert len(path_dict['single_path']) == 2
            assert '"/node_a"' in path_dict['single_path']
            assert '"/node_b"' in path_dict['single_path']
        finally:
            os.unlink(temp_path)

    def test_get_path_dict_preserves_order(self):
        """Test that node order is preserved in path"""
        path_dict = get_path_dict('architecture.yaml')

        # target_path_0: /node_src -> /node_src_0 -> /node_sub3pub1 -> /node_dst
        node_list = path_dict['target_path_0']
        src_idx = node_list.index('"/node_src"')
        dst_idx = node_list.index('"/node_dst"')

        # /node_src should come before /node_dst
        assert src_idx < dst_idx

    def test_get_path_dict_multiple_paths_independent(self):
        """Test that multiple paths are independent"""
        path_dict = get_path_dict('architecture.yaml')

        path_0 = path_dict['target_path_0']
        path_1 = path_dict['target_path_1']

        # Both paths should have /node_src and /node_dst but different intermediate nodes
        assert '"/node_src"' in path_0
        assert '"/node_src"' in path_1
        assert '"/node_dst"' in path_0
        assert '"/node_dst"' in path_1

        # path_0 has /node_src_0, path_1 has /node_src_1
        assert '"/node_src_0"' in path_0
        assert '"/node_src_1"' in path_1
