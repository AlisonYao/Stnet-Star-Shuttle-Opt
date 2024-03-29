"""
Author: Yuhan Yao (yy2564@nyu.edu)
Date: Feb 12, 2022
"""

import random
import numpy as np
import time
import matplotlib.pyplot as plt
from datetime import datetime


def generate_random_N_paths(N, path_length):
    '''
    Randomize N paths where each path is like 00 01 00 01 01 01
    '''
    one_solution = []
    while len(one_solution) < N:
        one_path_single_digit = random.choices(population=[0, 1], weights=[1-initial_prob, initial_prob], k=path_length)
        one_path_double_digit = ''
        for i in one_path_single_digit:
            if i == 0:
                one_path_double_digit += '00'
            elif i == 1:
                one_path_double_digit += random.choices(population=['10', '01'], weights=[1-pusan_prob, pusan_prob])[0]
        if check_path_integrity(one_path_double_digit):
            one_solution.append(one_path_double_digit)
    return one_solution

def check_solution_integrity(solution):
    for one_path_double_digit in solution:
        if not check_path_integrity(one_path_double_digit):
            return False
    return True

def check_path_integrity(one_path_double_digit):
    last_visited = None
    for i in range(len(one_path_double_digit)):
        if i % 2 == 0:
            two_digits = one_path_double_digit[i:i+2]
            if two_digits != '00':
                # first time going to AB
                if last_visited is None:
                    last_visited = 'AB'
                # following times
                elif last_visited == 'JQJY':
                    if two_digits == '01':
                        return False
                    else: # '10'
                        last_visited = 'AB'
                elif last_visited == 'PS':
                    if two_digits == '10':
                        return False
                    else: # '01'
                        last_visited = 'AB'
                else:
                    if two_digits == '10':
                        last_visited = 'JQJY'
                    else: # '01'
                        last_visited = 'PS'
    return True

def decode_one_path(one_path_double_digit):
    decoded, initial_node, last_visited = [], None, None
    for i in range(len(one_path_double_digit)):
        if i % 2 == 0:
            two_digits = one_path_double_digit[i:i+2]
            if two_digits == '00':
                if last_visited is None:
                    decoded.append([0, 0, 0, 0, 0, 0, 0])
                elif last_visited == 'JQJY':
                    decoded.append([1, 0, 0, 0, 0, 0, 0])
                elif last_visited == 'AB':
                    decoded.append([0, 0, 0, 1, 0, 0, 0])
                else: # PS
                    decoded.append([0, 0, 0, 0, 0, 0, 1])
            elif two_digits == '10':
                if last_visited is None:
                    initial_node = 0
                    last_visited = 'AB'
                    decoded.append([0, 1, 0, 0, 0, 0, 0])
                elif last_visited == 'AB':
                    last_visited = 'JQJY'
                    decoded.append([0, 0, 1, 0, 0, 0, 0])
                elif last_visited == 'JQJY':
                    last_visited = 'AB'
                    decoded.append([0, 1, 0, 0, 0, 0, 0])
                else:
                    print('SOMETHING IS WRONG1!!!')
            elif two_digits == '01':
                if last_visited is None:
                    initial_node = -1
                    last_visited = 'AB'
                    decoded.append([0, 0, 0, 0, 0, 1, 0])
                elif last_visited == 'AB':
                    last_visited = 'PS'
                    decoded.append([0, 0, 0, 0, 1, 0, 0])
                elif last_visited == 'PS':
                    last_visited = 'AB'
                    decoded.append([0, 0, 0, 0, 0, 1, 0])
                else:
                    print('SOMETHING IS WRONG2!!!')
    decoded = np.array(decoded).T
    decoded_sum = decoded.sum(axis=0)
    if sum(decoded_sum) == 0:
        if random.random() <= pusan_prob:
            decoded[0, :] = 0
        else:
            decoded[0, :] = 1
        return decoded
    k = 0
    while decoded_sum[k] == 0:
        decoded[initial_node, k] = 1
        k += 1
    return decoded

