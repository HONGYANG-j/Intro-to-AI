import streamlit as st
import random

# --- STREAMLIT PAGE SETTINGS ---
st.set_page_config(page_title="Genetic Algorithm Demo", page_icon="🧬")

st.title("🧬 Genetic Algorithm Simulator")

st.subheader("Problem Requirements")
st.markdown("""
1. **Population size:** 300  
2. **Fitness rule:** Maximum value when number of `1`s = 50  
3. **Chromosome length:** 80 bits  
4. **Maximum fitness:** Returns **80** only if `ones = 50`  
5. **Number of generations:** 50  
""")

# --- FIXED GA PARAMETERS AS PER REQUIREMENTS ---
POPULATION_SIZE = 300
CHROMOSOME_LENGTH = 80
GENERATIONS = 50
MUTATION_RATE = 0.01  # can stay default

st.divider()

st.subheader("Genetic Algorithm Output")

# ---------------------------------------------
# FITNESS FUNCTION (Requirement #2 and #4)
# ---------------------------------------------
def fitness(individual):
    ones = sum(individual)
    return 80 if ones == 50 else ones  # max fitness = 80 if exactly 50 ones

# ---------------------------------------------
# GA OPERATORS
# ---------------------------------------------
def generate_individual():
    # Requirement #3: chromosome length is 80 bits
    return [random.randint(0, 1) for _ in range(CHROMOSOME_LENGTH)]

def create_population():
    # Requirement #1: population size is 300
    return [generate_individual() for _ in range(POPULATION_SIZE)]

def selection(population):
    # Tournament selection
    a, b = random.sample(population, 2)
    return a if fitness(a) > fitness(b) else b

def crossover(p1, p2):
    point = random.randint(1, CHROMOSOME_LENGTH - 1)
    return p1[:point] + p2[point:], p2[:point] + p1[point:]

def mutate(individual):
    return [bit if random.random() > MUTATION_RATE else 1 - bit for bit in individual]

# ---------------------------------------------
# RUN GENETIC ALGORITHM
# Requirement #5: run for 50 generations
# ---------------------------------------------
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

        # Keep best 300 individuals
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
