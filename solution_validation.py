import random
import numpy as np
import time
import matplotlib.pyplot as plt
from datetime import datetime


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
    if not rushHour:
        print("r"+str(rushHourViolationNum), end="")
    if not maxWorkingHour:
        print("w"+str(maxWorkingHourViolationNum), end="")
    return demandFlag and rushHour and maxWorkingHour


initial_prob = 0.3 # # here I am going to start small
pusan_prob = 0.2
population_size = 20
elitism_cutoff = 2
mutation_num = 1 #
loop_limit = 100
evolution_depth = 30000
max_iter_num = 20000

"""initialization for buses"""
# # of buses
N = 19 #
# #seats on each bus
D = 50
tolerance = 0
intervalDuration = 0.5
# numerical example
demand = np.array([
    [114,106,132,132,117,83,57,52,13,8,18,13,26,3,13,10,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0], 
    [0,0,0,0,0,0,14,2,0,7,12,7,9,5,7,7,12,9,32,39,53,35,30,18,60,44,60,53,90,58,78,71,35,55]
])
# testing
# demand = np.array([
#     [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 
#     [0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
# ])
demand_JQJY = demand
demand_JQJY = demand_JQJY.astype(int)
demand_PS = np.around(demand / 9)
demand_PS = demand_PS.astype(int)

intervalNum = demand.shape[-1]
maxWorkingHour = 4
checkDemandFlag, checkRushHourFlag, checkMaxWorkingHourFlag = True, True, True
alpha, demandViolationPenalty, rushHourViolationPenalty, maxWorkingHourViolationPenalty = 1, 100, 100, 100


best_solution = \
['00001010000000100010000000000000000000001001000001010101010100000000',
 '10100010100000001000001010101000001000001000101010100000001010100000',
 '00001000000010100000100000100010100000100000000010000100000000000000',
 '00000010100010100010000010100000001010001000100000001000000000000000',
 '00100000100000000000100000000000000010100000000100000000000000000000',
 '01100000001001010001010000000000000000000000000000000000000000000000',
 '00000000100010101000001000100000000000001000100000101000001010000000',
 '00000100000010000000001010101000100001010100000000000000000000000000',
 '00000000000000000110101000001000000000001010001000001010100010001010',
 '00000000011000000000000000001000000101000000000001000100000001000000',
 '10000010100000001000000010001010000000000000100000100000101000101010',
 '00000001010101010101000101010101000000000000000000000000000000000000',
 '00010000100000000010010101000000000000000000000000000000000000000000',
 '00100010000010001010001010001010010000000000000000000000000000000000',
 '00000010101000100000001001010101000000000000010000000000000000000000',
 '00001000000000101010001000000010001010000000100010100010101010001000',
 '00000000000001000010100000101000101000010100000000000000010000000000',
 '10000010101000101010100000000000000000100010001000100000001000010101',
 '00100000000010000000000000001000001000000000000000100000100000100100']


allFeasibilityFlag = check_feasibility(best_solution, checkRushHour=checkRushHourFlag, checkMaxWorkingHour=checkMaxWorkingHourFlag)
print('Double Checking feasibility:', allFeasibilityFlag)
fitness_score = fitness(best_solution)
print('Fitness Score:', fitness_score)
