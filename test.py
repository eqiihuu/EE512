import math
import time
import os

from markov import *
from exact_inf import *

test_files = [1, 2, 4, 5, 6, 8, 9, 10]
hard_files = [7, 11]
for i in test_files:
    file_name = os.path.join('markov_files', 'markov%d' % i)
    uai_path = os.path.join('./data/', file_name+'.uai')

    evid_path = './data/2.uai.evid.txt'
    graph = Network(uai_path, evid_path)
    # graph = add_evid(graph)

    t0 = time.time()
    triangulate_graph(graph)
    max_cliques = get_max_cliques(graph)
    initialized_cliques = init_max_cliques(graph, max_cliques)

    junction_tree = get_junction_tree(initialized_cliques)

    message_passing(None, junction_tree[0])
    z = np.sum(junction_tree[0].get_function_table())
    t1 = time.time()

    print '%d\n Z = %e, log(Z) = %.3f' % (i, z, math.log(z))
    print ' Time: %.3f s' % (t1-t0)
