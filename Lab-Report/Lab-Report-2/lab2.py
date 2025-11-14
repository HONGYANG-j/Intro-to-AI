import random

# --- GA PARAMETERS ---
POPULATION_SIZE = 300
CHROMOSOME_LENGTH = 80
GENERATIONS = 50

# Fitness: maximum value when number of ones = 50
def fitness(individual):
    ones = sum(individual)
    return 80 if ones == 50 else ones

# Generate random individual
def generate_individual():
    return [random.randint(0, 1) for _ in range(CHROMOSOME_LENGTH)]

# Create initial population
def create_population():
    return [generate_individual() for _ in range(POPULATION_SIZE)]

# Selection: tournament
def selection(population):
    a, b = random.sample(population, 2)
    return a if fitness(a) > fitness(b) else b

# Crossover: single point
def crossover(parent1, parent2):
    point = random.randint(1, CHROMOSOME_LENGTH - 1)
    return parent1[:point] + parent2[point:], parent2[:point] + parent1[point:]

# Mutation
def mutate(individual, mutation_rate=0.01):
    return [bit if random.random() > mutation_rate else 1-bit for bit in individual]

# Main GA
population = create_population()

for generation in range(GENERATIONS):
    new_population = []

    for _ in range(POPULATION_SIZE):
        # Select parents
        parent1 = selection(population)
        parent2 = selection(population)

        # Crossover
        child1, child2 = crossover(parent1, parent2)

        # Mutation
        child1 = mutate(child1)
        child2 = mutate(child2)

        new_population.extend([child1, child2])

    # Keep best 300
    population = sorted(new_population, key=fitness, reverse=True)[:POPULATION_SIZE]

    # Best fitness of generation
    best_score = fitness(population[0])
    print(f"Generation {generation+1}: Best Fitness = {best_score}")

# Final result
print("\nBest Individual Found:")
print("Bitstring:", population[0])
print("Fitness:", fitness(population[0]))
