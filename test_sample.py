import math
import time
import os

from markov import *
from exact_inf import *

file_name = '2'
uai_path = './data/'+file_name+'.uai.txt'

evid_path = './data/'+file_name+'.uai.evid.txt'
graph = Network(uai_path, evid_path)
# graph = add_evid(graph)

t0 = time.time()
triangulated_graph = get_triangulated_graph(graph)
max_cliques = get_max_cliques(triangulated_graph)
initialized_cliques = init_max_cliques(graph, max_cliques)

junction_tree = get_junction_tree(initialized_cliques)

message_passing(None, junction_tree[0])
z = np.sum(junction_tree[0].get_function_table())
t1 = time.time()

print 'Z = %e, log(Z) = %.3f' % (z, math.log(z))
print 'Time: %.3f s' % (t1-t0)
