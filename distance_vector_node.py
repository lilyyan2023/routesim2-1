from simulator.node import Node
import copy
import math
import json

class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.dv = {self.id: {"cost": 0, "path": [self.id]}}
        self.neighbor_dv = {}


    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    def compute_shortest_path(self, n, latency):
        for dst in self.dv.keys():
            alt = math.inf
            prev = 0
            for neighbor in self.neighbors:
                dst_dv = self.neighbor_dv[neighbor]
                if self.id not in dst_dv[neighbor]["path"]:
                    if neighbor == n:
                        if latency + dst_dv[neighbor]["cost"] < alt:
                            alt = latency + dst_dv[neighbor]["cost"]
                            prev = neighbor
                    else:
                        if self.dv[neighbor]["cost"] + dst_dv[neighbor]["cost"] < alt:
                            alt = self.dv[neighbor]["cost"] + dst_dv[neighbor]["cost"]
                            prev = neighbor
            self.dv[dst]["cost"] = alt
            self.dv[dst]["path"] = copy.deepcopy(self.neighbor_dv[prev]["path"]).append(dst).reverse()

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        if neighbor not in self.dv.keys():
            self.dv[neighbor] = {"cost": latency, "path": [neighbor]}
        self.compute_shortest_path(neighbor, latency)
        routing_message_json = copy.deepcopy(self.dv)
        routing_message_rv = {"message": routing_message_json, "sender": self.id}
        routing_message = json.dumps(routing_message_rv)
        self.send_to_neighbors(routing_message)

    def compute_shortest_path_process(self):
        for dst in self.dv.keys():
            alt = math.inf
            prev = 0
            for neighbor in self.neighbors:
                dst_dv = self.neighbor_dv[neighbor]
                if self.id not in dst_dv[neighbor]["path"]:
                    if self.dv[neighbor]["cost"] + dst_dv[neighbor]["cost"] < alt:
                        alt = self.dv[neighbor]["cost"] + dst_dv[neighbor]["cost"]
                        prev = neighbor
            self.dv[dst]["cost"] = alt
            self.dv[dst]["path"] = copy.deepcopy(self.neighbor_dv[prev]["path"]).append(dst).reverse()

    # Fill in this function
    def process_incoming_routing_message(self, m):
        m_dict = json.loads(m)
        m_message_json = m_dict["message"]
        m_message = json.loads(m_message_json)
        m_sender = m_dict["sender"]
        if m_message != self.neighbor_dv[m_sender]:
            self.neighbor_dv[m_sender] = m_message
            self.compute_shortest_path_process()
            routing_message_json = copy.deepcopy(self.dv)
            routing_message_rv = {"message": routing_message_json, "sender": self.id}
            routing_message = json.dumps(routing_message_rv)
            self.send_to_neighbors(routing_message)

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        return self.dv[destination]["path"][0]
