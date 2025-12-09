FROM ros:jazzy

ARG USERNAME=theseus
ARG USER_UID=1000
ARG USER_GID=$USER_UID

ARG DEBIAN_FRONTEND=noninteractive

# Rename default user
ARG OLD_USERNAME=ubuntu
RUN usermod --login $USERNAME --move-home --home /home/$USERNAME $OLD_USERNAME\
    && groupmod --new-name $USERNAME $OLD_USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

RUN apt-get update && apt-get upgrade -y
RUN apt-get update && apt-get install -y python3-pip
ENV SHELL=/bin/bash

# ********************************************************
# * Anything else you want to do like clean up goes here *
# ********************************************************

# Install alternative RMW for better performance
RUN apt-get update && apt-get install -y ros-${ROS_DISTRO}-rmw-cyclonedds-cpp
RUN apt-get update && apt-get install -y ros-${ROS_DISTRO}-rmw-zenoh-cpp
ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# Dependencies for Velodyne
RUN apt-get update && apt-get install -y \
    libpcl-dev \
    ros-${ROS_DISTRO}-pcl-ros \
    ros-${ROS_DISTRO}-diagnostic-updater \
    ros-${ROS_DISTRO}-diagnostic-msgs \
    ros-${ROS_DISTRO}-sensor-msgs \
    ros-${ROS_DISTRO}-tf2 \
    ros-${ROS_DISTRO}-tf2-ros \
    ros-${ROS_DISTRO}-angles \
    ros-${ROS_DISTRO}-ament-index-cpp

RUN apt-get update && apt-get install -y \
    libpcap-dev \
    libyaml-cpp-dev \
    libboost-dev

RUN apt-get update && apt-get install -y ros-${ROS_DISTRO}-rviz2

ENV RCUTILS_COLORIZED_OUTPUT=1
USER ${USERNAME}
RUN mkdir -p /home/${USERNAME}/ws/src

WORKDIR /home/${USERNAME}/ws

# Add user to video group to allow access to webcams and dialout for serial devices
RUN sudo usermod --append --groups video,dialout $USERNAME

RUN rosdep update && rosdep install --from-paths /home/${USERNAME}/ws/src --ignore-src -y && sudo chown -R $(whoami) /home/${USERNAME}/ws/

# Configure bashrc
RUN grep -qF 'TAG1' $HOME/.bashrc || echo 'source /opt/ros/${ROS_DISTRO}/setup.bash # TAG1' >> $HOME/.bashrc
RUN grep -qF 'TAG2' $HOME/.bashrc || echo 'source ~/ws/install/setup.bash # TAG2' >> $HOME/.bashrc

# Build Velodyne packages
RUN --mount=type=bind,source=velodyne,target=src/velodyne \
    /bin/bash -c "source /opt/ros/${ROS_DISTRO}/setup.bash; colcon build --symlink-install --cmake-args -DBUILD_TESTING=OFF" 

# Create entrypoint script
RUN sudo bash -c "printf '#!/bin/bash\nsource /opt/ros/jazzy/setup.bash\nsource ~/ws/install/setup.bash\nexport DISPLAY=:0\nexec \"\$@\"\n' > /entrypoint.sh" && \
    sudo chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["ros2", "launch", "velodyne", "velodyne_launch.py"]

# CMD ["tail", "-f", "/dev/null"]
