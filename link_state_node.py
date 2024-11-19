from simulator.node import Node

class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)

        # link state info: (src, dest): (cost, seq_num)
        self.lsdb = {}

        # shortest path info
        self.routing_table = {}

        # store neighbors and latencies
        self.neighbors = {}

    def __str__(self):

        return f"id: {self.id}\ndb: {self.lsdb}\nrouting table: {self.routing_table}"

    def link_has_been_updated(self, neighbor, latency):

        cur_link = frozenset([self.id, neighbor])
        # update sequence number
        seq_num = self.lsdb.get(cur_link, (0, -1))[1] + 1

        if latency == -1: # delete
            if cur_link in self.lsdb:
                del self.lsdb[cur_link]
                if neighbor in self.neighbors:
                    del self.neighbors[neighbor]

        else:
            self.lsdb[cur_link] = (latency, seq_num)
            self.neighbors[neighbor] = latency

            # share with neighbor
            for link, (cost, seq) in self.lsdb.items():
                src, dst = min(link), max(link)
                message = f"{self.id},{src},{dst},{cost},{seq}"
                self.send_to_neighbor(neighbor, message)

        # update other neighbors
        message = f"{self.id},{min(self.id, neighbor)},{max(self.id, neighbor)},{latency},{seq_num}"
        for n in self.neighbors:
            if n != neighbor:
                self.send_to_neighbor(n, message)

        self.dijsktra()

    def process_incoming_routing_message(self, m: str):
        src, link_src, link_dst, cost, seq_num = m.split(",")
        src = int(src)
        link_src = int(link_src)
        link_dst = int(link_dst)
        cost = int(cost)
        seq_num = int(seq_num)

        link = frozenset([link_src, link_dst])

        cur_seq = self.lsdb.get(link, (0, -1))[1]

        if seq_num > cur_seq: # the message is newer info so we need to update
            self.lsdb[link] = (cost, seq_num)
            for n in self.neighbors:
                if n != src:
                    self.send_to_neighbor(n, m)
            self.dijsktra()

        elif seq_num < cur_seq: # the info from the message is outdated so we need to update the sender
            message = f"{self.id},{min(link_src, link_dst)},{max(link_src, link_dst)},{self.lsdb[link][0]},{self.lsdb[link][1]}"
            self.send_to_neighbor(src, message)

    def get_next_hop(self, destination):
        return self.routing_table.get(destination, -1)

    def dijsktra(self):

        distances = {self.id: 0}
        prev = {self.id: 0}
        unvisited = set()

        graph = {}
        for link, (cost, _) in self.lsdb.items():
            if cost != -1:
                src, dst = link
                if src not in graph:
                    graph[src] = {}
                    unvisited.add(src)
                if dst not in graph:
                    graph[dst] = {}
                    unvisited.add(dst)
                graph[src][dst] = cost
                graph[dst][src] = cost
        unvisited.add(self.id)

        while unvisited:
            # get closest
            cur = min((node for node in unvisited if node in distances), key=lambda x: distances[x], default=None)
            if cur is None:
                break
            unvisited.remove(cur)
            cur_dist = distances[cur]

            # update distances
            if cur in graph:
                for n, c in graph[cur].items():
                    new_dist = cur_dist + c
                    if new_dist < distances.get(n, float('inf')):
                        distances[n] = new_dist
                        prev[n] = cur

        # backtrack
        self.routing_table = {}
        for d in distances:
            if d != self.id:
                cur = d
                while prev.get(cur) != self.id and prev.get(cur) is not None:
                    cur = prev[cur]
                if prev.get(cur) == self.id:
                    self.routing_table[d] = cur

