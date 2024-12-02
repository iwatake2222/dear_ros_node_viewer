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
# limitations under the License.s
"""
Utility class for polling ROS statistics from running ROS graph

Note
----
Reference: /opt/ros/galactic/lib/python3.8/site-packages/rqt_graph/rosgraph2_impl.py
"""

import threading
import time
import networkx as nx
import matplotlib.pyplot as plt
from .logger_factory import LoggerFactory

# Note: Use try-except to avoid error at pytest in GitHub Actions (todo)
try:
  import rclpy
  from rclpy.executors import MultiThreadedExecutor
  from rqt_graph.rosgraph2_impl import Graph
  from rqt_graph.dotcode import RosGraphDotcodeGenerator
  from qt_dotgraph.pydotfactory import PydotFactory
except ImportError:
  pass

logger = LoggerFactory.create(__name__)


class Ros2Networkx():
  """Utility class for polling ROS statistics from running ROS graph"""
  def __init__(self, node_name='Ros2Networkx'):
    rclpy.init()
    self.node_name_ = node_name
    self.node_ = rclpy.create_node(node_name)
    self.executor_ = MultiThreadedExecutor()
    self.executor_.add_node(self.node_)
    self.thread_ = threading.Thread(target=self.node_loop)
    self.thread_.start()

  def node_loop(self):
    """thread main function"""
    while rclpy.ok():
      logger.info('Analyzing...')
      self.executor_.spin_once(timeout_sec=1.0)

  def save_graph(self, filename: str = None) -> str:
    """save dot graph"""
    time.sleep(5)
    graph = Graph(self.node_)
    graph.set_node_stale(5.0)
    logger.info('graph.update start')
    graph.update()
    logger.info('graph.update done')

    dotcode_generator = RosGraphDotcodeGenerator(self.node_)
    logger.info('generate_dotcode start')
    dotcode = dotcode_generator.generate_dotcode(
          rosgraphinst=graph,
          ns_filter='-/rosbag2_recorder',
          topic_filter='',
          # graph_mode='node_topic',
          graph_mode='node_node',
          hide_single_connection_topics=False,
          hide_dead_end_topics=True,
          cluster_namespaces_level=0,
          # accumulate_actions=accumulate_actions,
          dotcode_factory=PydotFactory(),
          # orientation=orientation,
          quiet=True,
          unreachable=True,
          hide_tf_nodes=True,
          hide_dynamic_reconfigure=True
          )
    logger.info('generate_dotcode done')

    if filename:
      with open(filename, encoding='UTF8', mode='w') as dot_file:
        dot_file.write(dotcode)

    return dotcode

  def get_graph(self) -> nx.classes.digraph.DiGraph:
    """get graph as NetworkX"""
    _ = self.save_graph('temp.dot')
    graph = nx.DiGraph(nx.nx_pydot.read_dot('temp.dot'))
    for node in graph.nodes:
      if self.node_name_ in graph.nodes[node]['label']:
        node_observer = node
        break
    graph.remove_node(node_observer)
    return graph

  def shutdown(self):
    """shutdown thread"""
    self.node_.destroy_node()
    rclpy.shutdown()


def main():
  """test code"""
  node_name = 'Ros2Networkx'
  ros2networkx = Ros2Networkx(node_name=node_name)
  graph = ros2networkx.get_graph()
  ros2networkx.shutdown()

  pos = nx.spring_layout(graph)
  nx.draw_networkx(graph, pos)
  plt.show()


if __name__ == '__main__':
  main()
