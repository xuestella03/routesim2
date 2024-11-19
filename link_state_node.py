# from networkx.classes import neighbors
# from tensorflow.python.ops.gen_experimental_dataset_ops import latency_stats_dataset
#
# from simulator.node import Node
#
#
# class Link_State_Node(Node):
#     def __init__(self, id):
#         super().__init__(id)
#         self.neighbors = {} # {neighbor_id: latency}
#         self.linkstatedb = {} # the link state db is the info the node knows about the network
#                               # {id: {neighbor_id: latency}}
#         self.shortest_paths = {} # {dest_id: (next_hop, cost)}
#         self.sequence_numbers = {}
#         # initialize your own entry
#         self.linkstatedb[self.id] = {}
#         self.sequence_numbers[self.id] = 0
#
#     # Return a string
#     def __str__(self):
#         res = f"id: {self.id}\n"
#         res += f"neighbors: {self.neighbors}\n"
#         res += f"db: {self.linkstatedb}\n"
#         res += f"paths: {self.shortest_paths}\n"
#         return res
#
#     # Fill in this function
#     def link_has_been_updated(self, neighbor, latency):
#         # latency = -1 if delete a link
#         if latency == -1:
#             if neighbor in self.neighbors:
#                 del self.neighbors[neighbor]
#
#         else:
#             self.neighbors[neighbor] = latency
#
#         # update sequence number
#         if self.id not in self.sequence_numbers:
#             self.sequence_numbers[self.id] = 0
#         self.sequence_numbers[self.id] += 1
#
#         # update link state db
#         self.linkstatedb[self.id] = self.neighbors.copy()
#
#         # update all neighbors
#         # for n in self.neighbors:
#         #     if n != self.id:
#         #         self.send_to_neighbor(n, f"{self.id} {self.sequence_numbers[self.id]} {self.linkstatedb[self.id]}")
#         self.send_to_neighbors(f"{self.id} {self.sequence_numbers[self.id]} {self.linkstatedb[self.id]}")
#
#     # Fill in this function
#     def process_incoming_routing_message(self, m):
#         # sender, linkstate_str = m.split(" ", 1)
#         # linkstate = eval(linkstate_str)
#
#         parts = m.split(" ", 2)
#         sender = parts[0]
#         seq_num = int(parts[1])
#         linkstate = eval(parts[2])
#
#         # if sender not in self.linkstatedb or self.linkstatedb[sender] != linkstate:
#         #     self.linkstatedb[sender] = linkstate
#         #
#         #     # send message to all neighbors except the sender
#         #     for n in self.linkstatedb[self.id]:
#         #         if n != sender:
#         #             self.send_to_neighbor(n, f"{sender} {linkstate}")
#         if (sender not in self.sequence_numbers or
#                 seq_num > self.sequence_numbers[sender] or
#                 sender not in self.linkstatedb or
#                 self.linkstatedb[sender] != linkstate):
#
#             # Update sequence number and link state
#             self.sequence_numbers[sender] = seq_num
#             self.linkstatedb[sender] = linkstate
#
#             # Forward to all neighbors except the one we received from
#             message = f"{sender} {seq_num} {linkstate}"
#             for n in self.neighbors:
#                 if n != sender:  # Don't send back to sender
#                     self.send_to_neighbor(n, message)
#
#     # Return a neighbor, -1 if no path to destination
#     def get_next_hop(self, destination):
#
#         # if no path
#         if destination not in self.linkstatedb:
#             return -1
#
#         # otherwise use Dijsktra's
#         unvisited = set(self.linkstatedb.keys())
#         distances = {node: float('inf') for node in unvisited}
#         prev = {node: None for node in unvisited}
#
#         distances[self.id] = 0
#
#         while unvisited:
#             cur = min(unvisited, key=lambda node: distances[node])
#
#             if distances[cur] == float('inf'): # nothing else is reachable
#                 break
#
#             unvisited.remove(cur)
#
#             for n, l in self.linkstatedb.get(cur, {}).items():
#                 if n in unvisited:
#                     new_dist = distances[cur] + l
#                     if new_dist < distances[n]:
#                         distances[n] = new_dist
#                         prev[n] = cur
#
#         if distances[destination] == float('inf'):
#             return -1
#
#         path = []
#         cur = destination
#         while cur is not None:
#             path.insert(0, cur)
#             cur = prev[cur]
#
#         if len(path) > 1 and path[0] == self.id:
#             return path[1]
#
#         else:
#             return -1
#
# from simulator.node import Node
#
# class Link_State_Node(Node):
#     def __init__(self, id):
#         super().__init__(id)
#         self.neighbors = {}
#         self.linkstatedb = {}
#         self.shortest_paths = {}
#         self.sequence_numbers = {}
#         self.linkstatedb[self.id] = {}
#         self.sequence_numbers[self.id] = 0
#         self.MAX_SEQUENCE = 2**32 - 1
#
#     def __str__(self):
#         res = f"id: {self.id}\n"
#         res += f"neighbors: {self.neighbors}\n"
#         res += f"db: {self.linkstatedb}\n"
#         res += f"paths: {self.shortest_paths}\n"
#         return res
#
#     def link_has_been_updated(self, neighbor, latency):
#         if latency == -1:
#             if neighbor in self.neighbors:
#                 del self.neighbors[neighbor]
#         else:
#             self.neighbors[neighbor] = latency
#
#         if self.id not in self.sequence_numbers:
#             self.sequence_numbers[self.id] = 0
#         self.sequence_numbers[self.id] = (self.sequence_numbers[self.id] + 1) % self.MAX_SEQUENCE
#
#         self.linkstatedb[self.id] = self.neighbors.copy()
#
#         message = f"{self.id} {self.sequence_numbers[self.id]} {self.linkstatedb[self.id]}"
#         self.send_to_neighbors(message)
#
#     def process_incoming_routing_message(self, m):
#         try:
#             parts = m.split(" ", 2)
#             if len(parts) != 3:
#                 return
#
#             sender = parts[0]
#             seq_num = int(parts[1])
#             linkstate = eval(parts[2])
#
#             current_seq = self.sequence_numbers.get(sender, 0)
#             is_newer = (seq_num > current_seq and seq_num - current_seq <= self.MAX_SEQUENCE//2) or \
#                       (seq_num < current_seq and current_seq - seq_num > self.MAX_SEQUENCE//2)
#
#             if (sender not in self.sequence_numbers or
#                     is_newer or
#                     sender not in self.linkstatedb or
#                     self.linkstatedb[sender] != linkstate):
#
#                 self.sequence_numbers[sender] = seq_num
#                 self.linkstatedb[sender] = linkstate
#
#                 message = f"{sender} {seq_num} {linkstate}"
#                 for n in self.neighbors:
#                     if n != sender:
#                         self.send_to_neighbor(n, message)
#
#         except (ValueError, SyntaxError) as e:
#             return
#
#     def get_next_hop(self, destination):
#         if destination not in self.linkstatedb or destination == self.id:
#             return -1
#
#         unvisited = set(self.linkstatedb.keys())
#         distances = {node: float('inf') for node in unvisited}
#         prev = {node: None for node in unvisited}
#
#         distances[self.id] = 0
#
#         while unvisited:
#             cur = min(unvisited, key=lambda node: distances[node])
#
#             if distances[cur] == float('inf'):
#                 break
#
#             unvisited.remove(cur)
#
#             for n, l in self.linkstatedb.get(cur, {}).items():
#                 if n in unvisited:
#                     new_dist = distances[cur] + l
#                     if new_dist < distances[n]:
#                         distances[n] = new_dist
#                         prev[n] = cur
#
#         if distances[destination] == float('inf'):
#             return -1
#
#         path = []
#         cur = destination
#         while cur is not None:
#             path.insert(0, cur)
#             cur = prev[cur]
#
#         if len(path) > 1 and path[0] == self.id:
#             return path[1]
#         return -1

