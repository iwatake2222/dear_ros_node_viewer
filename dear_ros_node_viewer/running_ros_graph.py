import threading
import rclpy
from rclpy.executors import MultiThreadedExecutor
from rqt_graph.rosgraph2_impl import Graph
from rqt_graph.dotcode import RosGraphDotcodeGenerator
from qt_dotgraph.pydotfactory import PydotFactory


class RunningRosGraph():
    """
    Utility class for polling ROS statistics from running ROS graph.

    Note
    ----
    Reference: /opt/ros/galactic/lib/python3.8/site-packages/rqt_graph/rosgraph2_impl.py
    """
    def __init__(self, node_name='RunningRosGraph'):
        try:
            rclpy.shutdown()
        except:
            pass

        rclpy.init()

        self.node_ = rclpy.create_node(node_name)

        self.executor_ = MultiThreadedExecutor()
        self.executor_.add_node(self.node_)

        self.thread_ = threading.Thread(target=self.node_loop)
        self.thread_.start()

    def node_loop(self):
        while rclpy.ok():
            self.executor_.spin_once(timeout_sec=1.0)

    def get_graph(self, filename=None):
        graph = Graph(self.node_)
        graph.set_node_stale(5.0)
        graph.update()

        dotcode_generator = RosGraphDotcodeGenerator(self.node_)
        dotcode = dotcode_generator.generate_dotcode(
                    rosgraphinst=graph,
                    ns_filter='',
                    topic_filter='',
                    # graph_mode='node_topic',
                    graph_mode='node_node',
                    hide_single_connection_topics=True,
                    hide_dead_end_topics=True,
                    cluster_namespaces_level=1,
                    # accumulate_actions=accumulate_actions,
                    dotcode_factory=PydotFactory(),
                    # orientation=orientation,
                    quiet=True,
                    unreachable=True,
                    group_tf_nodes=True,
                    hide_tf_nodes=True,
                    # group_image_nodes=group_image_nodes,
                    hide_dynamic_reconfigure=True
                    )

        if filename:
            with open(filename, 'w') as f:
                f.write(dotcode)
        
        return dotcode
    
    def shutdown(self):
        self.node_.destroy_node()
        rclpy.shutdown()


def main():
    running_ros_graph = RunningRosGraph(node_name='RunningRosGraph')
    dotcode = running_ros_graph.get_graph('graph.dot')
    running_ros_graph.shutdown()

    import networkx as nx
    import matplotlib.pyplot as plt
    graph = nx.DiGraph(nx.nx_pydot.read_dot('graph.dot'))
    pos = nx.spring_layout(graph)
    nx.draw_networkx(graph, pos)
    plt.show()


if __name__ == '__main__':
    main()