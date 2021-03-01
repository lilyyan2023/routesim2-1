from simulator.node import Node
import copy
import math
import json

class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.dv = {self.id: {"cost": 0, "path": []}}
        self.neighbor_dv = {}


    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    def compute_shortest_path(self, n, latency):
        if self.neighbor_dv != {}:
            for dst in self.dv.keys():
                alt = math.inf
                prev = None
                for neighbor in self.neighbor_dv.keys():
                    # get every neighbor dv
                    dst_dv = self.neighbor_dv[neighbor]
                    if dst in dst_dv.keys() and self.id not in dst_dv[dst]["path"]:
                        # never entered
                        print("enter")
                        if neighbor == n:
                            if latency + dst_dv[dst]["cost"] < alt:
                                alt = latency + dst_dv[dst]["cost"]
                                prev = neighbor
                        else:
                            if self.dv[neighbor]["cost"] + dst_dv[dst]["cost"] < alt:
                                alt = self.dv[neighbor]["cost"] + dst_dv[dst]["cost"]
                                prev = neighbor
                if prev != None:
                    self.dv[dst]["cost"] = alt
                    # print(self.neighbor_dv[prev][dst]["path"])
                    new_path = copy.deepcopy(self.neighbor_dv[prev][dst]["path"])
                    # new_path.append(dst)
                    # new_path.reverse()
                    # print("updated new path" + str(new_path))
                    if new_path != self.dv[dst]["path"]:
                        new_path.append(dst)
                        # new_path.reverse()
                        self.dv[dst]["path"] = new_path

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
        # print("============================================================")
        # print("current dv " + str(self.dv))
        # print("current neighbour " + str(self.neighbor_dv))
        if self.neighbor_dv != {}:
            for dst in self.dv.keys():
                alt = math.inf
                prev = None
                for neighbor in self.neighbor_dv.keys():
                    dst_dv = self.neighbor_dv[neighbor]
                    if dst in dst_dv.keys() and self.id not in dst_dv[dst]["path"]:
                        # print("compute shortest path")
                        if self.dv[neighbor]["cost"] + dst_dv[dst]["cost"] < alt:
                            alt = self.dv[neighbor]["cost"] + dst_dv[dst]["cost"]
                            prev = neighbor
                if prev != None:
                    self.dv[dst]["cost"] = alt
                    # print(self.neighbor_dv[prev][dst]["path"])
                    new_path = copy.deepcopy(self.neighbor_dv[prev][dst]["path"])
                    # new_path.append(dst)
                    # new_path.reverse()
                    # print("dst path" + str(self.dv[dst]["path"]))
                    # print("processed new path" + str(new_path))
                    if new_path != self.dv[dst]["path"]:
                        new_path.append(dst)
                        self.dv[dst]["path"] = new_path

    # Fill in this function
    def process_incoming_routing_message(self, m):
        m_dict = json.loads(m)
        m_message = m_dict["message"]
        m_sender = m_dict["sender"]
        if m_sender not in self.dv.keys():
            self.dv[m_sender] = m_message
        if m_sender not in self.neighbor_dv.keys() or m_message != self.neighbor_dv[m_sender]:
            self.neighbor_dv[m_sender] = m_message
            for d in m_message.keys():
                if d not in self.dv.keys():
                    new_path = copy.deepcopy(m_message[d]["path"])
                    new_path.insert(0,m_sender)
                    print("new path" + str(new_path))
                    self.dv[d] = {"cost": self.neighbor_dv[m_sender][d]["cost"] + m_message[d]["cost"], "path": new_path}
            self.compute_shortest_path_process()
            routing_message_json = copy.deepcopy(self.dv)
            routing_message_rv = {"message": routing_message_json, "sender": self.id}
            routing_message = json.dumps(routing_message_rv)
            self.send_to_neighbors(routing_message)

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        print("current dv " + str(self.dv))
        print("current neighbour " + str(self.neighbor_dv))
        if destination not in self.dv.keys():
            return -1
        return self.dv[destination]["path"][0]
