# This is a file to read uai.txt files
# Author: Qi Hu
import re


def read_uai(f_path):
    f = open(f_path, 'r')
    type = f.readline().strip('\n')
    num_variable = int(f.readline().strip('\n'))
    cardinalites = [int(i) for i in f.readline().strip('\n').split(' ') if i]
    num_clique = int(f.readline().strip('\n'))

    cliques = []
    for i in range(num_clique):
        line = f.readline().strip('\n')
        line = re.split('\t| ', line)
        num_vertex = int(line[0])
        clique = line[1:]
        for i in range(num_vertex):
            clique[i] = int(clique[i])
        cliques.append(clique)

    function_tables = []
    for i in range(num_clique):
        line = f.readline().strip('\n')
        while line == '':
            line = f.readline().strip('\n')
        num_entry = int(line)
        line = f.readline().strip('\n').split(' ')
        probs = []
        while line != ['']:
            probs = probs + [float(i) for i in line if i]
            if len(probs) == num_entry:
                break
            line = f.readline().strip('\n').split(' ')
        function_tables.append([num_entry, probs])
    return type, num_variable, cardinalites, num_clique, cliques, function_tables


def read_evid(f_path):
    evidence = {}
    f = open(f_path, 'r')
    line = f.readline().strip('\n').split(' ')
    num_evid = int(line[0])
    if num_evid == 0:
        return evidence
    evids = line[1:]
    for i in range(num_evid):
        evidence[int(evids[i*2])] = int(evids[i*2+1])
    return evidence

if __name__ == '__main__':
    uai_path = './data/3.uai.txt'
    evid_path = './data/3.uai.evid.txt'
    t, n_v, cdns, n_c, clqs, f_t = read_uai(uai_path)
    evids = read_evid(evid_path)
    print t
    print n_v, n_c
    print cdns
    print clqs
    print f_t
    print evids
