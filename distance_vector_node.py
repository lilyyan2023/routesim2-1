from simulator.node import Node
import copy

class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.dv = {}
        self.neighbor_dv = {}
        self.cost

    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        if neighbor not in self.dv.keys():
            self.dv[neighbor] = {"cost": latency, "path": [neighbor]}
        self.compute_shortest_path(neighbor, latency)
        self.dv[neighbor]["cost"] = latency


        routing_message = self.dv
    def compute_shortest_path(self):
        for neighbor in self.dv.keys():

            neighbor_dv = self.neighbor_dv[neighbor]
            for dst in neighbor_dv.keys():
                if latency + neighbor_dv[dst] < self.dv[dst]["cost"]:
                    self.dv[dst]["cost"] = latency + neighbor_dv[dst]
                    self.dv[dst]["path"] = copy.deepcopy(neighbor_dv[dst]["path"]).insert(neighbor)



    # Fill in this function
    def process_incoming_routing_message(self, m):
        pass

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        return -1
