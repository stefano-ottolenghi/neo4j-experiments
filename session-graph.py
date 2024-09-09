import pyvis
from neo4j import GraphDatabase
import neo4j


def visualize_result(query_graph, nodes_text_properties):
    visual_graph = pyvis.network.Network()

    for node in query_graph.nodes:
        node_label = list(node.labels)[0]
        node_text = node[nodes_text_properties[node_label]]
        visual_graph.add_node(node.element_id, node_text, group=node_label)

    for relationship in query_graph.relationships:
        visual_graph.add_edge(relationship.start_node.element_id,
                              relationship.end_node.element_id,
                              title=relationship.type)

    visual_graph.show('network.html')


def main():
    URI = "neo4j://localhost"
    AUTH = ("neo4j", "secret")

    with GraphDatabase.driver(URI, auth=AUTH) as driver:

        friends_list = [("Arthur", "Guinevre"),
                        ("Arthur", "Lancelot"),
                        ("Arthur", "Merlin")]

        with driver.session(database="neo4j") as session:
            for pair in friends_list:
                session.execute_write(create_friends, pair[0], pair[1])
            session.execute_write(create_film, "Wall-E")
            session.execute_write(like_film, "Wall-E", "Arthur")
            graph = session.execute_read(get_person_graph, "Arthur")

        # Draw graph
        nodes_text_properties = {  # what property to use as text for each node
            "Person": "name",
            "Film": "title",
        }
        visualize_result(graph, nodes_text_properties)


def create_friends(tx, name, friend_name):
    tx.run("""
        MERGE (a:Person {name: $name})
        MERGE (a)-[:KNOWS]->(friend:Person {name: $friend_name})
        """, name=name, friend_name=friend_name
    )


def create_film(tx, title):
    tx.run("MERGE (film:Film {title: $title})", title=title)


def like_film(tx, title, person_name):
    tx.run("""
        MATCH (film:Film {title: $title})
        MATCH (liker:Person {name: $person_name})
        MERGE (liker)-[:LIKES]->(film)
        """, title=title, person_name=person_name,
    )


def get_person_graph(tx, name):
    result = tx.run("""
        MATCH (a:Person {name: $name})-[r]-(b)
        RETURN a,r,b
        """, name=name
    )
    return result.graph()


if __name__ == "__main__":
    main()