def demand_constraint(binary_N_paths, tolerance):
    '''
    make sure the demand is met
    '''
    directional_N_paths = [decode_one_path(one_path) for one_path in binary_N_paths]
    link = sum(directional_N_paths)
    link_JQJY = link[:4, :]
    link_PS = link[-1:2:-1, :]
    JQJY_supply_demand_difference = np.greater_equal(demand_JQJY - tolerance, link_JQJY[1:3, :] * D)
    JQJY_mask = (demand_JQJY - tolerance) - (link_JQJY[1:3, :] * D)
    PS_supply_demand_difference = np.greater_equal(demand_PS - tolerance, link_PS[1:3, :] * D)
    PS_mask = (demand_PS - tolerance) - (link_PS[1:3, :] * D)
    missedDemandNumJQJY = np.sum(JQJY_supply_demand_difference * JQJY_mask)
    missedDemandNumPS = np.sum(PS_supply_demand_difference * PS_mask)
    return int(missedDemandNumJQJY + missedDemandNumPS) == 0, int(missedDemandNumJQJY + missedDemandNumPS)

def rush_hour_constraint(binary_N_paths):
    '''
    during rush hours, one interval is not enough time to commute
    '''
    violationCount = 0
    for one_path_double_digit in binary_N_paths:
        one_path_single_digit_list = []
        one_path_double_digit_list = list(one_path_double_digit)
        for i in range(len(one_path_double_digit_list)):
            if i % 2 == 0:
                one_path_single_digit_list.append(int(one_path_double_digit_list[i]) + int(one_path_double_digit_list[i+1]))
        # morning rush hour
        if one_path_single_digit_list[1] + one_path_single_digit_list[2] == 2:
            violationCount += 1
        # evening rush hour
        if one_path_single_digit_list[21] + one_path_single_digit_list[22] == 2:
            violationCount += 1
    return int(violationCount) == 0, int(violationCount)

def max_working_hour_constraint(binary_N_paths):
    '''
    make sure that no driver works more than a few hours continuously
    '''
    violationCount = 0
    for one_path_double_digit in binary_N_paths:
        one_path_single_digit_list = []
        one_path_double_digit_list = list(one_path_double_digit)
        for i in range(len(one_path_double_digit_list)):
            if i % 2 == 0:
                one_path_single_digit_list.append(int(one_path_double_digit_list[i]) + int(one_path_double_digit_list[i+1]))
        num, num_list = 0, []
        one_path_copy = one_path_single_digit_list.copy()
        # first check if rush hour 10 actually is 11.
        if checkRushHourFlag:
            if one_path_copy[1] == 1 and one_path_copy[2] == 0:
                one_path_copy[2] = 1
            if one_path_copy[21] == 1 and one_path_copy[22] == 0:
                one_path_copy[22] = 1
        for i, node in enumerate(one_path_copy):
            num += node
            if i+1 == len(one_path_copy):
                num_list.append(num)
                continue
            if node == 1 and one_path_copy[i+1] == 0:
                num_list.append(num)
                num = 0
        violationCount += sum(np.array(num_list) > maxWorkingHour / intervalDuration)
    return int(violationCount) == 0, int(violationCount)

def check_feasibility(binary_N_paths, checkDemand=True, checkRushHour=False, checkMaxWorkingHour=False):
    '''
    s.t. constraints (make sure initial paths & crossover paths & mutated paths are feasible)
    constraint1: meet demand
    constraint2: during rush hours, one interval is not enough time to commute (optional)
    constraint3: make sure that no driver works more than a few hours continuously
    '''
    demandFlag, rushHour, maxWorkingHour = True, True, True
    if checkDemand:
        demandFlag, demandViolationNum = demand_constraint(binary_N_paths, tolerance)
    if checkRushHour:
        rushHour, rushHourViolationNum = rush_hour_constraint(binary_N_paths)
    if checkMaxWorkingHour:
        maxWorkingHour, maxWorkingHourViolationNum = max_working_hour_constraint(binary_N_paths)
    if not demandFlag:
        print("d"+str(demandViolationNum), end="")
        f.write('d' + str(demandViolationNum))
    if not rushHour:
        print("r"+str(rushHourViolationNum), end="")
        f.write('r' + str(rushHourViolationNum))
    if not maxWorkingHour:
        print("w"+str(maxWorkingHourViolationNum), end="")
        f.write('w' + str(maxWorkingHourViolationNum))
    f.write('\n')
    return demandFlag and rushHour and maxWorkingHour

