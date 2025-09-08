# Node-(RED)<sup>2</sup> - Node-RED-based Robotics Empowerment Designer <!-- omit from toc -->
<div align="center">
  <img width="500" height="auto" src="images/cover.png">
</div>

## Table of Contents <!-- omit from toc -->
- [About the project](#about-the-project)
- [Key components](#key-components)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Limitations for Pepper Robot](#limitations-for-pepper-robot)  
  - [Installation](#installation)
    - [Preliminary explanations](#preliminary-explanations)
- [Usage](#usage)
  - [About nodes](#about-nodes)  
  - [Node list](#node-list)
- [Architecture](#architecture)
  - [Pepper robot](#pepper-robot)
  - [Docker Host](#docker-host)
- [Troubleshooting](#troubleshooting)
  - [Known/Typical issues](#knowntypical-issues)
- [Contributing](#contributing)
- [License](#license)
- [Setup Pepper/Salt, currently WIP](#setup-peppersalt-currently-wip)
- [Temi and LimeSurvey, currently not tested](#temi-and-limesurvey)
- [Configuration](#configuration)

## About the project
Node-(RED)<sup>2</sup> is a self-hosted web application designed to allow even untrained users to easily create and configure scenarios for different robots and multi-robot scenarios. Using custom nodes and flow control, this project leverages and extends the capabilities of [Node-RED](https://nodered.org/) as a low-code (visual) programming environment.

Currently supported robots are, in various combinations:
- Pepper
- Sawyer 
- Temi

With Node-RED the user will be able to easily create and configure scenarios for the robots, subsequently referred to as *flows*. To enable even non-technical users to use the system, we have deliberately made some fundamental changes to Node-RED. Therefore, we have moved away from the original event-based approach of how flows are started and stopped in Node-RED. In Node-(RED)<sup>2</sup> the user has to define a clear start and end to a flow with the respective *Start*- and *Stop*-nodes. This not only is a means of organization and intuitive This allows the user to start or stop a flow at any time.

> **Note**:
> This application was referenced in the paper ***Weike, M., Ruske, K., Gerndt, R. & Doernbach, T., 2024. Enabling Untrained Users to Shape Real-World Robot Behavior Using an Intuitive Visual Programming Tool in Human-Robot Interaction Scenarios, in International Symposium on Technological Advances in Human-Robot Interaction***.

## Key components
- [Node-RED](https://nodered.org/)
- [libqi-python](https://github.com/aldebaran/libqi-python)
- [Flask](https://github.com/pallets/flask/)

## Getting Started


Furthermore, this project is still in its early stages and should therefore only be used in secure local networks. In its current state, it should NEVER be accessible on public networks.
### Prerequisites
- Pepper robot running NAOqi 2.5.10.7 (QiSDK [NAOqi 2.9] is **not** supported)
- Ubuntu 22.04/Debian Bullseye (other flavours will probably work, but weren't tested)
- Docker Engine (https://docs.docker.com/engine/install/ubuntu/), Docker post-installation steps for Docker Engine (https://docs.docker.com/engine/install/linux-postinstall/) and Docker-Compose
- For Temi: Android Studio (Meerkat Feature Drop Version or newer)

### Limitations for Pepper Robot
This project uses the official [Python bindings](https://github.com/aldebaran/libqi-python) from aldebaran in order to control the robot. These bindings currently provide Python wheels only for x86-based systems and only up to Python 3.5. Releases AFTER version 1.0 will be supplied with a self-compiled Wheel for Python 3.10 (tested on Ubuntu 22.04).

### Installation

#### Preliminary explanations

- This repository is the frontend part of NodeRed. Alone, is it useless. 
- To connect the frontend with the robots, you need to include middleware repositories of one or more robots and start the respective docker-compose file. They are included as submodules, a Git functionality. More info on this [here](https://git-scm.com/book/en/v2/Git-Tools-Submodules) and in the following section.

1. Clone this repository
    ```sh
      git clone https://github.com/Robotics-Empowerment-Designer/node-red-standalone.git
    ```

2. For Pepper: initialize pepper_middleware subrepo in your project
    ```sh
      git submodule init
      git submodule add git@github.com:Robotics-Empowerment-Designer/pepper-middleware.git pepper-middleware
    ```
    or
    ```sh
      git submodule init
      git submodule add https://github.com/Robotics-Empowerment-Designer/pepper-middleware.git pepper-middleware
    ```
3. For Sawyer: Initialize sawyer_middleware subrepo in your project
     ```sh
      git submodule init
      git submodule add git@github.com:Robotics-Empowerment-Designer/sawyer-middleware.git sawyer-middleware
    ```
    or
    ```sh
      git submodule init
      git submodule add https://github.com/Robotics-Empowerment-Designer/sawyer-middleware.git sawyer-middleware
    ```
4. If you want to use Temi, install the Temi Middleware application on the robot and start the app "Mqtt" in the app overview.  

5. Build the necessary docker containers:

    Run the script with the following command. It will give you the opportunity to set the environment variables of EVERY robot. You can use the default values for most cases, or change the created .env file afterwards (Make sure to adjust ROBOT_IP_PEPPER and ROBOT_IP_SAWYER). Unnecessary environment variables can be ignored.

    ```sh
      ./buildAll.sh
    ```

7. (Optional) Check the log files to see if the building was successful. You can also check if the containers are displayed in docker with
    ```sh
       docker container ls
    ```

8. A custom MQTT broker for the communication with Temi is automatically started when running a docker compose file associated with Temi. 

    You might need to adjust the MQTT_BROKER_URL in the .env file of this project and BROKER_URL (For Localhost) in MainActivity.kt in the Temi Middleware application to your device IP.

    You can check the connection with for example MQTT Explorer. If you want to use a broker with authentification you have to adjust the env-variables MQTT_BROKER_USERNAME and MQTT_BROKER_PASSWORD.
        


9. After the initial setup is finished, you can start the respective middlewares along with NodeRed using one of the following commands: 
    ```sh
      # Pepper only
      docker compose -f docker-compose_pepper.yml up 

      # Sawyer only
      docker compose -f docker-compose_sawyer.yml up 

      # Temi only
      docker compose -f docker-compose_temi.yml up 

      # Sawyer & Pepper
      docker compose -f docker-compose_sawyer_pepper.yml up

      # Temi & Pepper
      docker compose -f docker-compose_temi_pepper.yml up   

      # Sawyer, Pepper & Temi
      docker compose -f docker-compose_temi_sawyer_pepper.yml up 
    ```

**IMPORTANT:**
- Currently, the pepper nodes are necessary to start NodeRed² successfully, even if you do not use the robot. Feel free to submit a merge request if you have solved this issue. 
- For Temi usage: Every time you start the container with the node-red configuration (docker compose -f docker-compose_temi_sawyer_pepper.yml up), you need to start the Mqtt application on the temi robot. You can find the Mqtt application using the Temi's tablet screen. You do not need to give the app permissions (grey screen).
- The following documentation assumes that you're using the default port. If you changed the port in the configuration wizard you need to use the respective port instead.

The application should now be running (under `http://<host-ip>:1880` or [http://localhost:1880](http://localhost:1880)) and both the log as well as the debug page (under `http://<host-ip>:5000` or [http://localhost:5000](http://localhost:5000)) should show `Connection type: Real robot`. If that isn't the case and it says `Connection type: disconnected` the application is running but a connection with the robot couldn't be established. Take a look at the [troubleshooting](#troubleshooting) section for more information.

## Usage
<div align="center">

  ![](images/nodered_usage.mp4)

</div>

<div align="center">
  <p align="center">Creation of a simple flow.</p>
</div>

1. Open Node-RED in your browser (`http://<flask-ip>:1880`, or [http://localhost:1880](http://localhost:1880)).
2. Drag a *Start*- and a *Stop*-node in your workspace (every flow **needs** exactly one *Start*-node and at least one *Stop*-node). Alternatively you can also use an *Inject*-node as a start point and a "Debug*-node as end point.
3. Implement your scenario with the other nodes.
   1. Wire up the nodes using the grey connectors as shown in the previous video.
   2. You can configure any node with a double-click on the respective node.
4. Deploy your scenario (red button in the top-right corner).
5. Start your flow (red square of the *Start*-node or blue square of the *Inject*-node).
6. If you want to use the buttons on the tablet to start a flow go to this [instruction](https://github.com/Robotics-Empowerment-Designer/temi-middleware?tab=readme-ov-file#test-3-checking-that-the-display-buttons-work-correctly-with-node-red).

### About nodes
Every robot has it's own nodes and needs to be controlled with only his own nodes. 
Every flow needs to have an own start- and stop node,
Sawyer needs the Initialisation node after his first action to work properly.

### Node list
The following figures show all currently implemented nodes for Temi, Pepper and Sawyer. Each node has a detailed documentation which is integrated directly into Node-RED. This documentation is available in two different versions, a short version which can be opened by hovering over a node in the node list or the detailed version which can be opened with the shortcut `CTRL+G H`. Alternatively, the markdown can be viewed at [/node-red/nodes/\<robot_name>/locales/\<node>/\<language>/\<name>.html](./node-red/nodes/) for Pepper and Sawyer and at [/node-red/nodes/\<robot_name>/\<node>/\<name>.html](./node-red/nodes/) for Temi.
<div align="center">
  Temi nodes
  <img width="650" height="auto" src="images/nodered_nodes_ss25.png">

  Pepper nodes
  <img width="650" height="auto" src="images/nodered_nodes.png">

  Sawyer nodes
  <img width="650" height="auto" src="images/Sawyer_nodes.png">
</div>


## Architecture
<div align="center">
  <img width="650" height="auto" src="images/deployment_diagram.jpg">
</div>

### Pepper robot
The robot consists of two separate systems: the NAOqi broker, which we use to trigger actions on the robot (i.e. to play an animation), and the tablet, which is running Android 5.1.  The only way to programmatically interact with the tablet is through the NAOqi-Broker, which limits the usefulness of the tablet (e.g. it's not possible to detect specific touch events of the tablet or to serve custom web pages that include javascript).

### Docker Host
The Docker host consists of three main containers: REST-Server, Node-RED and Mosquitto. The REST-Server container contains a Flask WSGI application that in turn exposes our API, which is mainly called by Node-RED. Additionally, it contains a debug page that lists useful information and some quick actions from the robot.

Node-RED acts as a frontend and is mostly responsible for the correct timing of the API calls. Node-RED and our Flask application communicate over Socket.IO (as well as some HTTP calls for configuration information).
> **Note:**
> Because we use docker it is important to note, that any changes you make to files inside of the container will only be persistent if this change happens inside of a mapped volume (can be seen in [docker-compose.yml](docker-compose.yml)). Should you make changes to dependencies (i.e. in [/rest-server/requirements.txt](https://github.com/Robotics-Empowerment-Designer/RED-Pepper-Middleware/blob/master/rest-server/requirements.txt)) you need to rebuild the images.

## Troubleshooting
Should you encounter issues (i.e. you start a flow but the robot doesn't perform any actions) the best place to start would be the .log file under `/\<robot-middleware>/rest-server/<robot-name>.log`. In there you should be able to find some pointers to your issues in the form of warning and error messages. For Temi you can find these information in the Logcat-subsection in Android Studio.

### Known/Typical issues
1. **My robot doesn't do anything!** <br>
  Is the robot switched on? Make sure your robot is connected to the application. You can check this through the debug site ([localhost:5000](localhost:5000)) or in the log file for `Connection type: Real robot` or `Connection type: Disconnected`. If your robot is not connected to the application make sure that both the system that the application is running on as well as the robot (**both** the robot and the tablet!) are in the same network. Next you should make sure that the robot ip you configured in .env-file is still valid (for pepper: briefly press the button behind the tablet on its chest to get the robot ip). If you're running this project inside of a VM, make sure to use a network bridge instead of NAT.
2. **After some time the robot doesn't do anything anymore!** <br>
  This is probably caused by one of the following two problems: either your network has connection issues (characterizes by longer processing time for e.g. speech recognition) or the libqi-python library tries to spawn a new thread which causes our application to lose connection to the robot and (currently) be in an unrecoverable state. Should the latter be the case you need to restart the application and refresh Node-RED in your browser.
3. **I can't install your application!** <br>
  This is most likely because you're either trying to install our application on Windows or on an arm-based system (e.g. newer Macs, Raspberry Pi).
4. **I started the building of the docker images again and now the ports are all in use!** <br>
You need to remove the currently running docker containers and images to get the setup to a newborn, valid state again. Unlike a stupid terminal, docker containers do not disappear after you have stopped them. Do this with the following sets of commands:

```sh
  # show images and containers currently existing
  docker image ls
  docker container ls

  # force-remove images
  docker image rm --force <image_names\> 
  docker image prune

  # force-remove containers
  docker container rm --force <container_names\> 
  docker container prune
```
5. **I do not know if the robot is accessible over the network!**
Ensure that you are in the same network as the robots. After that, ping them by using the terminal. 
```sh
  ping <IP-ADRESS\>
  ping <HOSTNAME\>

  # example for pepper
  ping pepper.hcr-lab
```

## Contributing
We welcome any contributions (improvements, bug fixes, new features or even additional robot support), just create a pull request!
Additionally we've created a short [contribution guide](./CONTRIBUTING.md). There you can find instructions on how to create your own nodes for this project as well as additional information on how to create issues an pull requests.


[comment]: # (Links)
[NodeRED-url]: https://nodered.org/

## License
This project is licensed under the Apache 2 License - see [LICENSE](/LICENSE) for details


## Setup Pepper/Salt, currently WIP
1. Install Docker
2. `./buildContainers.sh`
3. `docker-compose docker-compose_pepper_salt.yml -f up` for both robots, `_pepper.yml` and `_salt.yml` only for one robot, respectively
4. open `http://<IP_ADDRESS>:PORT` in the browser, see configuration; with PORT being 1881...1888 and IP_ADDRESS being the one of the machine where the containers run (NOT a robot IP!)

### Temi and LimeSurvey, currently not tested
Please have a look at [Temi-and-Lime](Temi_and_Lime.md)

## Configuration
Ports and IP addresses of the robots are configured in the `.env` file

