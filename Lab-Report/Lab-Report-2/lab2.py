import streamlit as st
import random

# -----------------------------------------------------------
#  Genetic Algorithm Parameters (Given Conditions)
# -----------------------------------------------------------
POPULATION_SIZE = 300          # 1. Population size = 300
CHROMOSOME_LENGTH = 80         # 3. Chromosome length = 80
GENERATIONS = 50               # 5. Run for 50 generations
TARGET_ONES = 50               # 2. Max value when ones = 50
MAX_FITNESS = 80               # 4. Return value = 80 when ones = 50
MUTATION_RATE = 0.01           # Standard mutation rate (keeps diversity)

# -----------------------------------------------------------
#  Fitness Function
# -----------------------------------------------------------
def fitness(individual):
    ones = sum(individual)
    return MAX_FITNESS if ones == TARGET_ONES else ones

# -----------------------------------------------------------
#  Generate Individual
# -----------------------------------------------------------
def generate_individual():
    return [random.randint(0, 1) for _ in range(CHROMOSOME_LENGTH)]

# -----------------------------------------------------------
#  Initial Population
# -----------------------------------------------------------
def create_population():
    return [generate_individual() for _ in range(POPULATION_SIZE)]

# -----------------------------------------------------------
#  Tournament Selection
# -----------------------------------------------------------
def selection(population):
    a, b = random.sample(population, 2)
    return a if fitness(a) > fitness(b) else b

# -----------------------------------------------------------
#  Single-Point Crossover
# -----------------------------------------------------------
def crossover(p1, p2):
    point = random.randint(1, CHROMOSOME_LENGTH - 1)
    return p1[:point] + p2[point:], p2[:point] + p1[point:]

# -----------------------------------------------------------
#  Mutation
# -----------------------------------------------------------
def mutate(individual):
    return [bit if random.random() > MUTATION_RATE else 1 - bit for bit in individual]

# -----------------------------------------------------------
#  Streamlit UI
# -----------------------------------------------------------
st.title("🧬 Genetic Algorithm Bit Pattern Generator")
st.write("This GA generates an 80-bit pattern following:")
st.write("""
- Population size: **300**  
- Chromosome length: **80 bits**  
- Maximum fitness when number of ones = **50**  
- Fitness = **80** when ones = 50  
- Total generations: **50**
""")

if st.button("Run Genetic Algorithm"):
    st.info("Running GA... Please wait.")

    population = create_population()
    generation_logs = []

    # Genetic Algorithm Loop
    for generation in range(GENERATIONS):
        new_population = []

        for _ in range(POPULATION_SIZE):
            parent1 = selection(population)
            parent2 = selection(population)

            child1, child2 = crossover(parent1, parent2)

            child1 = mutate(child1)
            child2 = mutate(child2)

            new_population.extend([child1, child2])

        population = sorted(new_population, key=fitness, reverse=True)[:POPULATION_SIZE]

        best_score = fitness(population[0])
        generation_logs.append(f"Generation {generation+1}: Best Fitness = {best_score}")

    # Display Logs
    st.subheader("📈 Generation Log")
    for line in generation_logs:
        st.write(line)

    # Final Output
    best_individual = population[0]
    ones_count = sum(best_individual)

    st.subheader("🏆 Best Individual Found")
    st.code("".join(map(str, best_individual)))
    st.write(f"**Fitness:** {fitness(best_individual)}")
    st.write(f"**Number of 1s:** {ones_count}")

    if ones_count == TARGET_ONES:
        st.success("Perfect solution found! 🎉")
    else:
        st.warning("Did not reach exactly 50 ones, but best pattern is shown.")