def fitness(binary_N_paths, addPenalty=False):
    """
    objective function ish -> natural selection to pick the good ones
    the lower the better!!
    """
    total_cost = 0
    # operation costs according to the path cost function
    for one_path_double_digit in binary_N_paths:
        one_path_single_digit_list = []
        one_path_double_digit_list = list(one_path_double_digit)
        for i in range(len(one_path_double_digit_list)):
            if i % 2 == 0:
                one_path_single_digit_list.append(int(one_path_double_digit_list[i]) + int(one_path_double_digit_list[i+1]))
        one_path_single_digit_np = np.array(one_path_single_digit_list)
        target_indices = np.where(one_path_single_digit_np == 1)[0]
        
        if len(target_indices) == 0:
            duration_interval_num = 0 # bus did not operate at all
        else:
            duration_interval_num = int(target_indices[-1] - target_indices[0] + 1)
        duration = duration_interval_num * intervalDuration

        if duration_interval_num == 0:
            total_cost += 0
        elif duration_interval_num == 1:
            total_cost += 75
        elif duration <= 6:
            if target_indices[0] == 0:
                assert target_indices[-1] <= 11
                total_cost += 110
            elif target_indices[0] >= 12:
                total_cost += 150
            else:
                total_cost += 153.2 * np.log10(6) + 7.22 * 6
        else:
            total_cost += 153.2 * np.log10(duration) + 7.22 * duration
    # add penalty
    if addPenalty:
        demandFlag, demandViolationNum = demand_constraint(binary_N_paths, tolerance)
        rushHour, rushHourViolatonNum = rush_hour_constraint(binary_N_paths)
        maxWorkingHour, maxWorkingHourViolationNum = max_working_hour_constraint(binary_N_paths)
        if checkDemandFlag:
            total_cost += alpha * demandViolationNum * demandViolationPenalty
        if checkRushHourFlag:
            total_cost += rushHourViolatonNum * rushHourViolationPenalty
        if maxWorkingHourViolationPenalty:
            total_cost += maxWorkingHourViolationNum * maxWorkingHourViolationPenalty
    return total_cost

def generate_population(population_size):
    population, fitness_scores_add_penalty = [], []
    for _ in range(population_size):
        binary_N_paths = generate_random_N_paths(N, intervalNum)
        population.append(binary_N_paths)
        fitness_score_add_penalty = fitness(binary_N_paths, addPenalty=True)
        fitness_scores_add_penalty.append(fitness_score_add_penalty)
    return np.array(population), np.array(fitness_scores_add_penalty)

def elitism(population, fitness_scores, elitism_cutoff=2):
    elite_indices = np.argpartition(np.array(fitness_scores), elitism_cutoff)[:elitism_cutoff]
    return population[elite_indices, :]

def create_next_generation(population, population_fitnesses_add_penalty, population_size, elitism_cutoff):
    """
    Randomly pick the good ones and cross them over
    """
    children = []
    while True:
        parents = random.choices(
            population=population,
            weights=[(max(population_fitnesses_add_penalty) - score + 1)/(max(population_fitnesses_add_penalty) * len(population_fitnesses_add_penalty) - sum(population_fitnesses_add_penalty) + len(population_fitnesses_add_penalty)) for score in population_fitnesses_add_penalty],
            k=2
        )
        kid1, kid2 = single_point_crossover(parents[0], parents[1])
        kid1 = single_mutation(kid1)
        children.append(kid1)
        if len(children) == population_size - elitism_cutoff:
            return np.array(children)
        kid2 = single_mutation(kid2)
        children.append(kid2)
        if len(children) == population_size - elitism_cutoff:
            return np.array(children)

def single_point_crossover(parent1, parent2):
    """
    Randomly pick the good ones and cross them over
    """
    assert parent1.size == parent2.size
    length = len(parent1)
    if length < 2:
        return parent1, parent2
    count = 0
    while count <= loop_limit:
        cut = random.randint(1, length - 1) * 2
        kid1 = np.array(list(parent1)[:cut] + list(parent2)[cut:])
        kid2 = np.array(list(parent2)[:cut] + list(parent1)[cut:])
        if check_solution_integrity(kid1) and check_solution_integrity(kid2):
            return kid1, kid2
        elif check_solution_integrity(kid1) and not check_solution_integrity(kid2):
            return kid1, None
        elif not check_solution_integrity(kid1) and check_solution_integrity(kid2):
            return None, kid2
        count += 1
    return parent1, parent2

def single_mutation(binary_N_paths):
    """
    Mutate only one node in one path for now
    """
    count = 0
    binary_N_paths_copy = binary_N_paths.copy()
    while count <= loop_limit:
        mutate_path = np.random.randint(0, N)
        mutate_index = np.random.randint(0, intervalNum) * 2
        double_digits_to_mutate = binary_N_paths_copy[mutate_path][mutate_index:mutate_index+2]
        pool = ['00', '01', '10']
        pool.remove(double_digits_to_mutate)
        mutated_double_digits = random.choices(population=pool)[0]
        original_string = binary_N_paths_copy[mutate_path]
        mutated_string = original_string[:mutate_index] + mutated_double_digits + original_string[mutate_index+2:]
        if check_path_integrity(mutated_string):
            binary_N_paths_copy[mutate_path] = mutated_string
            return binary_N_paths_copy
        count += 1
    return binary_N_paths

