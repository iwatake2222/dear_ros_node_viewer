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

from src.dear_ros_node_viewer.caret2networkx import caret2networkx, quote_name


def test_quote_name():
    name = 'abc'
    new_name = quote_name(name)
    assert new_name == '"abc"'


def test_caret2networkx():
    graph = caret2networkx('architecture.yaml')
    assert(graph.has_node('"/node_src"'))

    graph = caret2networkx('architecture.yaml', target_path='target_path_0')
    assert(graph.has_node('"/node_src"'))
