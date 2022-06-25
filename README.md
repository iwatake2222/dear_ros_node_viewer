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
- Others
    - [ ] Save/Load layout
    - [ ] Add sample data
    - [ ] Modify setting file
        - layout (horizontal, vertical)
        - fix layout
        - fix color
- Support more format
    - [ ] Graph from dot file
    - [ ] Graph from current ROS status
- Cooperation with CARET
    - [ ] Display executor and callback group
        - from architecture file
    - [ ] Display trigger of publishment
        - from architecture file
        - subscribe, timer(with period time), unknown
- More Cooperation with CARET
    - [ ] Display frequency of publishment and callback
        - need extra data created by CARET analysis
    - [ ] Edit architecture file
