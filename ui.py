import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from helpers import get_topic_children, get_keyword_metrics,generate_draft,post_on_wordpress
import time  # Import the time module

def fetch_keyword_metrics(keywords):
    try:
        keyword_string = ','.join(keywords[:20])  # Limit to 20 keywords
        response = get_keyword_metrics(keyword_string)
        if response['success']:
            return response['result']
        else:
            st.warning(f"API Warning: {response['message']}")
            return [{ 'keyword': keyword, 'searchVolume': 'N/A' } for keyword in keywords]
    except Exception as e:
        return [{ 'keyword': keyword, 'searchVolume': 'N/A' } for keyword in keywords]

def generate_subtopics_tree(topic, current_level, max_level, progress_log, added_nodes, keyword_data, fetch_keywords, child_topics_count, generate_post):
    start_time = time.time()  # Start the timer

    if current_level > max_level:
        return [], []

    log_entry = f"Level {current_level}: Generating subtopics for '{topic}'"
    progress_log.append(log_entry)
    
    subtopics = get_topic_children(topic,child_topics_count)
    nodes = []
    edges = []
    node_color = "white"
    if topic not in added_nodes:
        
        if fetch_keywords:
            main_topic_metrics = fetch_keyword_metrics([topic])
            main_search_volume = main_topic_metrics[0]['searchVolume'] if main_topic_metrics else 'N/A'
            keyword_data.extend(main_topic_metrics)
        else:
            main_search_volume = 'N/A'
        node_label = f"{topic} ( Search Volume: {main_search_volume})"
        if main_search_volume and main_search_volume != 'N/A':
            if main_search_volume > 10000:
                node_color = "#97eb14"
            elif main_search_volume > 1000:
                node_color = "#f4ff00"
            elif main_search_volume > 0:
                node_color = "#f10e38"
        else:
            node_color = "white"
        nodes.append(Node(id=topic, color = node_color, label=node_label, font={'color': 'white'}))
        
        

        added_nodes.add(topic)

    if fetch_keywords:
        # Fetch keyword metrics only if the checkbox is checked
        subtopic_metrics = fetch_keyword_metrics(subtopics)
        keyword_data.extend(subtopic_metrics)
    else:
        subtopic_metrics = [{'keyword': subtopic, 'searchVolume': 'N/A'} for subtopic in subtopics]

    for subtopic, metric in zip(subtopics, subtopic_metrics):
        search_volume = metric['searchVolume']
        node_label = f"{subtopic} (Search Volume: {search_volume})"
        if search_volume and search_volume != 'N/A':
            if search_volume > 10000:
                node_color = "#97eb14"
            elif search_volume > 1000:
                node_color = "#f4ff00"
            elif search_volume > 0:
                node_color = "#f10e38"
        else:
            node_color = "white"
        
        if subtopic not in added_nodes:
            if generate_post:
                draft = generate_draft(subtopic)
                post_on_wordpress(subtopic, draft)

            nodes.append(Node(id=subtopic, color = node_color, label=node_label, font={'color': 'white'}))
            added_nodes.add(subtopic)
        edges.append(Edge(source=topic, target=subtopic))
        
        sub_nodes, sub_edges = generate_subtopics_tree(subtopic, current_level + 1, max_level, progress_log, added_nodes, keyword_data, fetch_keywords,child_topics_count, generate_post)
        nodes.extend(sub_nodes)
        edges.extend(sub_edges)

    end_time = time.time()  # End the timer
    elapsed_time = end_time - start_time  # Calculate the elapsed time
    log_entry = f"Time taken for level {current_level} with topic '{topic}': {elapsed_time:.2f} seconds"
    progress_log.append(log_entry)  # Log the time taken
    
    return nodes, edges


def main():
    st.title("Intensive Topic Research with AI")

    # Sidebar setup
    with st.sidebar:
        st.write("Configuration")
        main_topic_keyword = st.text_input("Enter the main topic:", "")
        max_level = st.slider("Select the level of sub-leveling (1-5):", 1, 5, 1)
        child_topics_count = st.slider("Select the number of max child topics (3-10):", 3, 10, 3)
        fetch_keywords = st.checkbox("Fetch Keyword Data", False)  # Checkbox for fetching keyword data
        generate_posts = st.checkbox("Generate Blog Post Drafts", False)
        
        
        Physics = st.checkbox("Physics", False) 
        hierarchical = st.checkbox("hierarchical", False) 

    

    if "nodes" not in st.session_state or "edges" not in st.session_state or "keyword_data" not in st.session_state:
        st.session_state.nodes = []
        st.session_state.edges = []
        st.session_state.progress_log = []
        st.session_state.keyword_data = []

    if st.button("Start"):
        st.session_state.progress_log = []
        st.session_state.keyword_data = []
        added_nodes = set()
        
        with st.spinner("Generating..."):
            start_time = time.time()  # Start the timer for the entire operation
            st.session_state.nodes, st.session_state.edges = generate_subtopics_tree(
                main_topic_keyword, 1, max_level, st.session_state.progress_log, added_nodes, st.session_state.keyword_data,
                fetch_keywords=fetch_keywords,child_topics_count=child_topics_count, generate_post=generate_posts
            )
            end_time = time.time()  # End the timer for the entire operation
            elapsed_time = end_time - start_time  # Calculate the elapsed time for the entire operation
            st.session_state.progress_log.append(f"Total time to generate: {elapsed_time:.2f} seconds")
        
    if st.session_state.nodes:
        config = Config(
            width=800,
            height=800,
            directed=True,
            physics=Physics,
            hierarchical=hierarchical,
            nodeHighlightBehavior=True,
            highlightColor="#F7A7A6",  # Color of the highlight
            collapsible=True  # Enable collapsible nodes
        )
        agraph(nodes=st.session_state.nodes, edges=st.session_state.edges, config=config)

    with st.expander("Detailed Log"):
        for log_entry in st.session_state.progress_log:
            st.write(log_entry)

    with st.expander("Keyword Data"):
        for data in st.session_state.keyword_data:
            st.write(data)

if __name__ == "__main__":
    main()
