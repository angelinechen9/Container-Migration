from load_balancer import LoadBalancer
from flask import Flask
from flask import request
import json

app = Flask(__name__)

@app.before_first_request
def before_first_request():
	global load_balancer
	latency = eval(input("Latency (s): "))
	migration_time = eval(input("Migration Time (s): "))
	load_balancer = LoadBalancer(latency, migration_time)

@app.route("/add_workload", methods=["POST"])
def add_workload():
	global load_balancer
	data = json.loads(request.data)
	load_balancer.add_workload(data["workload_id"], data["delay"], data["usage"])
	return "workload added to the table"

@app.route("/add_edge_node", methods=["POST"])
def add_edge_node():
	global load_balancer
	data = json.loads(request.data)
	load_balancer.add_edge_node(data["edge_node_id"])
	return "edge node added to the table"

@app.route("/add_cloud_node", methods=["POST"])
def add_cloud_node():
	global load_balancer
	data = json.loads(request.data)
	load_balancer.add_cloud_node(data["cloud_node_id"])
	return "cloud node added to the table"

@app.route("/send_request", methods=["POST"])
def send_request():
	global load_balancer
	data = json.loads(request.data)
	load_balancer.send_request(data["workload"], data["delay"])
	return "request sent"