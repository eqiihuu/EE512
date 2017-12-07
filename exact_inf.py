import copy
import sys
from markov import *


def get_triangulated_graph(origin_graph):
    # use min-filling heuristic algorithm to find the triangulated graph
    graph = copy.deepcopy(origin_graph)
    unmarked = graph.get_variable_indexes()
    while len(unmarked) > 0:
        # First find the min filling-in node to eliminate
        min_n_fillin = sys.maxint
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


# Get all max-cliques using MSC
def get_max_cliques(trianulated_graph):
    max_cliques = []
    variables = trianulated_graph.get_variable_indexes()
    n_variable = trianulated_graph.get_n_variable()
    marked = [False ] *n_variable
    prev_cdn = set()
    prev_v_elim = variables[0]
    while False in marked:
        max_cdn = set()
        v_elim = variables[0]
        for v in variables:
            node = trianulated_graph.get_a_variable(v)
            cdn = set()  # record current node's cardinal of marked nodes
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
    return list(max_cliques)  # A list of set(int)


def is_include(clique, sub_clique):
    for n in sub_clique:
        if n not in clique:
            return False
    return True


def init_max_cliques(graph, max_cliques):
    cliques = []
    for clique in max_cliques:
        clique = list(clique)
        cardinalities = [n.get_cardinality() for n in graph.get_variables()]
        table_size = 1
        for v in clique:
            cdn = graph.get_a_variable(v).get_cardinality()
            table_size *= cdn
        table = [len(clique), [1]*table_size]
        # print cardinalities, clique, table
        new_clique = Clique(cardinalities, clique, table)
        cliques.append(new_clique)
    for sub_clique in graph.get_cliques():
        for clique in cliques:
            if is_include(clique.get_variables(), sub_clique.get_variables()):
                # print clique.get_variables(), sub_clique.get_variables()
                clique.function_table = get_updated_table(clique, sub_clique)
                break
    return cliques


# Generate junction tree by finding the neighbor with largest intersection
def get_junction_tree(max_cliques):
    junction_tree = copy.deepcopy(max_cliques)
    for i in range(1, len(junction_tree)):
        index = 0
        max_n_neighbor = 0
        for j in range(0, i):
            n_neighbor = len(set(junction_tree[i].get_variables()) & set(junction_tree[j].get_variables()))
            if n_neighbor > max_n_neighbor:
                max_n_neighbor = n_neighbor
                index = j
        junction_tree[index].get_neighbors().add(junction_tree[i])
        junction_tree[i].get_neighbors().add(junction_tree[index])
    return junction_tree


# get the new axis order for clique according to the separator
def get_new_axis(matrix1, matrix2):
    id1_list = [n for n in matrix1]
    id2_list = [n for n in matrix2]
    id2_dict = {}
    id_delta = len(id1_list) - len(id2_list)
    for i in range(len(id2_list)):
        id2_dict[id2_list[i]] = i + id_delta
    new_axis = []
    index = 0
    for n in id1_list:
        if n in id2_dict:
            new_axis.append(id2_dict[n])
        else:
            new_axis.append(index)
            index += 1
    return new_axis


# Get the table updated by separator
def get_updated_table(clique, separator):
    old_axis = range(len(clique.get_variables()))
    new_axis = get_new_axis(clique.get_variables(), separator.get_variables())
    c_table = clique.function_table
    s_table = separator.function_table
    rotated_c_table = np.moveaxis(c_table, old_axis, new_axis)
    updated_table = rotated_c_table * s_table
    reversed_c_table = np.moveaxis(updated_table, new_axis, old_axis)
    # print '='*30
    # print clique.get_variables()
    # print clique.get_function_table()
    # print '-' * 30
    # print separator.get_variables()
    # print separator.get_function_table()
    # print '-' * 30
    # print reversed_c_table
    return reversed_c_table


# Get the separator nodes's position in clique
def get_separator_index(clique, separator):
    id1_list = [n.get_index() for n in clique]
    id2_list = [n.get_index() for n in separator]
    id_list = []
    for i in range(len(id1_list)):
        if id1_list[i] in id2_list:
            id_list.append(i)
    return id_list


def message_passing(parent, curr):
    if curr.is_visited() or not parent:
        return
    for child in curr.get_neighbors():
        message_passing(child, parent)
    intersection = [i for i in parent.get_variable_indexes() if i in curr.get_variable_indexes()]
    separator = Clique(intersection, [], [], [])
    id_list = get_separator_index(parent, separator)
    table = np.sum(curr.get_function_table(), id_list)
    separator.function_table = table
    parent.function_table = get_updated_table(parent, curr)


# get a new graph with the evidence
def add_evid(graph):
    new_graph = copy.deepcopy(graph)
    for n in new_graph.get_variables():
        v = n.get_index()
        evid = n.get_evidence()
        if evid == -1:
            continue
        for c in new_graph.get_cliques():
            c_nodes = c.get_variables()
            old_table = c.get_function_table()
            if v not in c_nodes:
                continue
            s = []
            for c_node in c_nodes:
                cdn = new_graph.get_a_variable(c_node).get_cardinality()
                if cdn == 1:
                    continue
                if c_node != v:
                    s.append(range(cdn))
                else:
                    s.append(evid)
            n.cardinality = 1
            c.function_table = old_table[tuple(s)]
    print new_graph.cliques[0].variables, new_graph.cliques[0].function_table
    return new_graph