def result_stats(progress_with_penalty, progress):
    """
    print important stats & visulize progress_with_penalty
    """
    print('**************************************************************')
    print(f"Progress_with_penalty of improvement: {progress_with_penalty[0]} to {progress_with_penalty[-1]}")
    print(f"Progress of improvement: {progress[0]} to {progress[-1]}")
    print("Improvement Rate of progress:", abs(progress[-1] - progress[0])/progress[0])
    print('**************************************************************')
    # write to file
    f.write('**************************************************************' + '\n')
    f.write("Progress_with_penalty of improvement: " + str(progress_with_penalty[0]) + " to " + str(progress_with_penalty[-1]) + '\n')
    f.write("Progress of improvement: " + str(progress[0]) + ' to ' + str(progress[-1]) + '\n')
    f.write("Improvement Rate of progress: " + str(abs(progress[-1] - progress[0])/progress[0]) + '\n')
    f.write('**************************************************************' + '\n')
    # show plot
    plt.plot(progress_with_penalty, data=progress_with_penalty, label='Fitness Score')
    plt.plot(progress, data=progress, label='Operation Cost')
    plt.xlabel("Generation")
    plt.ylabel("Cost")
    plt.legend()
    # plt.show()
    plt.savefig(str(save_name) + '.png')
    plt.clf()

def run_evolution(population_size, evolution_depth, elitism_cutoff):
    '''
    Main function of Genetic Algorithm
    '''
    tic = time.time()

    # first initialize a population 
    population, population_fitnesses_add_penalty = generate_population(population_size)
    initialization_end = time.time()
    print(f'\nInitialization Done! Time: {initialization_end - tic:.6f}s')
    population_fitnesses = [fitness(binary_N_paths) for binary_N_paths in population]
    print(f'Initial Min Cost: {min(population_fitnesses_add_penalty)} -> {min(population_fitnesses)}')
    # keep track of improvement
    progress_with_penalty, progress = [], []
    allFeasibilityFlag = False
    i = 0
    ii = 0
    startover = False

    # start evolving :)
    while (allFeasibilityFlag is False) or (ii <= evolution_depth):
        progress_with_penalty.append(min(population_fitnesses_add_penalty))
        progress.append(min(population_fitnesses))
        print(f'----------------------------- generation {i + 1} Start! -----------------------------')
        elitism_begin = time.time()
        elites = elitism(population, population_fitnesses_add_penalty, elitism_cutoff)
        children = create_next_generation(population, population_fitnesses_add_penalty, population_size, elitism_cutoff)
        population = np.concatenate([elites, children])
        population_fitnesses_add_penalty = [fitness(binary_N_paths, addPenalty=True) for binary_N_paths in population]
        population_fitnesses = [fitness(binary_N_paths) for binary_N_paths in population]
        
        evol_end = time.time()
        print(f"Min Cost: {min(population_fitnesses_add_penalty)} -> {min(population_fitnesses)}")
        # check best solution feasibility
        minIndex = population_fitnesses_add_penalty.index(min(population_fitnesses_add_penalty))
        best_solution = population[minIndex]
        allFeasibilityFlag = check_feasibility(best_solution, checkRushHour=checkRushHourFlag, checkMaxWorkingHour=checkMaxWorkingHourFlag)
        print("\nAll constraints met?", allFeasibilityFlag)

        # best solution
        directional_N_paths = [decode_one_path(one_path) for one_path in population[minIndex]]
        link = sum(directional_N_paths)

        print(f'---------------------- generation {i + 1} evolved! Time: {evol_end - elitism_begin:.4f}s ----------------------\n')

        i += 1
        if allFeasibilityFlag:
            ii += 1
        
        if i % 20 == 0:
            f.write('----------------------------- generation ' + str(i+1) + ' Start! -----------------------------\n')
            f.write('Min Cost Penalty: ' + str(min(population_fitnesses_add_penalty)) + ' -> ' + str(min(population_fitnesses)) + '\n')

        if i - ii >= max_iter_num:
            startover = True
            break
    
    if startover:
        print('need to start over')
        return False
    else:
        print('no need to start over')
        # plot results
        result_stats(progress_with_penalty, progress)

        # print best solution
        minIndex = population_fitnesses_add_penalty.index(min(population_fitnesses_add_penalty))
        best_solution = population[minIndex]
        print('best solution (path):\n', best_solution)
        f.write('best solution (path):\n' + str(best_solution) + '\n')

        # check if all constraints are met (ideally True)
        print("\nAll constraints met?", check_feasibility(best_solution, checkDemand=checkDemandFlag, checkRushHour=checkRushHourFlag, checkMaxWorkingHour=checkMaxWorkingHourFlag))
        f.write("All constraints met? " + str(check_feasibility(best_solution, checkDemand=checkDemandFlag, checkRushHour=checkRushHourFlag, checkMaxWorkingHour=checkMaxWorkingHourFlag)) + '\n')
        directional_N_paths = [decode_one_path(one_path) for one_path in population[minIndex]]
        link = sum(directional_N_paths)
        print('best solution (link): \n', link)
        f.write('best solution (link): \n' + str(link) + '\n')
        f.write('#iteration: ' + str(i) + '\n')
        return True

