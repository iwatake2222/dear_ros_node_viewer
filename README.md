# Dear ROS Node Viewer
ROS2 Node Viewer using Dear PyGui 

## How to Run
```sh
sudo apt install graphviz graphviz-dev
pip3 install -r requirements.txt
python3 -m dear_ros_node_viewer --architecture_yaml_file architecture.yaml

```


## Commands for Development
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

## To Do
- [x] Align center
- [ ] Reset layout
    - [ ] impl
    - [x] menu
- [ ] Save/Load layout
    - [ ] impl
    - [x] menu
- [x] +/- font size
    - [x] impl
    - [x] menu
- [x] Omitted name
    - [x] full / first + last / last only
    - [x] impl
    - [x] menu
- [ ] Read dot file
- [ ] Current ROS node graph


