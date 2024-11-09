# -*- coding: utf-8 -*-
"""map generation.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1MrmnUNqAYBgoSO2dIvfCWQXlro1SQ5ut
"""

import pandas as pd

df = pd.read_csv('/content/route_detail.csv')

df.head()

"""# Data cleaning"""

df = df.iloc[:,1:]
df.head()

stat = df.groupby(by=["stop_name"])["route_id"].count().sort_values(ascending=False)
display(stat)

import matplotlib.pyplot as plt
stat.plot(kind = 'bar')
plt.show()

"""# Visualize data

after reseaching found network graph will best suit the usecase
"""

import matplotlib.pyplot as plt
import networkx as nx

sample = df[df["stop_name"]=="DUNLOP"]
G = nx.from_pandas_edgelist(sample, "route_id", "stop_name")
nx.draw_networkx(G)
plt.show()

"""# Modifing data to be represented as graph

"""

df.head()
df["next_stop"] = df.groupby(by=["route_id"])["stop_name"].shift(-1)
df.loc[:50]

"""**Note: last stop for every route can be consider as route_id for easy visualization purpose**

by updating nan with route id
"""

df.loc[df["next_stop"].isna(), "next_stop"] = df.loc[df["next_stop"].isna(), "route_id"]
df.loc[:50]

"""Sample data creation - Dunlop stop"""

sample_routes = df[df["stop_name"]=="DUNLOP"]["route_id"]
sample = df[df["route_id"].isin(sample_routes)]
sample.head()

plt.figure(figsize=(100, 100))
G = nx.from_pandas_edgelist(sample, "stop_name", "next_stop")
nx.draw_networkx(G, pos=nx.spring_layout(G, iterations=1000))
plt.savefig('dunlop_route.png')

"""Except for base stop all other stop should be unique to route. so intersection wont happen between routes"""

# sample["derived_next_stop"] = sample.apply(lambda row: row["next_stop"] if(row["next_stop"]=="DUNLOP") else row["route_id"]+row["next_stop"], axis=1)
# sample = sample.drop("derived_next_stop",axis=1)
sample.loc[~(sample["next_stop"]=="DUNLOP") & ~(sample["next_stop"]==sample["route_id"]),"derived_next_stop"] =  sample["route_id"]+ "-" +sample["next_stop"]
sample.loc[(sample["next_stop"]=="DUNLOP") | (sample["next_stop"]==sample["route_id"]),"derived_next_stop"] = sample["next_stop"]
sample.loc[~(sample["stop_name"]=="DUNLOP"),"derived_stop_name"] = sample["route_id"]+ "-" + sample["stop_name"]
sample.loc[sample["stop_name"]=="DUNLOP","derived_stop_name"] = sample["stop_name"]
sample.head()

plt.figure(figsize=(100, 100))
G = nx.from_pandas_edgelist(sample, "derived_stop_name", "derived_next_stop")
nx.draw_networkx(G, pos=nx.spring_layout(G, iterations=1000))
plt.savefig('routewise_map_from_dunlop.png')

"""# Add more detail
* coluring base stop differently
* colouring edges
* trying to find best layout for representing data - looks like only spring_layout is best for representing data
* have to find ways to give more space between node so stop name is visible
* add direction
* add different color for different route

"""

G = nx.from_pandas_edgelist(sample, "derived_stop_name", "derived_next_stop")
color =[]
for node in G:
    if node == "DUNLOP":
        # current stop
        color.append((0,1,0)) #green
    elif node in list(sample["route_id"]):
        color.append((1,0,0)) #red
    else:
        color.append((0,0,1)) #blue

plt.figure(figsize=(100,100))
nx.draw_networkx(G, pos=nx.spring_layout(G, iterations=100),edge_color=(0.8,0.6,0.3), node_color=color, arrows=True, arrowstyle= '-|>',
    arrowsize= 12)
# plt.legend()
plt.savefig('routewise_map_from_dunlop_with_color.png')

plt.figure(figsize=(100,100))
nx.draw_networkx(G, pos=nx.kamada_kawai_layout(G),edge_color=(0.8,0.6,0.3), node_color=color)
plt.savefig('kamada_kawai_layout.png')

"""* set same distance between all nodes

"""

distance = {}
for u,v in G.edges():
    if u not in distance.keys():
        distance[u] = {}
    if u == "DUNLOP":
        distance[u][v] = 500
    else:
        distance[u][v] = nx.shortest_path_length(G, source=u, target=v)
print(distance["DUNLOP"])

plt.figure(figsize=(100,100))
nx.draw_networkx(G, pos=nx.kamada_kawai_layout(G, dist=distance),edge_color=(0.8,0.6,0.3), node_color=color)
plt.savefig('kamada_kawai_layout.png')

"""# Adding Legend"""

from matplotlib.patches import Patch
from matplotlib.lines import Line2D

legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='Current Stop',markerfacecolor='g', markersize=15),
    Line2D([0], [0], marker='o', color='w', label='Bus number',markerfacecolor='r', markersize=15),
    Line2D([0], [0], marker='o', color='w', label='Stop',markerfacecolor='b', markersize=15),
]

# Create the figure
# fig, ax = plt.subplots()
# ax.legend(handles=legend_elements, loc='upper right')

# print(ax)

plt.figure(figsize=(100,100))
nx.draw_networkx(G, pos=nx.spring_layout(G, iterations=100, scale=2),edge_color=(0.8,0.6,0.3), node_color=color, arrows=True, arrowstyle= '-|>',
    arrowsize= 12)
# , ax=ax
# Setting it to how it was looking before.
# plt.axis('off')
plt.legend(handles=legend_elements, loc='upper right')
plt.savefig('routewise_map_from_dunlop_with_legend.png')

plt.figure(figsize=(100,100))
nx.draw_networkx(G, pos=nx.shell_layout(G),edge_color=(0.8,0.6,0.3), node_color=color)
plt.savefig('shell_layout.png')

plt.figure(figsize=(100,100))
nx.draw_networkx(G, pos=nx.fruchterman_reingold_layout(G),edge_color=(0.8,0.6,0.3), node_color=color)
plt.savefig('shell_layout.png')

"""
# recoloring based on bus number"""

!pip install distinctipy

from distinctipy import distinctipy

routes = sample["route_id"].unique()
n=len(list(routes))
# print(list(route))

reserved_color = [(1,0,0),(0,1,0),(0,0,1),(0.8,0.6,0.3)]

# generate N visually distinct colours
colors = distinctipy.get_colors(n,reserved_color)
# print(colors)
route_color_map = { route: color for route, color in zip(routes,colors)}
print(route_color_map)

G = nx.from_pandas_edgelist(sample, "derived_stop_name", "derived_next_stop")
color =[]
for node in G:
    if node == "DUNLOP":
        # current stop
        color.append((0,1,0)) #green
    elif node in list(sample["route_id"]):
        color.append((1,0,0)) #red
    else:
        color.append(route_color_map[node.split("-")[0]]) #route wise color

from matplotlib.lines import Line2D

legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='Current Stop',markerfacecolor='g', markersize=15),
    Line2D([0], [0], marker='o', color='w', label='Bus number',markerfacecolor='r', markersize=15),
]
route_legend = [
    Line2D([0], [0], marker='o', color='w', label= bus_num,markerfacecolor=route_color_map[bus_num], markersize=15) for bus_num in route_color_map
]
legend_elements = legend_elements + route_legend

# Create the figure
# fig, ax = plt.subplots()
# ax.legend(handles=legend_elements, loc='upper right')

# print(ax)

plt.figure(figsize=(100,100))
nx.draw_networkx(G, pos=nx.spring_layout(G, iterations=30),edge_color=(0.8,0.6,0.3), node_color=color, arrows=True,
    arrowsize= 25)
# , ax=ax q
# Setting it to how it was looking before.
# plt.axis('off')
plt.legend(handles=legend_elements, loc='upper right')
plt.savefig('routewise_map_from_dunlop_with_legend.png')

"""# relabeling to avoid overlapping for labels"""

G = nx.from_pandas_edgelist(sample, "derived_stop_name", "derived_next_stop", create_using=nx.DiGraph())
print(nx.is_directed(G))
color =[]
root_node = None
for node in G:
    if node == "DUNLOP":
        # current stop
        root_node = node
        color.append((0,1,0)) #green
    elif node in list(sample["route_id"]):
        color.append((1,0,0)) #red
    else:
        color.append(route_color_map[node.split("-")[0]]) #route wise color
print(root_node)

from matplotlib.lines import Line2D

legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='Current Stop',markerfacecolor='g', markersize=15),
    Line2D([0], [0], marker='o', color='w', label='Bus number',markerfacecolor='r', markersize=15),
]
route_legend = [
    Line2D([0], [0], marker='o', color='w', label= bus_num,markerfacecolor=route_color_map[bus_num], markersize=15) for bus_num in route_color_map
]
legend_elements = legend_elements + route_legend

# Create the figure
# fig, ax = plt.subplots()
# ax.legend(handles=legend_elements, loc='upper right')

# print(ax)

plt.figure(figsize=(100,100))
# pos=nx.spring_layout(G, iterations=100)
# pos=nx.kamada_kawai_layout(G)
# pos=nx.shell_layout(G)
pos=nx.nx_pydot.graphviz_layout(G,prog="twopi",root=root_node)
# print(pos)
nx.draw_networkx(G, pos=pos,edge_color=(0.8,0.6,0.3), node_color=color, arrows=True,
    arrowsize= 25)
# , ax=ax q
# Setting it to how it was looking before.
# plt.axis('off')
plt.legend(handles=legend_elements, loc='upper right')
plt.savefig('routewise_map_from_dunlop_with_legend.png')

"""# Alternative Representation

* use different color edges to represent
"""

