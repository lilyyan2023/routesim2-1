from simulator.node import Node
import copy
import math
import json

class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.dv = {str(self.id): {"cost": 0, "path": []}}
        self.neighbor_dv = {}
        self.neighbor_seq = {}
        self.cost = {}
        self.need_to_send = False


    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"


    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        #print("========================Update===============================")
        #print("current dv " + str(self.dv))
        #print("current neighbour " + str(self.neighbor_dv))
        

        if neighbor not in self.neighbors:
            self.dv[str(neighbor)] = {"cost": latency, "path": [str(neighbor)]}
            self.neighbors.append(neighbor)
            self.cost[str(neighbor)] = latency
        elif latency != -1:
            self.cost[str(neighbor)] = latency
            #self.compute_shortest_path()
        elif latency == -1:
            self.neighbors.remove(neighbor)
            self.cost[str(neighbor)] = math.inf
            self.neighbor_dv.pop(str(neighbor))
            for dst in self.dv.keys():
                if len(self.dv[dst]["path"]) != 0 and self.dv[dst]["path"][0] == str(neighbor):
                    self.dv[dst]["path"] = []
                    self.dv[dst]["cost"] = math.inf
        routing_message_json = self.dv
        routing_message_rv = {"message": json.dumps(routing_message_json), "sender": str(self.id), "seq": self.get_time()}
        routing_message = json.dumps(routing_message_rv)
        self.send_to_neighbors(routing_message)
            
        
        
        

    def compute_shortest_path(self):
        #print("========================Calculate===============================")
        #print("current dv " + str(self.dv))
        #print("current neighbour " + str(self.neighbor_dv))
        #print("cost " + str(self.cost))
        if self.neighbor_dv != {}:
            for dst in self.dv.keys():
                #print(dst)
                alt = math.inf
                prev = None
                for neighbor in self.neighbor_dv.keys():
                    dst_dv = self.neighbor_dv[neighbor]["dv"]
                    if dst in dst_dv.keys() and str(self.id) not in dst_dv[dst]["path"]:
                        # print("compute shortest path")
                        #print(self.cost.keys())
                        if self.cost[neighbor] + dst_dv[dst]["cost"] < alt:
                            alt = self.cost[neighbor] + dst_dv[dst]["cost"]
                            prev = neighbor
                if prev != None:
                    
                    new_path = copy.deepcopy(self.neighbor_dv[prev]["dv"][dst]["path"])
                    #print(new_path)
                    new_path.reverse()
                    new_path.append(prev)
                    new_path.reverse()
                    if self.dv[dst]["path"] != new_path or self.dv[dst]["cost"] != alt:
                        self.need_to_send = True
                    self.dv[dst]["path"] = new_path
                    self.dv[dst]["cost"] = alt
                    
        #print("Finish dv " + str(self.dv))
        #print("Finish neighbour " + str(self.neighbor_dv))

    # Fill in this function
    def process_incoming_routing_message(self, m):
        self.need_to_send = False
        #print("recevied" + m)
        m_dict = json.loads(m)
        m_message = json.loads(m_dict["message"])
        m_seq = m_dict["seq"]
        m_sender = str(m_dict["sender"])
        #tempt = copy.deepcopy(self.dv)
        if m_sender not in self.neighbor_seq.keys() or m_seq > self.neighbor_seq[m_sender]:
            #if m_sender in self.neighbor_seq.keys():
                #print(self.neighbor_dv[m_sender]["dv"] == m_message)
            self.neighbor_dv[m_sender] = {"dv": m_message, "seq": m_seq}
            self.neighbor_seq[m_sender] = m_seq
            for dst in m_message.keys():
                if dst not in self.dv.keys():
                    self.dv[dst] = {"cost": math.inf, "path": []}
                    self.need_to_send = True
            self.compute_shortest_path()
        if self.need_to_send:
            routing_message_json = self.dv
            routing_message_rv = {"message": json.dumps(routing_message_json), "sender": str(self.id), "seq": self.get_time()}
            routing_message = json.dumps(routing_message_rv)
            #for n in self.neighbors:
                 #self.send_to_neighbor(n, routing_message)
            self.send_to_neighbors(routing_message)
            self.need_to_send = False
            # else:
            #     self.dv = tempt



    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        #print("cost is " + str(self.cost))
        #print("current dv " + str(self.dv))
        #print("current neighbour " + str(self.neighbor_dv))
        #print("neighbor "+str(self.neighbors))
        #print(self.dv.keys())
        if str(destination) not in self.dv.keys():
            return -1
        return int(self.dv[str(destination)]["path"][0])