# from simulator.node import Node
#
#
# class Link_State_Node(Node):
#     def __init__(self, id):
#         super().__init__(id)
#         self.neighbor_latencies = {}  # Direct neighbors and their latencies
#         self.topology = {}  # Network topology
#         self.next_hop = {}  # Next hop for each destination
#         self.seen_messages = set()  # Track seen LSAs
#         self.topology[id] = {}  # Initialize own topology entry
#
#     def __str__(self):
#         return f"Node {self.id}\nTopology: {self.topology}\nNext hops: {self.next_hop}"
#
#     def link_has_been_updated(self, neighbor, latency):
#         # Update direct neighbor latency
#         if latency == -1:
#             if neighbor in self.neighbor_latencies:
#                 del self.neighbor_latencies[neighbor]
#             if neighbor in self.topology[self.id]:
#                 del self.topology[self.id][neighbor]
#         else:
#             self.neighbor_latencies[neighbor] = latency
#             if self.id not in self.topology:
#                 self.topology[self.id] = {}
#             self.topology[self.id][neighbor] = latency
#
#             # Ensure neighbor exists in topology
#             if neighbor not in self.topology:
#                 self.topology[neighbor] = {}
#             self.topology[neighbor][self.id] = latency
#
#         # Create and flood LSA
#         message = f"LSA:{self.id}:{neighbor}:{latency}"
#         self.send_to_neighbors(message)
#
#         # Update routing
#         self._run_dijkstra()
#
#     def process_incoming_routing_message(self, m):
#         if m in self.seen_messages:
#             return
#
#         self.seen_messages.add(m)
#         parts = m.split(":")
#
#         if parts[0] == "LSA":
#             source = int(parts[1])
#             neighbor = int(parts[2])
#             latency = float(parts[3])
#
#             # Create topology entries if needed
#             if source not in self.topology:
#                 self.topology[source] = {}
#             if neighbor not in self.topology:
#                 self.topology[neighbor] = {}
#
#             # Update topology
#             if latency == -1:
#                 if neighbor in self.topology[source]:
#                     del self.topology[source][neighbor]
#                 if source in self.topology[neighbor]:
#                     del self.topology[neighbor][source]
#             else:
#                 self.topology[source][neighbor] = latency
#                 self.topology[neighbor][source] = latency
#
#             # Forward the LSA
#             self.send_to_neighbors(m)
#
#             # Update routing
#             self._run_dijkstra()
#
#     def get_next_hop(self, destination):
#         if destination not in self.topology:
#             return -1
#         if destination in self.next_hop:
#             return self.next_hop[destination]
#         return -1
#
#     def _run_dijkstra(self):
#         # Initialize data structures
#         dist = {}  # Shortest distance to each node
#         prev = {}  # Previous node in optimal path
#         unvisited = set()  # Set of unvisited nodes
#
#         # Initialize distances
#         for node in self.topology:
#             dist[node] = float('inf')
#             prev[node] = None
#             unvisited.add(node)
#         dist[self.id] = 0
#
#         while unvisited:
#             # Find closest unvisited node
#             u = None
#             min_dist = float('inf')
#             for node in unvisited:
#                 if dist[node] < min_dist:
#                     min_dist = dist[node]
#                     u = node
#
#             if u is None or dist[u] == float('inf'):
#                 break
#
#             unvisited.remove(u)
#
#             # Update distances to neighbors
#             if u in self.topology:
#                 for v, weight in self.topology[u].items():
#                     if v in unvisited:
#                         alt = dist[u] + weight
#                         if alt < dist[v]:
#                             dist[v] = alt
#                             prev[v] = u
#
#         # Build routing table
#         self.next_hop = {}
#         for dest in self.topology:
#             if dest == self.id:
#                 continue
#
#             if dist[dest] == float('inf'):
#                 continue
#
#             # Reconstruct path
#             path = []
#             current = dest
#             while current is not None and current != self.id:
#                 path.append(current)
#                 current = prev[current]
#
#             if current == self.id and path:  # Found a valid path
#                 # Set next hop as first node in path from us to destination
#                 self.next_hop[dest] = path[-1]
#
#             # Direct neighbor case
#             if dest in self.neighbor_latencies:
#                 self.next_hop[dest] = dest