G = nx.from_pandas_edgelist(sample, "derived_stop_name", "derived_next_stop", create_using=nx.DiGraph())
print(nx.is_directed(G))

edge_color = []
for u,v in G.edges():
    route_id = None
    u_list = u.split("-")
    v_list = v.split("-")
    if len(u_list) > 1:
        route_id = u_list[0]
    elif len(v_list) > 1:
        route_id = v_list[0]

    edge_color.append(route_color_map[route_id])
# print(edge_color)

"""* use different color node to represent stop"""

stops = sample["stop_name"].unique()
n=len(list(stops))

print(n)

reserved_color = [(1,0,0),(0,1,0),(0,0,1)] + edge_color

# generate N visually distinct colours
colors = distinctipy.get_colors(n,reserved_color)
# print(colors)
stop_color_map = { stop: color for stop, color in zip(stops,colors)}
# print(stop_color_map)

"""* display only route id
* set root node
"""

node_color =[]
root_node = None
labels = {}
for node in G:
    if node == "DUNLOP":
        # current stop
        root_node = node
        node_color.append((0,1,0)) #green
        labels[node] = node
    elif node in list(sample["route_id"]):
        node_color.append((1,0,0)) #red
        labels[node] = node
    else:
        labels[node] = sample.loc[sample["derived_stop_name"]== node,"stop_id"].values[0]
        node_color.append(stop_color_map[node.split("-")[1]]) #route wise color
# print(root_node)
# print(labels)

"""* use graphviz radical layout
* add these details in legend
* increse edge width
"""

from matplotlib.lines import Line2D

legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='Current Stop (DUNLOP)',markerfacecolor='g', markersize=15),
    Line2D([0], [0], marker='o', color='w', label='Bus number',markerfacecolor='r', markersize=15),
]
route_legend = [
    Line2D([0], [0], marker='d', color='w', label= bus_num,markerfacecolor=route_color_map[bus_num], markersize=15) for bus_num in route_color_map
]
stop_legend = [
    Line2D([0], [0], marker='o', color='w', label= stop,markerfacecolor=stop_color_map[stop], markersize=15) for stop in stop_color_map
]
legend_elements = legend_elements + route_legend + stop_legend

# Create the figure
# fig, ax = plt.subplots()
# ax.legend(handles=legend_elements, loc='upper right')

# print(ax)

plt.figure(figsize=(100,100))
# pos=nx.spring_layout(G, iterations=100)
# pos=nx.kamada_kawai_layout(G)
# pos=nx.shell_layout(G)
pos=nx.nx_pydot.graphviz_layout(G,prog="twopi",root=root_node)
# print(pos)
nx.draw_networkx(G, pos=pos,edge_color=edge_color, node_color=node_color, arrows=True,
    arrowsize= 25, width=5, labels=labels)
#  with_labels=False,
# , ax=ax q
# Setting it to how it was looking before.
# plt.axis('off')
plt.legend(handles=legend_elements, loc='upper right')
plt.savefig('routewise_map_from_dunlop_with_legend.png')

"""# Tired to use external lable
* use graphviz external label layout - not possible since node is too close and tidious
"""

!sudo apt-get install graphviz graphviz-dev -y
!pip install pygraphviz

from matplotlib.lines import Line2D

legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='Current Stop',markerfacecolor='g', markersize=15),
    Line2D([0], [0], marker='o', color='w', label='Bus number',markerfacecolor='r', markersize=15),
]
route_legend = [
    Line2D([0], [0], marker='o', color='w', label= bus_num,markerfacecolor=route_color_map[bus_num], markersize=15) for bus_num in route_color_map
]
legend_elements = legend_elements + route_legend

# Create the figure
# fig, ax = plt.subplots()
# ax.legend(handles=legend_elements, loc='upper right')

# print(ax)

plt.figure(figsize=(100,100))
# pos=nx.spring_layout(G, iterations=100)
# pos=nx.kamada_kawai_layout(G)
# pos=nx.shell_layout(G)
# pos=nx.nx_pydot.graphviz_layout(G,prog="twopi",root=root_node)
A = nx.nx_agraph.to_agraph(G)
for node in A:
    word = str(node).split("-")
    if len(word) == 2:
        node.attr["xlabel"] = word[1]
    else:
        node.attr["xlabel"] = word[0]

G = nx.nx_agraph.from_agraph(A, create_using=nx.DiGraph())

pos=nx.nx_pydot.graphviz_layout(G,prog="twopi",root=root_node)

# print(pos)
nx.draw_networkx(G, pos=pos,edge_color=(0.8,0.6,0.3), node_color=color, arrows=True,
    arrowsize= 25)
# , ax=ax q
# Setting it to how it was looking before.
# plt.axis('off')
plt.legend(handles=legend_elements, loc='upper right')
plt.savefig('routewise_map_from_dunlop_with_legend.png')

"""# future enhancement
Instead of focusing on route, stop or destination can be highlighted and colour code route which takes to those destination or stop.

multiple graph same set nodes. complicates the graph. something for future enhancement
"""
