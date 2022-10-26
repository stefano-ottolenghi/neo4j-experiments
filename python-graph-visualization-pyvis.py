import pyvis
from neo4j import GraphDatabase
import neo4j
import random

driver = GraphDatabase.driver("neo4j://localhost:7687",
                              auth=("neo4j", "secret"))

def add_friend(tx, name, friend_name):
    tx.run("MERGE (a:Person {name: $name}) "
           "MERGE (a)-[:KNOWS]->(friend:Person {name: $friend_name})",
           name=name, friend_name=friend_name)
           
def add_film_like(tx, person_name, title):
    tx.run("MERGE (film:Film {title: $title}) "
           "MERGE (liker:Person {name: $person_name}) "
           "MERGE (liker)-[:LIKES]->(film)",
           title=title, person_name=person_name)

def print_friends(tx, name):
    query = ("MATCH (a:Person)-[:KNOWS]->(friend) WHERE a.name = $name "
             "RETURN friend.name ORDER BY friend.name")
    for record in tx.run(query, name=name):
        print(record["friend.name"])

def visualize_result(query_graph, nodes_text_properties):
    visual_graph = pyvis.network.Network()
    colors = {} # association node labels <-> colors (ex 'Person':'#ABC567')
    
    # all the list casting is because of frozensets
    for node in list(query_graph.nodes):
        
        # If we don't yet have a color for this type of node
        if len(node.labels.intersection(colors.keys())) == 0:
            color = "#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])
            colors[list(node.labels)[0]] = color
        
        else:
            color = colors[list(node.labels.intersection(colors.keys()))[0]]
        
        node_label = dict(node.items())[nodes_text_properties[list(node.labels)[0]]]
        visual_graph.add_node(node.element_id, node_label, color=color)
    
    for relationship in list(query_graph.relationships):
        visual_graph.add_edge(relationship.start_node.element_id, 
                              relationship.end_node.element_id, 
                              title=relationship.type)
    
    visual_graph.show('network.html')

with driver.session(default_access_mode=neo4j.WRITE_ACCESS) as session:
    # Clear db
    session.run("MATCH (a)-[r]-() DETACH DELETE a,r")
    session.run("MATCH (n) DETACH DELETE n")
    
    # Add some data
    session.execute_write(add_friend, "Arthur", "Lancelot")
    session.execute_write(add_friend, "Arthur", "Guinevere")
    session.execute_write(add_friend, "Arthur", "Merlin")
    session.execute_write(add_film_like, "Arthur", "Wall-E")
    
    # Query to get a graphy result
    result = session.run("MATCH (a:Person {name: $name})-[r]-(b) "
                         "RETURN a,r,b;", 
                         name="Arthur")
    #print(result.peek().data)
    
    # Draw graph
    nodes_text_properties = {'Person': 'name', 'Film': 'title'} # what property to use as text for each node
    visualize_result(result.graph(), nodes_text_properties)

"""
>>> res = session.run("MERGE (a:Person {name: $name}) MERGE c=(a)-[:KNOWS]->(friend:Person {name: $friend_name}) RETURN c;", name='Alice', friend_name='Bob')
>>> g = res.graph()
>>> list(g.relationships)[0].start_node == list(g.nodes)[0]
True
"""

"""
Networkx 
- requires matplotlib
- has no straightforward way to add labels to nodes
- static plotting to file
- import matplotlib.pyplot as plt
- visually less appealing
- pyvis is a js wrapper so there is hope that it works for other langs?
"""

driver.close()
