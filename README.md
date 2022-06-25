# Dear Ros Node Viewer
ROS2 node viewer using Dear PyGui 

```sh
sudo apt install graphviz graphviz-dev
pip3 install -r requirements.txt
python3 -m dear_ros_node_viewer --architecture_yaml_file architecture.yaml

```


## Commands for development
```sh
### Debug ###
python3 main.py --architecture_yaml_file architecture.yaml

### Install ###
pip3 install ./
# python3 setup.py sdist
# pip3 install dist/dear_ros_node_viewer-1.0.tar.gz

### Test ###
python3 -m pytest --doctest-modules -v --cov=./dear_ros_node_viewer
python3 -m pylint ./dear_ros_node_viewer
```
