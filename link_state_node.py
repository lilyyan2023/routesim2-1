from simulator.node import Node
import json
import math
class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.nodes = {}
        self.seq_num = 0
        self.latest_msg = ""
        self.vertices = []

    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        if self.id not in self.vertices:
            self.vertices.append(self.id)
        if neighbor not in self.vertices:
            self.vertices.append(neighbor)
        self.seq_num += 1
        #routing_message = str([self.id, neighbor, self.seq_num, latency])
        routing_message_dict = {}
        routing_message_dict["sender"] = self.id
        routing_message_dict["src"] = self.id
        routing_message_dict["dst"] = neighbor
        routing_message_dict["seq"] = self.seq_num
        routing_message_dict["cost"] = latency
        routing_message = json.dumps(routing_message_dict)
        self.latest_msg = routing_message
        self.nodes[frozenset([self.id,neighbor])] = latency
        self.send_to_neighbors(routing_message)
        # latency = -1 if delete a link
        if latency == -1 and neighbor in self.neighbors:
            self.neighbors.remove(neighbor)
        # add new links
        if latency != -1 and neighbor not in self.neighbors:
            self.neighbors.append(neighbor)

        self.logging.debug('link update, neighbor %d, latency %d, time %d' % (neighbor, latency, self.get_time()))

    # Fill in this function
    def process_incoming_routing_message(self, m):
        if self.id not in self.vertices:
            self.vertices.append(self.id)
        m_dict = json.loads(m)
        m_sender = m_dict["sender"]
        m_latency = m_dict["cost"]
        m_seq_num = m_dict["seq"]
        m_src = m_dict["src"]
        m_dst = m_dict["dst"]
        #Old seq_num arrive: transmit the lastest version back
        if m_seq_num < self.seq_num:
            latest_dict = json.loads(self.latest_msg)
            latest_dict["sender"] = self.id
            routing_message = json.dumps(latest_dict)
            self.send_to_neighbor(m_sender, routing_message)
        #New seq_num arrive: retransmit to other link
        elif m_seq_num > self.seq_num:
            self.seq_num = m_seq_num
            self.latest_msg = m
            latest_dict = json.loads(self.latest_msg)
            latest_dict["sender"] = self.id
            routing_message = json.dumps(latest_dict)
            self.nodes[frozenset([m_src,m_dst])] = m_latency
            for neighbor in self.neighbors:
                if neighbor != m_sender:
                    self.send_to_neighbor(neighbor, routing_message)
        #Same seq_num arrive: do nothing
        self.logging.debug("receive a message at Time %d. " % self.get_time() + m)


    def Dijkstra(self):
        print(self.nodes)
        dist = {}
        prev = {}
        for v in self.vertices:
            dist[v] = math.inf
            prev[v] = None
        dist[self.id] = 0
        unvisited = self.vertices.copy()
        sorted_dict = {}
        sorted_keys = sorted(dist, key=dist.get)
        for w in sorted_keys:
            sorted_dict[w] = dist[w]
        print(sorted_dict)
        while len(unvisited) > 0:
            u = None
            for k in sorted_keys:
                if k in unvisited: 
                    u = k
            print("we will remove" + str(u))
            unvisited.remove(u)
            for v in self.vertices:
                if frozenset([u,v]) in self.nodes.keys() and self.nodes[frozenset([u,v])] != -1:
                    print("the neighbour is "+ str(v))
                    alt = dist[u] + self.nodes[frozenset([u,v])]
                    print("distance is " + str(alt))
                    if alt < dist[v]:
                        dist[v] = alt
                        prev[v] = u
        return dist, prev

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        dist, prev = self.Dijkstra()
        next = destination
        while prev[next] != self.id:
            next = prev[next]
        return next


    
        
