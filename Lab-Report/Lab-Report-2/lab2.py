import streamlit as st
import random

# --- STREAMLIT PAGE SETTINGS ---
st.set_page_config(page_title="Genetic Algorithm Demo", page_icon="🧬")

st.title("🧬 Genetic Algorithm Simulator")
st.write("This app runs a simple Genetic Algorithm to optimize a bitstring of length 80.")

# --- GA PARAMETERS (editable by user) ---
POPULATION_SIZE = st.slider("Population Size", 50, 500, 300)
CHROMOSOME_LENGTH = 80
GENERATIONS = st.slider("Number of Generations", 10, 200, 50)
MUTATION_RATE = st.slider("Mutation Rate", 0.001, 0.1, 0.01)

st.divider()

st.subheader("Genetic Algorithm Output")

# --- FITNESS FUNCTION ---
def fitness(individual):
    ones = sum(individual)
    return 80 if ones == 50 else ones  # 80 = max score

# --- GA OPERATORS ---
def generate_individual():
    return [random.randint(0, 1) for _ in range(CHROMOSOME_LENGTH)]

def create_population():
    return [generate_individual() for _ in range(POPULATION_SIZE)]

def selection(population):
    a, b = random.sample(population, 2)
    return a if fitness(a) > fitness(b) else b

def crossover(p1, p2):
    point = random.randint(1, CHROMOSOME_LENGTH - 1)
    return p1[:point] + p2[point:], p2[:point] + p1[point:]

def mutate(individual):
    return [bit if random.random() > MUTATION_RATE else 1-bit for bit in individual]

# Run GA only when button is clicked
if st.button("Run Genetic Algorithm"):
    population = create_population()
    best_scores = []

    progress = st.progress(0)
    status = st.empty()

    for generation in range(GENERATIONS):
        new_population = []

        for _ in range(POPULATION_SIZE):
            parent1 = selection(population)
            parent2 = selection(population)

            child1, child2 = crossover(parent1, parent2)
            child1 = mutate(child1)
            child2 = mutate(child2)

            new_population.extend([child1, child2])

        # Keep best individuals
        population = sorted(new_population, key=fitness, reverse=True)[:POPULATION_SIZE]

        best_score = fitness(population[0])
        best_scores.append(best_score)

        progress.progress((generation + 1) / GENERATIONS)
        status.write(f"Generation {generation+1}: Best Fitness = {best_score}")

    st.success("Genetic Algorithm Completed!")

    st.subheader("Best Individual Found")
    st.write("Bitstring:", "".join(map(str, population[0])))
    st.write("Fitness:", fitness(population[0]))

    st.line_chart(best_scores)
