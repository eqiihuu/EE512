# This is a file to define the Classes for Markov Networks
# Author: Qi Hu
import numpy as np
import load_data
import copy


class Network(object):
    def __init__(self, uai_path):
        net_type, n_variable, cardinalities, n_clique, clique_vertex, function_tables = load_data.read_uai(uai_path)
        evidences = load_data.read_evid(evid_path)
        self.type = net_type
        self.n_variable = n_variable
        self.n_clique = n_clique
        self.variables = []
        self.cliques = []
        for i in range(n_variable):
            variable = Variable(i, cardinalities[i], clique_vertex, evidences)
            self.variables.append(variable)
        for i in range(n_clique):
            clique = Clique(cardinalities, clique_vertex[i], function_tables[i])
            self.cliques.append(clique)
        self.evidences = evidences

    def get_type(self):
        return self.type

    def get_n_variable(self):
        return self.n_variable

    def get_n_clique(self):
        return self.n_clique

    def get_variables(self):
        return self.variables

    def get_variable_indexes(self):
        index_list = []
        for v in self.get_variables():
            index_list.append(v.get_index())
        return index_list

    def get_a_variable(self, index):
        for v in self.variables:
            if v.index == index:
                return v
        print 'No such node: %d' % v.index
        return Variable(-1, -1, [], [])

    def get_cliques(self):
        return self.cliques

    def get_evidences(self):
        return self.evidences

    def get_triangulated_graph(self):
        # use min-filling heuristic algorithm to find the triangulated graph
        graph = copy.deepcopy(self)
        unmarked = graph.get_variable_indexes()
        while len(unmarked) > 0:
            # First find the min filling-in node to eliminate
            min_n_fillin = len(unmarked)
            for v in unmarked:  # iterate through all nodes
                node = graph.get_a_variable(v)
                n_fillin = 0  # initialize the number of filling-in as zero
                for neighbor in node.get_neighbors():  # iterate through all its neighbors
                    if neighbor in unmarked:
                        neighbor_node = graph.get_a_variable(neighbor)
                        for neighbor_prime in node.get_neighbors():
                            if (neighbor != neighbor_prime) and (neighbor_prime not in neighbor_node.get_neighbors()):
                                n_fillin += 1
                if n_fillin < min_n_fillin:
                    min_n_fillin = n_fillin
                    v_elim = v
            # Second connect all neighbors of this node
            node_elim = graph.get_a_variable(v_elim)
            for neighbor in graph.get_a_variable(v_elim).get_neighbors():
                if neighbor in unmarked:
                    neighbor_node = graph.get_a_variable(neighbor)
                    for neighbor_prime in node_elim.get_neighbors():
                        if neighbor_prime in unmarked and neighbor != neighbor_prime:
                            neighbor_node.add_neighbor(neighbor_prime)
                            # print neighbor, neighbor_prime
            # Third, eliminate the node
            unmarked.remove(v_elim)
        return graph

    def get_max_cliques(self):
        max_cliques = []
        variables = self.get_variable_indexes()
        n_variable = self.get_n_variable()
        marked = [False]*n_variable
        prev_cdn = set()
        prev_v_elim = variables[0]
        while False in marked:
            max_cdn = set()
            v_elim = variables[0]
            for v in variables:
                node = self.get_a_variable(v)
                cdn = set()  # record current node's cardinal of unmarked nodes
                if not marked[v]:  # this node is unmarked
                    for neighbor in node.get_neighbors():
                        if marked[neighbor]:
                            cdn.add(neighbor)
                if len(cdn) > len(max_cdn):
                    v_elim = v
                    max_cdn = cdn
            if (len(prev_cdn) >= len(max_cdn)) and (len(max_cdn) != 0):
                prev_cdn.add(prev_v_elim)
                max_cliques.append(prev_cdn)
            marked[v_elim] = True
            prev_cdn = max_cdn
            prev_v_elim = v_elim
        prev_cdn.add(prev_v_elim)
        max_cliques.append(prev_cdn)
        return max_cliques

    def get_junction_tree(self):
        max_cliques = self.get_max_cliques()
        cliques = []
        for clique in max_cliques:
            cliques.append(JunctionTreeCloud(clique, set()))
        for i in range(0, len(cliques)):
            index = 0
            max_n_neighbor = 0
            for j in range(0, i):
                n_neighbor = len(cliques[i].nodes & cliques[j].nodes)
                if n_neighbor > max_n_neighbor:
                    max_n_neighbor = n_neighbor
                    index = j
            cliques[index].neighbors.add(cliques[i])
            cliques[i].neighbors.add(cliques[index])
        return cliques[0]


# Class to store a single variable (vertex)
class Variable(object):
    def __init__(self, index, cardinality, cliques, evidences):
        self.index = index
        self.cardinality = cardinality
        self.neighbors = set()
        self.init_neighbors(cliques)
        self.evidence = -1
        self.init_evidences(evidences)

    def get_index(self):
        return self.index

    def get_cardinality(self):
        return self.cardinality

    def get_neighbors(self):
        return self.neighbors

    def add_neighbor(self, index):
        self.neighbors.add(index)

    def get_evidence(self):
        return self.evidence

    def init_neighbors(self, cliques):
        for j in range(len(cliques)):
            clique = cliques[j]
            if self.index in clique:
                for i in clique:
                    self.neighbors.add(i)
        self.neighbors.remove(self.index)

    def init_evidences(self, evidences):
        if self.index in evidences.keys():
            self.evidence = evidences[self.index]


# Class to store a single clique
class Clique(object):
    def __init__(self, cardinalities, clique, function_table):
        self.variables = clique
        self.n_variables = len(clique)
        self.n_entry = function_table[0]
        self.function_table = np.asarray(function_table[1])
        cardinality = []
        for i in range(self.n_variables):
            cardinality.append(cardinalities[clique[i]])
        self.function_table = self.function_table.reshape(cardinality)

    def get_variables(self):
        return self.variables

    def get_n_entry(self):
        return self.n_entry

    def get_entry(self, var_values):
        '''
            Parameters:
                var_values: list of values for all variables in this clique
        '''
        dim = len(var_values)
        if dim != len(self.function_table.shape):
            print 'invalid index!'
            return -1
        entry = self.function_table
        for i in range(dim):
            entry = entry[var_values[i]]
        return entry


class JunctionTreeCloud(object):
    def __init__(self, nodes, neighbors):
        self.nodes = nodes
        self.neighbors = neighbors


if __name__ == '__main__':
    uai_path = './data/test.uai.txt'
    evid_path = './data/test.uai.evid.txt'
    markov = Network(uai_path)
    # print markov.get_type()
    # print markov.get_variables()[0].get_cardinality()
    # print markov.get_variables()[2].get_neighbors()
    # print markov.get_variables()[0].get_evidence()
    # print markov.get_cliques()[-1].get_entry([0, 1])
    for i in markov.get_variable_indexes():
        v = markov.get_a_variable(i)
        print i, v.get_neighbors()

    triangulated_graph = markov.get_triangulated_graph()
    for i in triangulated_graph.get_variable_indexes():
        v = triangulated_graph.get_a_variable(i)
        print i, v.get_neighbors()

    max_cliques = triangulated_graph.get_max_cliques()
    for c in max_cliques:
        print c