from simulator.node import Node
import copy
import math
import json

class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.dv = {str(self.id): {"cost": 0, "path": []}}
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
                    if dst in dst_dv["dv"].keys() and str(self.id) not in dst_dv["dv"][dst]["path"]:
                        if neighbor == str(n):
                            if latency + dst_dv["dv"][dst]["cost"] < alt:
                                alt = latency + dst_dv["dv"][dst]["cost"]
                                prev = neighbor
                        else:
                            if dst_dv["dv"][str(self.id)]["cost"] + dst_dv["dv"][dst]["cost"] < alt:
                                alt = dst_dv["dv"][str(self.id)]["cost"] + dst_dv["dv"][dst]["cost"]
                                prev = neighbor
                if prev != None:
                    self.dv[dst]["cost"] = alt
                    # print(self.neighbor_dv[prev][dst]["path"])
                    new_path = copy.deepcopy(self.neighbor_dv[prev]["dv"][dst]["path"])
                    # new_path.append(dst)
                    # new_path.reverse()
                    # print("updated new path" + str(new_path))
                    if new_path != self.dv[dst]["path"]:
                        new_path.append(dst)
                        # new_path.reverse()
                        self.dv[dst]["path"] = new_path
                        #print(new_path)

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        if neighbor not in self.dv.keys() or latency != -1:
            self.dv[str(neighbor)] = {"cost": latency, "path": [str(neighbor)]}
        self.compute_shortest_path(neighbor, latency)
        routing_message_json = copy.deepcopy(self.dv)
        routing_message_rv = {"message": json.dumps(routing_message_json), "sender": str(self.id), "seq": self.get_time()}
        routing_message = json.dumps(routing_message_rv)
        self.send_to_neighbors(routing_message)

    def compute_shortest_path_process(self):
        print("============================================================")
        print("current dv " + str(self.dv))
        print("current neighbour " + str(self.neighbor_dv))
        if self.neighbor_dv != {}:
            for dst in self.dv.keys():
                alt = math.inf
                prev = None
                for neighbor in self.neighbor_dv.keys():
                    dst_dv = self.neighbor_dv[neighbor]
                    if dst in dst_dv["dv"].keys() and str(self.id) not in dst_dv["dv"][dst]["path"]:
                        # print("compute shortest path")
                        print(dst_dv["dv"].keys())
                        if dst_dv["dv"][str(self.id)]["cost"] + dst_dv["dv"][dst]["cost"] < alt:
                            alt = dst_dv["dv"][str(self.id)]["cost"] + dst_dv["dv"][dst]["cost"]
                            prev = neighbor
                if prev != None:
                    self.dv[dst]["cost"] = alt
                    new_path = copy.deepcopy(self.neighbor_dv[prev]["dv"][dst]["path"])
                    new_path.append(dst)
                    new_path.reverse()
                    # print(self.neighbor_dv[prev][dst]["path"])                    
                    #print("dst path" + str(self.dv[dst]["path"]))
                    #print("processed new path" + str(new_path))
                #if new_path != self.dv[dst]["path"]:
                    #new_path.append(dst)
                    #self.dv[dst]["path"] = new_path
                    #print(new_path)

    # Fill in this function
    def process_incoming_routing_message(self, m):
        
        m_dict = json.loads(m)
        m_message = json.loads(m_dict["message"])
        m_seq = m_dict["seq"]
        m_sender = m_dict["sender"]
        tempt = copy.deepcopy(self.dv)
        
        if str(m_sender) not in self.dv.keys():
            self.dv[str(m_sender)] = m_message[str(self.id)]
            self.dv[str(m_sender)]["path"].remove(str(self.id))
            self.dv[str(m_sender)]["path"].reverse()
            self.dv[str(m_sender)]["path"].append(str(m_sender))
        for dst in m_message.keys():
           if str(dst) not in self.dv.keys():
               path = copy.deepcopy(m_message[dst]["path"])
               cost = m_message[dst]["cost"]
               path = copy.deepcopy(self.dv[str(m_sender)]["path"]) + path
               self.dv[dst] = {"cost": cost + self.dv[m_sender]["cost"], "path": path}
        if str(m_sender) not in self.neighbor_dv.keys() or m_seq >= self.neighbor_dv[str(m_sender)]["seq"]:
            self.neighbor_dv[m_sender] = {"dv": m_message, "seq": m_seq}
        self.compute_shortest_path_process()
        if self.dv != tempt:
            routing_message_json = copy.deepcopy(self.dv)
            routing_message_rv = {"message": json.dumps(routing_message_json), "sender": str(self.id), "seq": m_seq}
            routing_message = json.dumps(routing_message_rv)
            self.send_to_neighbors(routing_message)
        else:
            self.dv = tempt



    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        #print("current dv " + str(self.dv))
        #print("current neighbour " + str(self.neighbor_dv))
        #print(self.dv.keys())
        if str(destination) not in self.dv.keys():
            return -1
        return int(self.dv[str(destination)]["path"][0])
