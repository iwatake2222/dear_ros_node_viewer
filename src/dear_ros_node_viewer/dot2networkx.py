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
Function to create NetworkX object from dot graph file (rosgraph.dot)
"""

from __future__ import annotations
import networkx as nx
import matplotlib.pyplot as plt

from .logger_factory import LoggerFactory
from .caret2networkx import make_graph_from_topic_association

logger = LoggerFactory.create(__name__)


def dot2networkx_nodeonly(graph_org: nx.classes.digraph.DiGraph,
              ignore_unconnected=True) -> nx.classes.digraph.DiGraph:
  """Create NetworkX Object from dot graph file (nodes only) by rqt_graph"""
  graph = nx.MultiDiGraph()
  for node_org in graph_org.nodes:
    if 'label' not in graph_org.nodes[node_org]:
      continue
    label = graph_org.nodes[node_org]['label']
    if not ignore_unconnected:
      graph.add_node(label)

  for edge in graph_org.edges:
    if 'label' not in graph_org.nodes[edge[0]] or 'label' not in graph_org.nodes[edge[1]] or 'label' not in graph_org.edges[edge]:
      continue
    node_pub = graph_org.nodes[edge[0]]['label']
    node_sub = graph_org.nodes[edge[1]]['label']
    label = graph_org.edges[edge]['label']
    graph.add_edge(node_pub, node_sub, label=label)

  return graph


def dot2networkx_nodetopic(graph_org: nx.classes.digraph.DiGraph) -> nx.classes.digraph.DiGraph:
  """Create NetworkX Object from dot graph file (nodes / topics) by rqt_graph"""

  # "/topic_0": ["/node_0", ], <- publishers of /topic_0 are ["/node_0", ] #
  topic_pub_dict: dict[str, list[str]] = {}

  # "/topic_0": ["/node_1", ], <- subscribers of /topic_0 are ["/node_1", ] #
  topic_sub_dict: dict[str, list[str]] = {}

  for edge in graph_org.edges:
    src = graph_org.nodes[edge[0]]
    dst = graph_org.nodes[edge[1]]
    if not ('label' in src and 'label' in dst and 'shape' in src and 'shape' in dst):
      continue
    src_name = src['label']
    dst_name = dst['label']
    src_is_node = bool(src['shape'] == 'ellipse')
    dst_is_node = bool(dst['shape'] == 'ellipse')

    if src_is_node is True and dst_is_node is False:
      if dst_name in topic_pub_dict:
        topic_pub_dict[dst_name].append(src_name)
      else:
        topic_pub_dict[dst_name] = [src_name]
    elif src_is_node is False and dst_is_node is True:
      if src_name in topic_sub_dict:
        topic_sub_dict[src_name].append(dst_name)
      else:
        topic_sub_dict[src_name] = [dst_name]

  graph = make_graph_from_topic_association(topic_pub_dict, topic_sub_dict)

  return graph


def dot2networkx(filename: str, ignore_unconnected=True) -> nx.classes.digraph.DiGraph:
  """Function to create NetworkX object from dot graph file (rosgraph.dot)"""
  graph_org = nx.MultiDiGraph(nx.nx_pydot.read_dot(filename))

  is_node_only = True
  for node_org in graph_org.nodes:
    if 'shape' in graph_org.nodes[node_org]:
      if graph_org.nodes[node_org]['shape'] == 'box':
        is_node_only = False
        break

  if is_node_only:
    graph = dot2networkx_nodeonly(graph_org, ignore_unconnected)
  else:
    graph = dot2networkx_nodetopic(graph_org)

  logger.info('len(connected_nodes) = %d', len(graph.nodes))

  return graph


if __name__ == '__main__':
  def local_main():
    """main function for this file"""
    graph = dot2networkx('rosgraph_nodeonly.dot')
    pos = nx.spring_layout(graph)
    # pos = nx.circular_layout(graph)
    nx.draw_networkx(graph, pos)
    plt.show()

  local_main()
