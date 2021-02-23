# Test Script Description

In the first parts of setting up the test script, we created a base docker container that is running Ubuntu. We created a copy of the test.sh script inside the home directory, so the file is at ~/test.sh.

On another terminal window we use docker ps to check what the name of the running container is:

```bash
$ docker ps
CONTAINER ID   IMAGE     COMMAND       CREATED          STATUS          PORTS     NAMES
5f98e54075c1   ubuntu    "/bin/bash"   20 minutes ago   Up 19 minutes             nervous_curran
```

We are now able to use docker exec -it nervous_curran bash -c "bash ~/test.sh", and it will use the container's resources and output the command results into my terminal window. We checked with docker stats nervous_curran and made sure it was using the container's resources:

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

## Resources:
[DoMonit](https://github.com/eon01/DoMonit)                                                                            

[Docker Memory & CPU Usage Monitoring](https://stackoverflow.com/questions/59750238/python-docker-get-containers-memory-usage-cpu-percentage-programmatically-in-p)

[Python Docker Image](https://hub.docker.com/_/python)                                                                                

[Docker-Python Compatibility](https://djangostars.com/blog/what-is-docker-and-how-to-use-it-with-python/) 