# from simulator.node import Node
# import json
#
#
# class Link_State_Node(Node):
#     def __init__(self, id):
#         super().__init__(id)
#         # Dictionary to store direct link costs to neighbors
#         self.neighbor_latencies = {}
#         # Dictionary to store the network topology (node -> {neighbor -> cost})
#         self.network_topology = {id: {}}
#         # Dictionary to store sequence numbers for each node's LSAs
#         self.sequence_numbers = {}
#         # Dictionary to store shortest paths
#         self.shortest_paths = {}
#         # Initialize sequence number for this node
#         self.sequence_numbers[id] = 0
#
#     def __str__(self):
#         paths = {dest: self.get_next_hop(dest) for dest in self.shortest_paths}
#         return f"Node {self.id}\nTopology: {self.network_topology}\nNext hops: {paths}"
#
#     def link_has_been_updated(self, neighbor, latency):
#         """Handle link updates by updating topology and running Dijkstra's algorithm"""
#         changed = False
#
#         if latency == -1:  # Link is being deleted
#             if neighbor in self.neighbor_latencies:
#                 del self.neighbor_latencies[neighbor]
#                 # Update our view of the topology
#                 if self.id in self.network_topology:
#                     self.network_topology[self.id].pop(neighbor, None)
#                 if neighbor in self.network_topology:
#                     self.network_topology[neighbor].pop(self.id, None)
#                 changed = True
#         else:  # Link is being added or updated
#             if neighbor not in self.neighbor_latencies or self.neighbor_latencies[neighbor] != latency:
#                 self.neighbor_latencies[neighbor] = latency
#                 # Update our view of the topology
#                 if self.id not in self.network_topology:
#                     self.network_topology[self.id] = {}
#                 if neighbor not in self.network_topology:
#                     self.network_topology[neighbor] = {}
#                 self.network_topology[self.id][neighbor] = latency
#                 self.network_topology[neighbor][self.id] = latency  # Add reverse link
#                 changed = True
#
#         if changed:
#             # Increment sequence number
#             self.sequence_numbers[self.id] = self.sequence_numbers.get(self.id, 0) + 1
#             # Send LSA to neighbors
#             self._send_link_state_advertisement()
#             # Recompute shortest paths
#             self._run_dijkstra()
#
#     def process_incoming_routing_message(self, m):
#         """Process incoming LSA from a neighbor"""
#         try:
#             # Parse message format: JSON containing node_id, seq_num, and neighbors
#             lsa = json.loads(m)
#             node_id = lsa['node_id']
#             seq_num = lsa['seq_num']
#             neighbors = lsa['neighbors']
#
#             # Check if this is a newer LSA
#             if node_id not in self.sequence_numbers or seq_num > self.sequence_numbers[node_id]:
#                 # Update sequence number
#                 self.sequence_numbers[node_id] = seq_num
#
#                 # Update topology - ensure bidirectional links
#                 self.network_topology[node_id] = neighbors.copy()
#                 for neighbor, cost in neighbors.items():
#                     if neighbor not in self.network_topology:
#                         self.network_topology[neighbor] = {}
#                     self.network_topology[neighbor][node_id] = cost
#
#                 # Forward LSA to neighbors
#                 self.send_to_neighbors(m)
#                 # Recompute shortest paths
#                 self._run_dijkstra()
#
#         except (json.JSONDecodeError, KeyError):
#             # Ignore malformed messages
#             pass
#
#     def get_next_hop(self, destination):
#         """Return next hop for reaching destination"""
#         if destination in self.shortest_paths:
#             path = self.shortest_paths[destination]
#             if len(path) > 1:
#                 return path[1]  # First hop after current node
#             elif len(path) == 1 and path[0] == destination:
#                 return destination  # Destination is directly connected
#         return -1
#
#     def _run_dijkstra(self):
#         """Run Dijkstra's algorithm to compute shortest paths to all nodes"""
#         # Initialize data structures
#         distances = {self.id: 0}
#         paths = {self.id: [self.id]}
#         unvisited = set(self.network_topology.keys())
#         visited = set()
#
#         while unvisited:
#             # Find unvisited node with minimum distance
#             current = min(unvisited, key=lambda x: distances.get(x, float('inf')))
#             current_distance = distances.get(current, float('inf'))
#
#             # If remaining nodes are unreachable, break
#             if current_distance == float('inf'):
#                 break
#
#             # Add current node to visited set
#             visited.add(current)
#             unvisited.remove(current)
#
#             # Check all neighbors of current node
#             if current in self.network_topology:
#                 for neighbor, weight in self.network_topology[current].items():
#                     if neighbor not in visited:
#                         distance = current_distance + weight
#
#                         # Update distance if shorter path is found
#                         if distance < distances.get(neighbor, float('inf')):
#                             distances[neighbor] = distance
#                             paths[neighbor] = paths[current] + [neighbor]
#
#         # Store computed paths
#         self.shortest_paths = paths
#
#     def _send_link_state_advertisement(self):
#         """Send LSA to all neighbors"""
#         # Construct LSA
#         lsa = {
#             'node_id': self.id,
#             'seq_num': self.sequence_numbers[self.id],
#             'neighbors': self.network_topology[self.id]
#         }
#
#         # Convert to JSON and send
#         message = json.dumps(lsa)
#         self.send_to_neighbors(message)

