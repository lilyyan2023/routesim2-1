from simulator.node import Node
import json

class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.nodes = {}
        self.seq_num = 0

    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        self.seq_num += 1
        routing_message = str([self.node1, self.node2, self.seq_num, latency])
        routing_message_json = json.loads(routing_message)
        # latency = -1 if delete a link
        if latency == -1 and neighbor in self.neighbors:
            self.send_to_neighbor(neighbor, routing_message_json)
            self.neighbors.remove(neighbor)
        # update already existing neighbors
        elif neighbor in self.neighbors:
            self.send_to_neighbor(neighbor, routing_message_json)
        # add new links
        else:
            self.neighbors.append(neighbor)
            # self.send_to_neighbors("hello")
            self.send_to_neighbor(neighbor, routing_message_json)
        self.nodes[neighbor] = latency

        self.logging.debug('link update, neighbor %d, latency %d, time %d' % (neighbor, latency, self.get_time()))

    # Fill in this function
    def process_incoming_routing_message(self, m):
        m_str = json.dumps(m)
        m_latency = m_str[3]
        m_seq_num = m_str[2]
        m_origin = m_str[0]
        if m_seq_num < self.seq_num:
            routing_message = str([self.node1, self.node2, self.seq_num, m_latency])
            routing_message_json = json.loads(routing_message)
            self.send_to_neighbor(m_origin, routing_message_json)
        elif m_seq_num > self.seq_num:
            routing_message = str([self.node1, self.node2, self.seq_num, m_latency])
            routing_message_json = json.loads(routing_message)
            for neighbor in self.neighbors:
                self.send_to_neighbor(neighbor, routing_message_json)
        self.nodes[] = int(m_str)
        self.seq_num += 1
        self.logging.debug("receive a message at Time %d. " % self.get_time() + m)

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        if self.neighbors != []:
            return self.neighbors[0]
        return -1
