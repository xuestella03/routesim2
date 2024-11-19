from simulator.node import Node

class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.neighbor_latencies = {}
        self.neighbor_dist_vecs = {}
        self.distances = {id: 0}
        self.next_hop = {id: id}

    def __str__(self):
        return f"id: {self.id}\ndistances: {self.distances}\nnext hops: {self.next_hop}"

    def link_has_been_updated(self, neighbor, latency):

        if latency == -1: # delete
            if neighbor in self.neighbor_latencies:
                del self.neighbor_latencies[neighbor]
                if neighbor in self.neighbor_dist_vecs:
                    del self.neighbor_dist_vecs[neighbor]
        else:
            if neighbor not in self.neighbor_latencies or self.neighbor_latencies[neighbor] != latency:
                self.neighbor_latencies[neighbor] = latency


        self.recompute_distances()
        self.send_distance_vector()

    def process_incoming_routing_message(self, m):

        parts = m.split(";")
        from_id = int(parts[0])

        new_vector = {}
        for part in parts[1:]:
            dest, dist = part.split(",")
            new_vector[int(dest)] = float(dist)

        # check if distance vector has changed
        if from_id not in self.neighbor_dist_vecs or self.neighbor_dist_vecs[from_id] != new_vector:
            self.neighbor_dist_vecs[from_id] = new_vector
            self.recompute_distances()
            self.send_distance_vector()


    def get_next_hop(self, destination):
        return self.next_hop.get(destination, -1)

    def recompute_distances(self):

        # reset distances
        self.distances = {self.id: 0}
        self.next_hop = {self.id: self.id}

        # direct neighbors
        for neighbor, latency in self.neighbor_latencies.items():
            self.distances[neighbor] = latency
            self.next_hop[neighbor] = neighbor

        # paths through neighbors
        for neighbor, neighbor_vector in self.neighbor_dist_vecs.items():

            if neighbor not in self.neighbor_latencies:
                continue

            neighbor_cost = self.neighbor_latencies[neighbor]

            # check each destination in neighbor's vector
            for dest, dest_cost in neighbor_vector.items():
                total_cost = neighbor_cost + dest_cost

                # update if better path
                if dest not in self.distances or total_cost < self.distances[dest]:
                    self.distances[dest] = total_cost
                    self.next_hop[dest] = neighbor

    def send_distance_vector(self):

        msg_parts = [str(self.id)]

        for dest, dist in self.distances.items():
            msg_parts.append(f"{dest},{dist}")

        message = ";".join(msg_parts)
        self.send_to_neighbors(message)