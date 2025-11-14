import random

# -----------------------------------------------------------
#  Genetic Algorithm Requirements (given conditions)
# -----------------------------------------------------------
POPULATION_SIZE = 300          # 1. Population size = 300
CHROMOSOME_LENGTH = 80         # 3. All individuals = 80 bits
GENERATIONS = 50               # 5. Run for 50 generations
TARGET_ONES = 50               # 2. Max value when ones = 50
MAX_FITNESS = 80               # 4. Fitness returns 80 when ones = 50
MUTATION_RATE = 0.01           # Standard value

# -----------------------------------------------------------
#  Fitness Function (Requirement #2 & #4)
# -----------------------------------------------------------
def fitness(individual):
    ones = sum(individual)
    return MAX_FITNESS if ones == TARGET_ONES else ones

# -----------------------------------------------------------
#  Generate 1 Individual (80-bit chromosome)
# -----------------------------------------------------------
def generate_individual():
    return [random.randint(0, 1) for _ in range(CHROMOSOME_LENGTH)]

# -----------------------------------------------------------
#  Generate Initial Population (size = 300)
# -----------------------------------------------------------
def create_population():
    return [generate_individual() for _ in range(POPULATION_SIZE)]

# -----------------------------------------------------------
#  Selection (Tournament)
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
#  Main GA Loop (Requirement #5: 50 generations)
# -----------------------------------------------------------
population = create_population()

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

    # Output generation best
    best_score = fitness(population[0])
    print(f"Generation {generation+1}: Best Fitness = {best_score}")

# -----------------------------------------------------------
#  Final Output
# -----------------------------------------------------------
print("\nBest Individual Found:")
print("Bitstring:", "".join(map(str, population[0])))
print("Fitness:", fitness(population[0]))
