<<<<<<< HEAD
# SVIn-Plus
=======
SVIN+ is a tightly coupled Sonar-Visual-Inertial-Pressure-DVL and loosely coupled 3D Sonar formulation of Simultaneous Localization and Mapping (SLAM)
algorithm for real-time underwater navigation. The package contains two modules:

1. okvis_ros: Adaption of OKVIS (<https://github.com/ethz-asl/okvis_ros>) to fuse Pressure, DVL information in the tightly
   coupled formulation and 3D Sonar pose in a loosely coupled manner.
2. pose_graph:  Loop-closing module to enable real-time loop detection and pose-graph optimization based on the
   bag-of-binary-words library DBoW2.

### Setup Instructions ###

The setup instructions are tested on Ubuntu 24.04 with ROS Jazzy.

**Prerequisites**

- [Glog](http://rpg.ifi.uzh.ch/docs/glog.html), [Gflags](https://gflags.github.io/gflags/)
- [BLAS](https://www.netlib.org/blas/), [LAPACK](https://www.netlib.org/lapack/)
- [OpenCV](https://github.com/opencv/opencv) >= 3.4
- [Suitesparse](https://people.engr.tamu.edu/davis/suitesparse.html)
- [ceres-solver](https://github.com/ceres-solver/ceres-solver/tree/master)
- [Brisk](https://ieeexplore.ieee.org/document/6126542)
- [ROS2 Jazzy](https://docs.ros.org/en/jazzy/index.html)

Please follow [installation page](install.md) for detailed instructions on building SVIN.

### Running the project ###

ToDo

### !!!Note !!!: Any changes in config/launch files are not reflected unless you build the repo again. All the config/launch files are saved inside install folder and will be updated as part of build. ###

To build again use

```bash
colcon build  --event-handlers console_direct+
```

To install

```bash
sudo apt install pipx
pipx install rosbags
```

## Running on Datasets with launch files ##

Run the launch file for IROS 2026 Dataset:

```bash
source install/setup.bash
ros2 launch okvis_ros svin_aqua2_A6_uw.launch.py
```


