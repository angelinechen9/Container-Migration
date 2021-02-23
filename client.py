import docker
import logging

def getDockerClient(env):
    client = None

    #if environment variable specific to local machine then use DockerClient to communicate with Docker server
    if(env == 'local'):
        client = DockerClient(base_url='unix://var/run/docker.sock',
                                  version='1.22')
    
    elif(env == 'swarm'):
         tls_config = docker.tls.TLSConfig(
            ca_cert='/home/azureuser/ca.pem',
            client_cert=('/home/azureuser/cert.pem', '/home/azureuser/key.pem'),
            verify=True
        )

        client = docker.DockerClient(base_url='https://ape-swarm-manager:3376',
                                  tls=tls_config,
                                  version='1.23')

    return client

def testDockerClient(env):
     client = getDockerClient(env)

    connlist = cli.containers.list()
    logging.info('List of containers running')
    for conn in connlist:
        logging.info(conn.name)

    logging.info('Docker info')
    logging.info(client.info())
