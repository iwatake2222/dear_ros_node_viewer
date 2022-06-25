from setuptools import setup, find_packages

setup(
    name="dear_ros_node_viewer",
    version='0.0.1',
    description='ROS2 node viewer using Dear PyGui ',
    author='takeshi-iwanari',
    author_email='takeshi.iwanari@tier4.jp',
    url='https://github.com/takeshi-iwanari/dear_ros_node_viewer',
    license='Apache License 2.0',
    tests_require=['pytest'],
    packages=find_packages(),
    entry_points="""
      [console_scripts]
      dear_ros_node_viewer=dear_ros_node_viewer.__main__:main
    """,
)