from simulator.node import Node
import json


class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        # Store link state information: {frozenset([src, dst]): (cost, seq_num)}
        self.link_state_db = {}
        # Store shortest path information
        self.routing_table = {}
        # Store neighbors and their latencies
        self.neighbors = {}

    def __str__(self):
        # Convert frozensets to lists for JSON serialization
        link_state_dict = {
            f"{min(k)}-{max(k)}": v
            for k, v in self.link_state_db.items()
        }
        return f"Node {self.id}\nLink State DB: {json.dumps(link_state_dict, indent=2)}\nRouting Table: {json.dumps(self.routing_table, indent=2)}"

    def link_has_been_updated(self, neighbor, latency):
        # Get current sequence number or start at 0
        current_link = frozenset([self.id, neighbor])
        seq_num = self.link_state_db.get(current_link, (0, -1))[1] + 1

        if latency == -1:
            # Link deletion
            if current_link in self.link_state_db:
                del self.link_state_db[current_link]
                if neighbor in self.neighbors:
                    del self.neighbors[neighbor]
        else:
            # Link addition or update
            self.link_state_db[current_link] = (latency, seq_num)
            self.neighbors[neighbor] = latency

            # Share entire link state database with new neighbor
            for link, (cost, seq) in self.link_state_db.items():
                src, dst = link
                message = {
                    "type": "LSM",
                    "source": self.id,
                    "link_source": min(src, dst),
                    "link_dest": max(src, dst),
                    "cost": cost,
                    "seq_num": seq
                }
                self.send_to_neighbor(neighbor, json.dumps(message))

        # Create and broadcast current link update message
        message = {
            "type": "LSM",
            "source": self.id,
            "link_source": min(self.id, neighbor),
            "link_dest": max(self.id, neighbor),
            "cost": latency,
            "seq_num": seq_num
        }

        # Broadcast to all neighbors except the updated one
        for n in self.neighbors:
            if n != neighbor:
                self.send_to_neighbor(n, json.dumps(message))

        # Recalculate shortest paths
        self.calculate_shortest_paths()

    def process_incoming_routing_message(self, m):
        try:
            msg = json.loads(m)
            if msg["type"] != "LSM":
                return

            link = frozenset([msg["link_source"], msg["link_dest"]])
            current_seq = self.link_state_db.get(link, (0, -1))[1]

            if msg["seq_num"] > current_seq:
                # New or newer information - update and flood
                self.link_state_db[link] = (msg["cost"], msg["seq_num"])

                # Flood to all neighbors except the one we received from
                for neighbor in self.neighbors:
                    if neighbor != msg["source"]:
                        self.send_to_neighbor(neighbor, m)

                # Recalculate shortest paths
                self.calculate_shortest_paths()

            elif msg["seq_num"] < current_seq:
                # We have newer information - send it back
                newer_message = {
                    "type": "LSM",
                    "source": self.id,
                    "link_source": min(msg["link_source"], msg["link_dest"]),
                    "link_dest": max(msg["link_source"], msg["link_dest"]),
                    "cost": self.link_state_db[link][0],
                    "seq_num": self.link_state_db[link][1]
                }
                self.send_to_neighbor(msg["source"], json.dumps(newer_message))

        except (json.JSONDecodeError, KeyError):
            pass

    def get_next_hop(self, destination):
        return self.routing_table.get(destination, -1)

    def calculate_shortest_paths(self):
        # Initialize variables for Dijkstra's algorithm
        distances = {self.id: 0}
        predecessors = {self.id: None}
        unvisited = set()

        # Build graph from link state database
        graph = {}
        for link, (cost, _) in self.link_state_db.items():
            if cost != -1:  # Skip deleted links
                src, dst = link
                if src not in graph:
                    graph[src] = {}
                    unvisited.add(src)
                if dst not in graph:
                    graph[dst] = {}
                    unvisited.add(dst)
                graph[src][dst] = cost
                graph[dst][src] = cost

        # Add current node to unvisited if not already there
        unvisited.add(self.id)

        # Main Dijkstra loop
        while unvisited:
            # Find unvisited node with minimum distance
            current = min(
                (node for node in unvisited if node in distances),
                key=lambda x: distances[x],
                default=None
            )

            if current is None:
                break

            unvisited.remove(current)
            current_distance = distances[current]

            # Update distances to neighbors
            if current in graph:
                for neighbor, cost in graph[current].items():
                    new_distance = current_distance + cost
                    if new_distance < distances.get(neighbor, float('inf')):
                        distances[neighbor] = new_distance
                        predecessors[neighbor] = current

        # Build routing table
        self.routing_table = {}
        for dest in distances:
            if dest != self.id:
                # Trace back through predecessors to find first hop
                current = dest
                while predecessors.get(current) != self.id and predecessors.get(current) is not None:
                    current = predecessors[current]
                if predecessors.get(current) == self.id:
                    self.routing_table[dest] = current