# System Architecture
We used load balancing and container migration to implement an integrated edge and cloud computing system that allocates resources based on the delay requirements of tasks and exchanges containers between edge and cloud.

In order to implement a prioritization method, we implemented a controller that receives task requirements from IoT devices and assigns IoT devices to containers running on nodes in a Kubernetes cluster. When a pod is created, the pod is placed on the edge node with the most resources. When a request with the requested delay is sent to the controller, the controller uses a table of CPU usage and estimated delay to send the request to any pods with the estimated delay less than the requested delay. If the request is sent to the pod with the most CPU usage, there will be spare capacity for running containers that require more CPU usage. If there are not enough resources on the edge nodes for the request, containers are exchanged between edge and cloud. A container running on an edge node is migrated to a cloud node using a prioritization method. Containers receiving requests that require longer delay are migrated from the edge nodes to the cloud nodes before containers receiving requests that require shorter delay.

![System Architecture](https://github.com/angelinechen9/Container-Migration/blob/master/System%20Architecture.png)

IoT1 sends task requirements to the controller, the controller assigns IoT1 to CC1, and IoT1 sends the request to CC1. IoT2 sends task requirements to the controller, the controller assigns IoT2 to EC1, and IoT2 sends the request to EC1. IoT3 sends task requirements to the controller, and the controller assigns IoT3 to a container running on a node. IoT4 sends task requirements to the controller. The controller stores the containers running on the nodes in a table. When the controller assigns an IoT device to a container running on a node, the controller checks if there are enough resources on the edge nodes for the request. If there not are enough resources on the edge nodes for the request, containers are migrated from the edge nodes to the cloud nodes.

# Approach
When we implemented the system, we followed the following steps:
* How to allocate processing resources in edge and cloud nodes?
* How to manage resources?
* How to balance the load of nodes?
* How to migrate workload between edge and cloud node?

# Resource Allocation
Containerization is used to allocate processing resources in edge and cloud nodes. Containerization has become an alternative to virtualization because containers are flexible, lightweight, portable, loosely coupled, scalable, and secure. Both containers and virtual machines isolate and allocate resources. In containerization, multiple containers can run on the same machine. In virtualization, the hypervisor allows multiple virtual machines to run on the same machine. While containers virtualize the operating system, virtual machines virtualize the hardware. As a result, containers are more lightweight than virtual machines. In containerization, multiple containers can share the operating system kernel. In virtualization, each virtual machine runs an operating system. Containers take up less space and take less time to start than virtual machines, which allows more containers to run on the same machine.

# Resource Management
We assumed that the workload is image processing. When a request with the image that will be processed and the requested delay is sent to the controller, the controller sends the request to a container running an image processor. A table of CPU usage and estimated delay is used to estimate the CPU usage for the requested delay. The table of CPU usage and estimated delay is created by limiting the amount of CPU used by the container and measuring the amount of time needed to process different images for different CPU usages.

We hypothesized that we can control the delay of image classification by controlling the amount of resources allocated to each task. We predicted that as delay decreases, CPU usage increases.

We used the Tensorflow Object Detection API to process images. The Tensorflow Object Detection API is served using Flask. The application is containerized using Docker.

The workloads are three images that have different resolutions and different sizes. As the resolution and the size of the image increases, the amount of time needed to process the image increases.

We limited the amount of CPU used by the container and measured the amount of time needed to process different images for different CPU usages. We fit an exponential model to the results.

We used the following command to limit the amount of CPU used by the container:
```bash
docker run -it --cpus x
```

![Real Time Comparisons Data](https://github.com/angelinechen9/Container-Migration/blob/master/Real%20Time%20Comparisons%20Data.png)
![Real Time Comparisons Graph](https://github.com/angelinechen9/Container-Migration/blob/master/Real%20Time%20Comparisons%20Graph.png)

Our hypothesis is correct because there is an inverse relationship between CPU usage and delay. As delay decreases, CPU usage increases. We modeled the inverse relationship between CPU usage and delay by fitting an exponential model to the results. The exponential model is used to estimate the CPU usage for the given delay or the delay for the given CPU usage.

# Load Balancing Strategy
When IoT devices are added to the system, the workloads running on the IoT devices are added to the table stored in the controller. When edge nodes and cloud nodes are added to the system, the edge nodes and the cloud nodes are added to the table stored in the controller. When IoT devices send requests to the controller, a table of CPU usage and estimated delay is used to estimate the CPU usage for the requested delay. If the estimated delay is less than the requested delay, the request can be sent to the node.

There are three cases:

Case 1: There are enough resources on the edge nodes for the new request. The new request is sent to the edge node with the most CPU usage.

The controller finds an edge node that can receive the request. If there are enough resources on the edge nodes for the request, the controller sends the request to the edge node with the most CPU usage. The table that stores requests sent to the edge nodes is used to find an edge node with the estimated delay less than the requested delay. The new request is sent to the edge node with the most CPU usage. The table that stores requests sent to the edge nodes is updated.

For example, two requests are sent to the controller.

![Load Balancing Strategy Case 1](https://github.com/angelinechen9/Container-Migration/blob/master/Load%20Balancing%20Strategy%201%201.png)
![Load Balancing Strategy Case 1](https://github.com/angelinechen9/Container-Migration/blob/master/Load%20Balancing%20Strategy%201%202.png)
![Load Balancing Strategy Case 1](https://github.com/angelinechen9/Container-Migration/blob/master/Load%20Balancing%20Strategy%201%203.png)

There are enough resources on the edge nodes for the request because $usage_{1} < 1$. The first request is sent to the edge node. IoT1 sends task requirements to the controller, the controller assigns IoT1 to EC1, and IoT1 sends the request to EC1.

Case 2: There are not enough resources on the edge nodes for the new request. An old request sent to an edge node cannot be sent to a cloud node. The new request is sent to the cloud node with the most CPU usage.

The controller finds an edge node that can receive the request. If there are not enough resources on the edge nodes for the request, the controller finds a request sent to an edge node that can be sent to a cloud node. A table of CPU usage and estimated delay is used to estimate the CPU usage for the requested delay if the old requests are sent to the cloud nodes. If the requests sent to the edge nodes cannot be sent to the cloud nodes, the controller sends the request to the cloud node with the most CPU usage. The table that stores requests sent to the cloud nodes is used to find a cloud node with the estimated delay less than the requested delay. The new request is sent to the cloud node with the most CPU usage. The table that stores requests sent to the cloud nodes is updated.

For example, two requests are sent to the controller.

![Load Balancing Strategy Case 2](https://github.com/angelinechen9/Container-Migration/blob/master/Load%20Balancing%20Strategy%202%201.png)
![Load Balancing Strategy Case 2](https://github.com/angelinechen9/Container-Migration/blob/master/Load%20Balancing%20Strategy%202%202.png)
![Load Balancing Strategy Case 2](https://github.com/angelinechen9/Container-Migration/blob/master/Load%20Balancing%20Strategy%202%203.png)

Case 3: There are not enough resources on the edge nodes for the new request. An old request sent to an edge node can be sent to a cloud node. The container receiving the old request is migrated from the edge node to the cloud node. The new request is sent to the edge node with the most CPU usage.

The controller finds an edge node that can receive the request. If there are not enough resources on the edge nodes for the request, the controller finds a request sent to an edge node that can be sent to a cloud node. A table of CPU usage and estimated delay is used to estimate the CPU usage for the requested delay if the old requests are sent to the cloud nodes. If the requests sent to the edge nodes can be sent to the cloud nodes, containers are migrated from the edge nodes to the cloud nodes, and the controller sends the request to the edge node with the most CPU usage. The table that stores requests sent to the edge nodes is updated. The table that stores requests sent to the edge nodes is used to find an edge node with the estimated delay less than the requested delay. The new request is sent to the edge node with the most CPU usage. The table that stores requests sent to the edge nodes is updated.

For example, two requests are sent to the controller.

![Load Balancing Strategy Case 3](https://github.com/angelinechen9/Container-Migration/blob/master/Load%20Balancing%20Strategy%203%201.png)
![Load Balancing Strategy Case 3](https://github.com/angelinechen9/Container-Migration/blob/master/Load%20Balancing%20Strategy%203%202.png)
![Load Balancing Strategy Case 3](https://github.com/angelinechen9/Container-Migration/blob/master/Load%20Balancing%20Strategy%203%203.png)
![Load Balancing Strategy Case 3](https://github.com/angelinechen9/Container-Migration/blob/master/Load%20Balancing%20Strategy%203%204.png)

# Container Migration Strategy
We used Linux Checkpoint/Restore in Userspace (Linux CRIU) to implement post-copy migration. We used the following commands to migrate containers:
```bash
[src] criu dump --tree <pid> --images-dir <path-to-existing-directory> --leave-stopped
[src] scp -r <path-to-images-dir> <dst>:/<path-to-images>
[dst] criu restore --images-dir <path-to-images>
```

# Resource Monitoring
In the first parts of setting up the test script, we created a base docker container that is running Ubuntu. We created a copy of the test.sh script inside the home directory, so the file is at ~/test.sh.

On another terminal window we use docker ps to check what the name of the running container is:

```bash
$ docker ps
CONTAINER ID   IMAGE     COMMAND       CREATED          STATUS          PORTS     NAMES
5f98e54075c1   ubuntu    "/bin/bash"   20 minutes ago   Up 19 minutes             nervous_curran
```

We are now able to use the command ```docker exec -it nervous_curran bash -c "bash ~/test.sh"```, and it will use the container's resources and output the command results into my terminal window. We checked with docker stats nervous_curran and made sure it was using the container's resources:

```bash
CONTAINER ID   NAME             CPU %     MEM USAGE / LIMIT     MEM %     NET I/O        BLOCK I/O   PIDS
5f98e54075c1   nervous_curran   108.68%   68.99MiB / 6.148GiB   1.10%     40MB / 754kB   0B / 0B     3
```

Now, at this point we just need to transpose these commands into one simple Python script. *Using Python 2.7

We running unix commands via python using the subprocess module. The order of unix commands we run are:
```bash
	docker start nervous_curran
	docker exec -it nervous_curran bash -c "bash ~/test.sh"
	docker stop nervous_curran
```

## Resources
[DoMonit](https://github.com/eon01/DoMonit)                                                                            

[Docker Memory & CPU Usage Monitoring](https://stackoverflow.com/questions/59750238/python-docker-get-containers-memory-usage-cpu-percentage-programmatically-in-p)

[Python Docker Image](https://hub.docker.com/_/python)                                                                                

[Docker-Python Compatibility](https://djangostars.com/blog/what-is-docker-and-how-to-use-it-with-python/)
