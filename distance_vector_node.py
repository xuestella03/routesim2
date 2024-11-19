# from simulator.node import Node
# import ast
#
#
# class Distance_Vector_Node(Node):
#     def __init__(self, id):
#         super().__init__(id)
#         self.routing_table = {} # {destination: (cost, next_hop)}
#         self.neighbors = {} # {neighbor_id: latency}
#
#     # Return a string
#     def __str__(self):
#         neighbors_str = ", ".join([f"({neighbor}, {latency})" for neighbor, latency in self.neighbors.items()])
#         routing_table_str = ", ".join([f"{destination}: (cost: {cost_to_dest}, next hop: {next_hop})"
#                                        for destination, (cost_to_dest, next_hop) in self.routing_table.items()])
#
#         return (f"Node {self.id}\n"
#                 f"Neighbors: {neighbors_str}\n"
#                 f"Routing Table: {routing_table_str}")
#
#     # Fill in this function
#     def link_has_been_updated(self, neighbor, latency):
#         # latency = -1 if delete a link
#         if latency == -1:
#             if neighbor in self.neighbors:
#                 del self.neighbors[neighbor]
#                 # Remove routes that went through this neighbor
#                 for dest in list(self.routing_table.keys()):
#                     if self.routing_table[dest][1] == neighbor:
#                         del self.routing_table[dest]
#
#         else:
#             old_latency = self.neighbors[neighbor] if neighbor in self.neighbors else float('inf')
#
#             # If cost increased, remove affected routes first
#             if latency > old_latency:
#                 for dest in list(self.routing_table.keys()):
#                     if self.routing_table[dest][1] == neighbor:
#                         del self.routing_table[dest]
#
#             # Update neighbor link and direct route
#             self.neighbors[neighbor] = latency
#             self.routing_table[neighbor] = (latency, neighbor)
#
#         # Make sure we keep route to self
#         self.routing_table[self.id] = (0, self.id)
#
#         # Share routing table after changes
#         routing_message = f"{self.id} {str(self.routing_table)}"
#         self.send_to_neighbors(routing_message)
#
#     # Fill in this function
#     def process_incoming_routing_message(self, m):
#         try:
#             sender, table_str = m.split(" ", 1)
#             sender = int(sender)
#             received_table = ast.literal_eval(table_str)
#
#             if sender not in self.neighbors:
#                 return
#
#             updated = False
#             sender_cost = self.neighbors[sender]
#
#             # Process each destination in received table
#             for dest, (cost, next_hop) in received_table.items():
#                 if dest == self.id:  # Skip routes to self
#                     continue
#
#                 # Calculate total cost to reach destination through sender
#                 total_cost = sender_cost + cost
#
#                 # Update if we don't have a route or if this route is better
#                 if dest not in self.routing_table or total_cost < self.routing_table[dest][0]:
#                     self.routing_table[dest] = (total_cost, sender)
#                     updated = True
#                 elif total_cost == self.routing_table[dest][0] and sender < self.routing_table[dest][1]:
#                     # If costs are equal, prefer the path through the lower-numbered node
#                     self.routing_table[dest] = (total_cost, sender)
#                     updated = True
#
#             # Only propagate if we made changes
#             if updated:
#                 routing_message = f"{self.id} {str(self.routing_table)}"
#                 self.send_to_neighbors(routing_message)
#
#         except Exception as e:
#             print(f"Error processing message: {e}")
#
#     # Return a neighbor, -1 if no path to destination
#     def get_next_hop(self, destination):
#         if destination in self.routing_table:
#             return self.routing_table[destination][1]
#         return -1

from simulator.node import Node


class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        # Dictionary to store direct link costs to neighbors
        self.neighbor_latencies = {}
        # Dictionary to store distance vectors received from neighbors
        self.neighbor_distance_vectors = {}
        # Dictionary to store shortest known distance to each destination
        self.distances = {}
        # Dictionary to store next hop for each destination
        self.next_hop = {}
        # Initialize distance to self as 0
        self.distances[id] = 0
        self.next_hop[id] = id

    def __str__(self):
        return f"Node {self.id}\nDistances: {self.distances}\nNext hops: {self.next_hop}"

    def link_has_been_updated(self, neighbor, latency):
        """Handle link updates by updating costs and recalculating distances"""
        # Update neighbor latency
        changed = False

        if latency == -1:  # Link is being deleted
            if neighbor in self.neighbor_latencies:
                del self.neighbor_latencies[neighbor]
                if neighbor in self.neighbor_distance_vectors:
                    del self.neighbor_distance_vectors[neighbor]
                changed = True
        else:  # Link is being added or updated
            if neighbor not in self.neighbor_latencies or self.neighbor_latencies[neighbor] != latency:
                self.neighbor_latencies[neighbor] = latency
                changed = True

        if changed:
            # Recalculate distances
            self._recompute_distances()
            # Send distance vector to neighbors
            self._send_distance_vector()

    def process_incoming_routing_message(self, m):
        """Process incoming distance vector from a neighbor"""
        try:
            # Parse message format: "from_id:dest1,dist1:dest2,dist2:..."
            parts = m.split(":")
            from_id = int(parts[0])

            # Only process if this is from a current neighbor
            if from_id not in self.neighbor_latencies:
                return

            # Parse distance vector
            new_vector = {}
            for part in parts[1:]:
                if part:  # Skip empty parts
                    dest, dist = part.split(",")
                    new_vector[int(dest)] = float(dist)

            # Check if distance vector has changed
            if from_id not in self.neighbor_distance_vectors or \
                    self.neighbor_distance_vectors[from_id] != new_vector:
                # Update stored vector
                self.neighbor_distance_vectors[from_id] = new_vector
                # Recalculate distances
                self._recompute_distances()
                # Send updated distance vector to neighbors
                self._send_distance_vector()

        except (ValueError, IndexError):
            # Ignore malformed messages
            pass

    def get_next_hop(self, destination):
        """Return next hop for reaching destination"""
        if destination in self.next_hop:
            return self.next_hop[destination]
        return -1

    def _recompute_distances(self):
        """Recompute the distance vector using the Bellman-Ford equation"""
        # Save old distances for comparison
        old_distances = self.distances.copy()

        # Reset distances (except to self)
        self.distances = {self.id: 0}
        self.next_hop = {self.id: self.id}

        # Direct neighbors
        for neighbor, latency in self.neighbor_latencies.items():
            self.distances[neighbor] = latency
            self.next_hop[neighbor] = neighbor

        # Consider paths through neighbors
        for neighbor, neighbor_vector in self.neighbor_distance_vectors.items():
            # Skip if neighbor link is down
            if neighbor not in self.neighbor_latencies:
                continue

            # Get cost to this neighbor
            neighbor_cost = self.neighbor_latencies[neighbor]

            # Check each destination in neighbor's vector
            for dest, dest_cost in neighbor_vector.items():
                total_cost = neighbor_cost + dest_cost

                # Update if this is a better path
                if dest not in self.distances or total_cost < self.distances[dest]:
                    self.distances[dest] = total_cost
                    self.next_hop[dest] = neighbor

    def _send_distance_vector(self):
        """Send distance vector to all neighbors"""
        # Construct message
        msg_parts = [str(self.id)]  # Start with our ID

        # Add each destination and distance
        for dest, dist in self.distances.items():
            msg_parts.append(f"{dest},{dist}")

        # Join with colons
        message = ":".join(msg_parts)

        # Send to all neighbors
        self.send_to_neighbors(message)