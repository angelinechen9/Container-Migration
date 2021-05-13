import math
import numpy as np
from scipy.optimize import curve_fit
from pynverse import inversefunc
import datetime

class Request:
	def __init__(self, id, workload, delay):
		self.id = id
		self.workload = workload
		self.start_time = datetime.datetime.now()
		self.end_time = self.start_time + datetime.timedelta(seconds=delay)
		self.delay = delay
		self.usage = self.workload.fit_inverse(self.delay)

	def __repr__(self):
		return "{'id': %s, 'delay': %s, 'usage': %s}" %(str(self.id), str(self.delay), str(round(self.usage, 2)))

class Workload:
	def __init__(self, id, delay, usage):
		self.id = id
		self.delay = np.array(delay)
		self.usage = np.array(usage)
		def exponential(x, a, b):
			return a * np.exp(b * x)
		self.param, self.param_cov = curve_fit(exponential, self.usage, self.delay)

	#estimate the delay
	def fit(self, x):
		return self.param[0] * math.exp(self.param[1] * x)

	#estimate the usage
	def fit_inverse(self, y):
		inverse = inversefunc(lambda x: self.param[0] * math.exp(self.param[1] * x))
		return inverse(y).item()

class Node:
	def __init__(self, id):
		self.id = id
		self.usage = 0
		self.containers = []

	def __repr__(self):
		return "{'usage': %s, 'containers': %s}" %(str(round(self.usage, 2)), str(self.containers))

class LoadBalancer:
	def __init__(self, latency, migration_time):
		self.request_id = 0
		self.workloads = {}
		self.edge_nodes = {}
		self.cloud_nodes = {}
		self.latency = latency
		self.migration_time = migration_time

	#find a node that can receive the request
	def find_node(self, new_request):
		for edge_key, edge_value in self.edge_nodes.items():
			filter(lambda container : container.end_time > datetime.datetime.now(), edge_value.containers)
		for cloud_key, cloud_value in self.cloud_nodes.items():
			filter(lambda container : container.end_time > datetime.datetime.now(), cloud_value.containers)
		#find an edge node that can receive the request
		node = ""
		for key, value in self.edge_nodes.items():
			#if the estimated delay is less than the required delay
			if (new_request.workload.fit(1 - value.usage) < new_request.delay):
				if (node == ""):
					node = key
				if ((node != "") and (value.usage > self.edge_nodes[node].usage)):
					node = key
		#if there are not enough resources on the edge nodes for the request
		if (node == ""):
			#find requests sent to the edge nodes that can be sent to the cloud nodes
			edge_node = ""
			cloud_node = ""
			request = {}
			maximum = 0
			for edge_key, edge_value in self.edge_nodes.items():
				for container in edge_value.containers:
					for cloud_key, cloud_value in self.cloud_nodes.items():
						#if the estimated delay is less than the required delay
						if (((1 - edge_value.usage) + container.usage > new_request.usage) and (container.usage > maximum) and (container.workload.fit(1 - cloud_value.usage) + self.latency < container.delay) and (datetime.datetime.now() + datetime.timedelta(seconds=self.migration_time) < container.end_time)):
							edge_node = edge_key
							cloud_node = cloud_key
							request = container
							maximum = container.usage
			#if the requests sent to the edge nodes cannot be sent to the cloud nodes
			if (cloud_node == ""):
				#send the request to the cloud node with the most CPU usage
				cloud_node = ""
				for key, value in self.cloud_nodes.items():
					if (cloud_node == ""):
						cloud_node = key
					if ((cloud_node != "") and (value.usage > self.cloud_nodes[cloud_node].usage)):
						cloud_node = key
				self.add_request(self.cloud_nodes, cloud_node, new_request)
			#if the requests sent to the edge nodes can be sent to the cloud nodes
			else:
				#migrate containers from the edge nodes to the cloud nodes
				self.remove_request(container)
				#send the request to the edge node with the most CPU usage
				cloud_node = ""
				for key, value in self.cloud_nodes.items():
					if (cloud_node == ""):
						cloud_node = key
					if ((cloud_node != "") and (value.usage > self.cloud_nodes[cloud_node].usage)):
						cloud_node = key
				self.add_request(self.cloud_nodes, cloud_node, container)
				self.add_request(self.edge_nodes, edge_node, new_request)
		#if there are enough resources on the edge nodes for the request
		else:
			#send the request to the edge node with the most CPU usage
			self.add_request(self.edge_nodes, node, new_request)

	#add the request to the table
	def add_request(self, nodes, node, request):
		nodes[node].containers.append(request)
		nodes[node].usage += request.usage

	#remove the request from the table
	def remove_request(self, request):
		for key, value in self.edge_nodes.items():
			for container in value.containers:
				if (request.id == request.id):
					value.containers.remove(request)
					value.usage -= request.usage
		for key, value in self.cloud_nodes.items():
			for container in value.containers:
				if (request.id == request.id):
					value.containers.remove(request)
					value.usage -= request.usage

	#add the workload to the table
	def add_workload(self, workload_id, delay, usage):
		self.workloads[workload_id] = Workload(workload_id, delay, usage)

	#remove the workload from the table
	def remove_workload(self, workload_id, delay, usage):
		del self.workloads[workload_id]

	#add the edge node to the table
	def add_edge_node(self, edge_node_id):
		self.edge_nodes[edge_node_id] = Node(edge_node_id)

	#remove the edge node from the table
	def remove_edge_node(self, edge_node_id):
		del self.edge_nodes[edge_node_id]

	#add the cloud node to the table
	def add_cloud_node(self, cloud_node_id):
		self.cloud_nodes[cloud_node_id] = Node(cloud_node_id)

	#remove the cloud node from the table
	def remove_cloud_node(self, cloud_node_id):
		del self.cloud_nodes[cloud_node_id]

	#send the request to the node
	def send_request(self, workload, delay):
		if (workload in list(self.workloads.keys())):
			self.request_id += 1
			request = Request(self.request_id, self.workloads[workload], delay)
			self.find_node(request)
			print(self.edge_nodes)
			print(self.cloud_nodes)