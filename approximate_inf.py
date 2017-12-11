from markov import *


# get the new axis order for clique according to the separator
def get_new_axis(id1_list, id2_list):
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
    return reversed_c_table


# Get the separator nodes's position in clique
def get_sum_index(clique, separator):  # (Clique, list)
    id_list = []
    for i in range(len(clique)):
        if clique[i] not in separator:
            id_list.append(i)
    return tuple(id_list)


# Remove a specific node from the graph
# (Not completed, need to update the adjacent nodes)
def elim_a_node(graph, node):
    index = node.get_index()
    cliques = graph.get_cliques()
    for c in cliques:
        if index in c.get_variables():
            table = get_updated_table(c, node)
            sum_list = get_sum_index(c, node)
            c.function_table = np.sum(table, axis=sum_list)
            c.variables.remove(index)

    graph.variables.remove(node)


# Eliminate graph nodes which can be eliminated without filling-in
def elim_nodes(origin_graph):
    # use min-filling heuristic algorithm to find the triangulated graph
    graph = copy.deepcopy(origin_graph)
    remained = []
    while len(remained) > 0:
        # First find the min filling-in node to eliminate
        stop = True
        for v in remained:  # iterate through all nodes
            eliminate = True
            node = graph.get_a_variable(v)
            for neighbor in node.get_neighbors():  # iterate through all its neighbors
                if neighbor in remained:
                    neighbor_node = graph.get_a_variable(neighbor)
                    for neighbor_prime in node.get_neighbors():
                        if (neighbor_prime in remained) and (neighbor != neighbor_prime)\
                                and (neighbor_prime not in neighbor_node.get_neighbors()):
                            eliminate = False
                            break
                    if not eliminate:
                        break
                if not eliminate:
                    break
            if eliminate:
                elim_a_node(graph, node)
                stop = False
        if stop:
            break
    return graph

