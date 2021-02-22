import subprocess
def subprocess_cmd(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print proc_stdout

subprocess_cmd('docker start nervous_curran; docker exec -it nervous_curran bash -c "bash ~/test.sh"; docker stop nervous_curran')

client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
for i in client.containers.list():
    print(i.stats(stream=False))
