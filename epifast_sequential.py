import argparse
import os
#import matplotlib.pylab as plt
import json
import networkx as nx
from networkx.readwrite import json_graph
# Import packages for data cleaning
import numpy as np
import pandas as pd
import re # For finding specific strings in the text
# Import packages for data visualization
import networkx as nx
#import matplotlib.pyplot as plt
#test = nx.DiGraph()
import random
import sys
#print('test')
import networkx as nx
G = nx.DiGraph()
# add nodes, edges, etc to G ...


def add_both_edge(G, node1, node2):
    """
    adding both edges with weight 1
    """
    G.add_edge(node1, node2, weight=1)
    G.add_edge(node2, node1, weight=1)
    #print('added')

def update(G, rate, S, E, I, R, newly_exposed):
    #update daily based on rate 
    #S, E, I, and R represents list of nodes with number of days in 
    for ne in newly_exposed:
        E[ne] = rate['t_e'] + 1
        newly_exposed.remove(ne)
    for i in I.keys():
        I[i] -= 1
        if I[i] == 0:
            del I[i]
            #Remove recovered node from the graph 
            G.remove_node(i)
            R.append(i)
    for e in E.keys():
        E[e] -= 1
        if E[e] == 0:
            del E[e]
            I[e] = rate['t_i']

def sequential(G, rate, S, E, I, R, NE, T, t_rate):
    for t in range(T):
        #first thing of the day
        #update at morning 
        print(t)
        update(G, rate, S, E, I, R, NE)

        #no intervention at this level
        #
        for i in I.keys():
            contact = G.out_edges(i)
            for c in contact:
                #calculate transmissibility 
                #p(w(u,v)) = 1-(1-r)^{(w(u,v))}
                #TODO actually impliment weighted but since the weight is uniformed, the p(w(u,v)) = 0.5 
                #if v is adjacenet to u. 
                #if transmissed
                if (c[1] in S) and (np.random.binomial(1, t_rate) >0):
                    NE.append(c[1])
                    S.remove(c[1])

        #print
        print("On day " + str(t+1) +'\n')
        print("Number of susceptible is " + str(len(S)) + '\n')
        print("Number of exposed is " + str(len(E.keys())) + '\n')
        print("Number of infectious is " + str(len(I.keys())) + '\n')
        print("Number of Recovered " + str(len(R)) + '\n')
        #print("Suscepted nodes are:")
        #for s in S:
        #    print(s)
        #print("Infected nodes are: ")
        #for i in I.keys():
        #    print(i)
        #print("New exposed nodes are:")
        #for ne in NE:
        #    print(ne) 
        #print("Exposed nodes are:")
        #for e in E.keys():
        #    print(e) 
        #print("Recovered nodes are:")
        #for r in R:
        #    print(r)
        print('\n')

print("Starting.....")

parser =argparse.ArgumentParser()
parser.add_argument("--input_format",
                    nargs='+',
                    required=True,
                    help="{json/raw} whether the file is in networkx json('nodes'=[], 'edges'=[]) or format of space separated as Dr. Eubank's ")
parser.add_argument("--input_file",
                    nargs='+',
                    required=True,
                    help="Name of the input file")
parser.add_argument("--output_file",
                    nargs='+',
                    required=True,
                    help="Name of the output file")
parser.add_argument("--time", required=False, type=int, default="100", help="Simulation period in days")
parser.add_argument("--init_infection", required=False, type=int, default="20", help="Number of initial infectious people")
parser.add_argument("--transmission_rate", required=False, type=str, default="0.5", help="probability of disease transmission for a contact of one unit time")
parser.add_argument("--incubation_period", required=False, type=int, default="2", help="Average time period(in days) to be in exposed phase")
parser.add_argument("--infectious_period", required=False, type=int, default="4", help="Average time period(in days) to be infectious to other nodes")


args = parser.parse_args()
input_format = args.input_format[0]
input_file = args.input_file[0]
output_file = args.output_file[0]
sys.stdout=open(output_file, 'w')
time = args.time
init_infection = args.init_infection
transmission_rate = float(args.transmission_rate)
t_e = args.incubation_period
t_i = args.infectious_period


rate = {'t_e': t_e, 't_i':t_i}
t_r=transmission_rate
T=time

G=nx.DiGraph()
if (input_format == 'raw'):
    ver_number = {}
    ver_ver = {}
    just_number = []
    line_count = 0
    map_file = open(input_file+'.json', "w+")
    with open(input_file) as fp:
        line = fp.readline()
        ver_name = ""
        ver_list = []
        while line:
            values = line.split()
            if len(values) ==2: #vertex    degree
                if(len(ver_list) != 0): 
                    ver_ver[ver_name] = ver_list
                    ver_list = []
                just_number.append(int(values[1]))
                ver_number[values[0]] = int(values[1])
                ver_name = values[0]
            else: #     vertex    weight   0
                ver_list.append(values[0])
                #G.add_edge(int(ver_name), int(values[0]), weight=float(values[1]))
                add_both_edge(G, ver_name, values[0])
            #print(line)
            line = fp.readline()
    map_file.write(json.dumps(dict(nodes=G.nodes(), edges=G.edges())))
    map_file.close()
elif (input_format == 'json'):
    d = json.load(open(input_file, "r"))
    G.add_nodes_from(d['nodes'])
    G.add_edges_from(d['edges'])
else:
    print("Invalid input format")
    sys.exit()

print("finished reading the graph")

exposed = {}
removed = []
newly_exposed = []
#randomly pick 20 nodes
infectious = {}
init_infectious_nodes = random.sample(list(G.nodes()), init_infection)
for init_i_nodes in init_infectious_nodes:
    infectious[init_i_nodes] = rate['t_i']
print("calling sequentials")
susceptible=[node for node in list(G.nodes()) if node not in init_infectious_nodes]



sequential(G, rate, susceptible, exposed, infectious, removed, newly_exposed, T, t_r)
#number of nodes w/ one or more edges 
#number of nodes
#number of connected nodes
#number of clusters 
#centrality 
#print("done")
#print("average degree")
#print(sum(just_number)/len(just_number))
#print("number of vertex")
#print(len(just_number))
#print(ver_ver)
#map_file.write(json_graph.dumps(G))
