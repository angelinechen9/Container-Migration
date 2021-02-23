import docker

client = docker.from_env()
client.containers.run("ubuntu", tty=True, detach=True)
container = client.containers.list()[0]
container.start()
container.exec_run("bash ~/test.sh")
container.stop()