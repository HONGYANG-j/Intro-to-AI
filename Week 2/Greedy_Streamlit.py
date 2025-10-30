

import streamlit as st

# Define the graph as a dictionary of dictionaries
# In the graph dictionary, the keys are the nodes and the values are dictionaries of the neighbors with their edge weights.
graph = {
    'A': {'B': 1, 'C': 4},
    'B': {'C': 2, 'D': 5},
    'C': {'D': 3},
    'D': {}
}

# Define the heuristic function as the distance to the goal
# In the heuristic dictionary, the keys are the nodes and the values are the heuristic values for each node.
heuristic = {'A': 8, 'B': 7, 'C': 4, 'D': 0}

# Define the Greedy Best-First Search algorithm
def greedy_best_first_search(start, goal):
    open_list = [start]
    closed_list = []
    came_from = {start: None}
    g_score = {start: 0}
    f_score = {start: heuristic[start]}

    while open_list:
        current = min(open_list, key=lambda x: f_score[x])
        if current == goal:
            return reconstruct_path(came_from, current)

        open_list.remove(current)
        closed_list.append(current)

        for neighbor in graph[current]:
            tentative_g_score = g_score[current] + graph[current][neighbor]
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic[neighbor]
                if neighbor not in open_list:
                    open_list.append(neighbor)

    return None

# Define the function to reconstruct the path
def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]

# Define the main function
def main():
    # Set up the Streamlit app
    st.title("Greedy Best-First Search Algorithm")

    # Get user input for the start and goal nodes
    start = st.text_input("Start Node:")
    goal = st.text_input("Goal Node:")

    if st.button("Search"):
        if start and goal:
            if start in graph and goal in graph:
                path = greedy_best_first_search(start, goal)

                if path:
                    st.write("Path from", start, "to", goal, "is:", path)
                else:
                    st.write("No path from", start, "to", goal)

            else:
                st.write("Invalid start or goal node")

        else:
            st.write("Please enter start and goal nodes")

# Run the app
if __name__ == "__main__":
    main()