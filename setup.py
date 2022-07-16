"""setup script"""
from setuptools import setup, find_packages
from os import path
import re

package_name = 'dear_ros_node_viewer'
root_dir = path.abspath(path.dirname(__file__))

with open(path.join(root_dir, package_name, '__init__.py')) as f:
    init_text = f.read()
    version = re.search(r'__version__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    license = re.search(r'__license__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    author = re.search(r'__author__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    author_email = re.search(r'__author_email__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    url = re.search(r'__url__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)

assert version
assert license
assert author
assert author_email
assert url

with open("README.md", encoding='utf8') as f:
    long_description = f.read()

setup(
    name="dear_ros_node_viewer",
    version=version,
    description='ROS2 node viewer using Dear PyGui ',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='ros ros2 rqt_graph node-editor dearpygui',
    author=author,
    author_email=author_email,
    url=url,
    project_urls={
        "Source":
        "https://github.com/takeshi-iwanari/dear_ros_node_viewer",
        "Tracker":
        "https://github.com/takeshi-iwanari/dear_ros_node_viewer/issues",
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
        'Topic :: Scientific/Engineering :: Visualization',
        'Framework :: Robot Framework :: Tool',
    ],
    license=license,
    python_requires=">=3.7",
    install_requires=[
        "numpy",
        "matplotlib",
        "pydot",
        "networkx",
        "dearpygui",
        "graphviz",
        "pygraphviz",
        "pyyaml",
    ],
    # tests_require=['pytest'],
    packages=find_packages(),
    platforms=["linux", "unix"],
    package_data={"dear_ros_node_viewer": ["setting.json", "font/*/*.ttf"]},
    entry_points="""
        [console_scripts]
        dear_ros_node_viewer=dear_ros_node_viewer.__main__:main
    """,
)