if __name__ == "__main__":

    SUCCESS = False

    """initialization for genetic algo"""
    # starting from a lower initial_prob will give you fewer 1s, 
    # then demand constraint is violated, 
    # but rush hour constraint and max working hour constraint are likely to be satisfied
    # starting from a higher initial_prob will give you more 1s,
    # then demand constraint is unlikely to be violated,
    # but rush hour constraint and max working hour constraint are probably violated.
    # So there's the tradeoff
    initial_prob = 0.3 # # here I am going to start small
    pusan_prob = 0.2
    population_size = 20
    elitism_cutoff = 2
    loop_limit = 100
    evolution_depth = 30000
    max_iter_num = 20000

    """initialization for buses"""
    # # of buses
    N = 19
    # #seats on each bus
    D = 50 # this is C in the paper
    tolerance = 0 # this is W in the paper
    intervalDuration = 0.5
    # numerical example
    demand = np.array([
        [114,106,132,132,117,83,57,52,13,8,18,13,26,3,13,10,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0], 
        [0,0,0,0,0,0,14,2,0,7,12,7,9,5,7,7,12,9,32,39,53,35,30,18,60,44,60,53,90,58,78,71,35,55]
    ])
    demand_JQJY = demand
    demand_JQJY = demand_JQJY.astype(int)
    demand_PS = np.around(demand / 9)
    demand_PS = demand_PS.astype(int)

    intervalNum = demand.shape[-1]
    maxWorkingHour = 4 # this is Q in the paper
    checkDemandFlag, checkRushHourFlag, checkMaxWorkingHourFlag = True, True, True
    alpha, demandViolationPenalty, rushHourViolationPenalty, maxWorkingHourViolationPenalty = 1, 100, 100, 100

    # run main function & save everything to txt and png
    while not SUCCESS:
        save_name =  'test_results/'+str(evolution_depth)+'_'+str(initial_prob)+'_N'+str(N)+'_'+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+'_nv'
        f = open(save_name + '.txt', 'w')
        f.write('initial_prob: ' + str(initial_prob) + '\n')
        f.write('pusan_prob: ' + str(pusan_prob) + '\n')
        f.write('population_size: ' + str(population_size) + '\n')
        f.write('elitism_cutoff: ' + str(elitism_cutoff) + '\n')
        f.write('loop_limit: ' + str(loop_limit) + '\n')
        f.write('evolution_depth: ' + str(evolution_depth) + '\n')
        f.write('max_iter_num: ' + str(max_iter_num) + '\n')
        f.write('N: ' + str(N) + '\n')
        f.write('D: ' + str(D) + '\n')
        f.write('tolerance: ' + str(tolerance) + '\n')
        f.write('intervalDuration:' + str(intervalDuration) + '\n')
        f.write('demand:' + str(demand) + '\n')
        f.write('maxWorkingHour: ' + str(maxWorkingHour) + '\n')
        f.write('alpha, demandViolationPenalty, rushHourViolationPenalty, maxWorkingHourViolationPenalty: '+str(alpha)+', '+str(demandViolationPenalty)+', '+str(rushHourViolationPenalty)+', '+str(maxWorkingHourViolationPenalty)+'\n')
        start_time = time.time()
        SUCCESS = run_evolution(population_size, evolution_depth, elitism_cutoff)
        end_time = time.time()
        f.write('total run time: ' + str(end_time - start_time) + 's')
        f.close()
