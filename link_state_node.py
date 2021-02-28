from simulator.node import Node
import json
import math
class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.nodes = {}
        self.seq = {}
        self.latest_msg = ""
        self.vertices = []

    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        #print("updating " + str(self.id) + " to " + str(neighbor))
        if self.id not in self.vertices:
            self.vertices.append(self.id)
        if neighbor not in self.vertices:
            self.vertices.append(neighbor)
        #routing_message = str([self.id, neighbor, self.seq_num, latency])
        self.nodes[frozenset([self.id,neighbor])] = latency
        self.seq[frozenset([self.id,neighbor])] = self.get_time()
        routing_message_dict = {}
        routing_message_dict["sender"] = self.id
        routing_message_dict["src"] = self.id
        routing_message_dict["dst"] = neighbor
        routing_message_dict["seq"] = self.get_time()
        routing_message_dict["cost"] = latency
        routing_message = json.dumps(routing_message_dict)
        self.latest_msg = routing_message
        
        # latency = -1 if delete a link
        if latency == -1 and neighbor in self.neighbors:
            #self.neighbors.remove(neighbor)
            self.nodes.pop(frozenset([self.id,neighbor]))
        # add new links
        if latency != -1 and neighbor not in self.neighbors:
            #self.neighbors.append(neighbor)
            self.send_to_neighbor(neighbor, routing_message)
        #print(self.nodes)
        #print("current seq is "+ str(self.seq_num))
        self.send_to_neighbors(routing_message)
        #print("neighbor are " + str(self.neighbors))
        self.logging.debug('link update, neighbor %d, latency %d, time %d' % (neighbor, latency, self.get_time()))

    # Fill in this function
    def process_incoming_routing_message(self, m):
        #print("current seq " + str(self.seq_num))
        
        #print(str(self.id) + "recevive a message")
        if self.id not in self.vertices:
            self.vertices.append(self.id)
        m_dict = json.loads(m)
        m_sender = m_dict["sender"]
        m_latency = m_dict["cost"]
        m_seq_num = m_dict["seq"]
        m_src = m_dict["src"]
        m_dst = m_dict["dst"]
        #if (m_src == 5 and m_dst == 1) or (m_src == 1 and m_dst == 5):
            #print(m)
        #print("received seq " + str(m_seq_num))
        if m_sender not in self.vertices:
            self.vertices.append(m_sender)
        if m_sender not in self.neighbors:
            self.neighbors.append(m_sender)
            for k in self.nodes.keys():
                routing_message_dict = {}
                routing_message_dict["sender"] = self.id
                routing_message_dict["src"] = list(k)[0]
                routing_message_dict["dst"] = list(k)[1]
                routing_message_dict["seq"] = self.seq[k]
                routing_message_dict["cost"] = self.nodes[k]
                routing_message = json.dumps(routing_message_dict)
                self.send_to_neighbor(m_sender, routing_message)    
        #print("current seq is "+ str(self.seq_num))
        #print("receive seq is "+ str(m_seq_num))
        #Old seq_num arrive: transmit the lastest version back
        latest_dict = json.loads(self.latest_msg)
        if frozenset([m_src,m_dst]) not in self.seq.keys() or self.seq[frozenset([m_src,m_dst])] < m_seq_num:
            if m_latency == -1:
                self.nodes.pop(frozenset([m_src,m_dst]))
            else:
                self.nodes[frozenset([m_src,m_dst])] = m_latency
            self.seq[frozenset([m_src,m_dst])] = m_seq_num
            m_dict["sender"] = self.id
            routing_message = json.dumps(m_dict)
            for neighbor in self.neighbors:
                if neighbor != m_sender:
                    self.send_to_neighbor(neighbor, routing_message)
        elif self.seq[frozenset([m_src,m_dst])] > m_seq_num:
            m_dict["cost"] = self.nodes[frozenset([m_src,m_dst])]
            m_dict["seq"] = self.seq[frozenset([m_src,m_dst])]
            m_dict["sender"] = self.id
            routing_message = json.dumps(m_dict)
            self.send_to_neighbor(m_sender, routing_message)
        #print(self.nodes)
        
        


        #New seq_num arrive: retransmit to other link
        # elif m_seq_num >= self.seq_num:
        #     self.seq_num = m_seq_num
        #     self.latest_msg = m
        #     latest_dict = json.loads(self.latest_msg)
        #     latest_dict["sender"] = self.id
        #     routing_message = json.dumps(latest_dict)
        #     self.nodes[frozenset([m_src,m_dst])] = m_latency
        #     for neighbor in self.neighbors:
        #         if neighbor != m_sender:
        #             self.send_to_neighbor(neighbor, routing_message)
        #Same seq_num arrive: do nothing
        #print(self.nodes)
        self.logging.debug("receive a message at Time %d. " % self.get_time() + m)


    def Dijkstra(self):
        #print("=======================================================================")
        uni = frozenset([])
        for pair in self.nodes.keys():
            uni = uni.union(pair)
        self.vertices = list(uni)
        #print(uni)
        #print(self.neighbors)
        #print(self.nodes)
        #print(self.vertices)
        dist = {}
        prev = {}
        for v in self.vertices:
            dist[v] = math.inf
            prev[v] = None
        dist[self.id] = 0
        unvisited = self.vertices.copy()
        #print("unvisited " + str(unvisited))
        sorted_dict = {}
        sorted_keys = sorted(dist, key=dist.get)
        for w in sorted_keys:
            sorted_dict[w] = dist[w]
        #print(sorted_dict)
        while len(unvisited) > 0:
            u = None
            sorted_keys = sorted(dist, key=dist.get)
            for k in sorted_keys:
                if u != None:
                    break
                if k in unvisited: 
                    u = k
            #print("we will remove" + str(u))
            unvisited.remove(u)
            for v in self.vertices:
                if frozenset([u,v]) in self.nodes.keys() and self.nodes[frozenset([u,v])] != -1:
                    #print("the neighbour is "+ str(v))
                    alt = dist[u] + self.nodes[frozenset([u,v])]
                    #print("distance is " + str(alt))
                    if alt < dist[v]:
                        dist[v] = alt
                        prev[v] = u
                    #print("new dist is " + str(dist))
                    #print("new prev is " + str(prev))
        return dist, prev

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        dist, prev = self.Dijkstra()
        next = destination
        while prev[next] != self.id:
            next = prev[next]
        return next


    
        
