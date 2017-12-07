from markov import *
from exact_inf import *


file_name = '1'
uai_path = './data/'+file_name+'.uai.txt'
evid_path = './data/'+file_name+'.uai.evid.txt'
markov = Network(uai_path, evid_path)
evid_graph = add_evid(markov)

triangulated_graph = get_triangulated_graph(evid_graph)
max_cliques = get_max_cliques(triangulated_graph)
initialized_cliques = init_max_cliques(evid_graph, max_cliques)
junction_tree = get_junction_tree(initialized_cliques)

# for c in evid_graph.get_cliques():
#     print c.get_variables()
#     print '-', c.get_function_table().shape
    # for n in c.get_neighbors():
    #     print '---', n.get_variables()

message_passing(None, junction_tree[0])
z = np.sum(junction_tree[0].get_function_table())

print z
