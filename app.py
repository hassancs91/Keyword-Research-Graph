import networkx as nx
from pyvis.network import Network
from helpers import get_topic_children


def generate_subtopics_graph(graph, topic, current_level, max_level):
    if current_level > max_level:
        return
    
    print(f"Level {current_level}: Generating subtopics for '{topic}'")
    
    subtopics = get_topic_children(topic)
    for subtopic in subtopics:
        print(f"  Adding edge from '{topic}' to '{subtopic}'")
        graph.add_edge(topic, subtopic)
        generate_subtopics_graph(graph, subtopic, current_level + 1, max_level)

        

def main():
    main_topic_keyword = "Machine Learning"
    max_level = int(input("Enter the level of sub-leveling (1-10): "))
    
    graph = nx.DiGraph()
    generate_subtopics_graph(graph, main_topic_keyword, 1, max_level)
    
    # Convert networkx graph to pyvis network
    net = Network(notebook=True)
    net.from_nx(graph)
    
    # Save and display the interactive graph
    net.show("generated_topic_graph.html")
    print("Interactive graph saved as 'generated_topic_graph.html'")

if __name__ == "__main__":
    main()
