import multiprocessing as mp
import time
import sys
import argparse
import os
import random
import numpy as np
import math

node_num = 0
edge_num = 0
model = ''
start_time = time.time()
time_limitat = 60


class Node(object):
    def __init__(self, index: int):
        self.index = index
        self.iteration = -1
        self.child_list = []
        self.child_weight = []
        self.father_node = None
        self.threshold = random.random()
        self.in_degree = 0
        self.out_degree = 0
        self.active = False
        self.visited = False

    def set_active(self):
        self.active = True

    def set_visited(self):
        self.visited = True


def ise_IC(graph: list, activate_seed: list, run_round: int):
    activate_counter = len(activate_seed)
    return_list = list()
    return_list.append(activate_seed[0])
    while (len(activate_seed) > 0):
        next_activate_seed = []
        for current_node in activate_seed:
            for child_node_index in range(len(current_node.child_list)):
                child_node = graph[current_node.child_list[child_node_index]]
                child_weight = current_node.child_weight[child_node_index]
                if child_node.iteration < run_round:
                    random_number = np.random.uniform(0, 1)
                    if random_number <= child_weight:
                        child_node.iteration = run_round
                        next_activate_seed.append(child_node)
                        return_list.append(child_node)
        activate_counter += len(next_activate_seed)
        activate_seed = next_activate_seed
    return return_list


def ise_LT(graph: list, activate_seed: list, run_round: int):
    for node in graph:
        if node.threshold == 0:
            activate_seed.append(node)
    activate_counter = len(activate_seed)
    while (len(activate_seed) > 0):
        next_activate_seed = []
        for current_node in activate_seed:
            for child_node_index in range(len(current_node.child_list)):
                child_node = graph[current_node.child_list[child_node_index]]
                child_weight = current_node.child_weight[child_node_index]
                child_node.threshold -= child_weight
                if child_node.threshold < 0 and child_node.iteration < run_round:
                    child_node.iteration = run_round
                    next_activate_seed.append(child_node)
        activate_counter += len(next_activate_seed)
        activate_seed = next_activate_seed
    return float(activate_counter)


def refresh_activate_seed(graph: list, activate_seed: list, run_round: int):
    for activate_index in activate_seed:
        graph[activate_index.index].iteration = run_round
    return graph


def initialize_LT(graph: list):
    for node in graph:
        node.threshold = np.random.uniform(0, 1)
    return graph


def go(graph: list, activate_seed: list, model: str, time_limit: int):
    sum = 0
    N = 1000000
    # N = 100
    start_time = time.time()
    counter = 0
    if model == "IC":
        for run_counter in range(N):
            np.random.seed(run_counter)
            graph = refresh_activate_seed(graph=graph, activate_seed=activate_seed, run_round=run_counter)
            sum += ise_IC(graph=graph, activate_seed=activate_seed, run_round=run_counter)
            current_time = time.time()
            counter = run_counter
            if current_time - start_time + 10 > time_limit:
                break
    else:
        # LT model
        for run_counter in range(N):
            np.random.seed(run_counter)
            graph = initialize_LT(graph=graph)
            graph = refresh_activate_seed(graph=graph, activate_seed=activate_seed, run_round=run_counter)
            sum += ise_LT(graph=graph, activate_seed=activate_seed, run_round=run_counter)
            current_time = time.time()
            counter = run_counter
            if current_time - start_time + 10 > time_limit:
                break
    # print("+++++++++++++++++")
    # print("total is ", sum/counter)
    # print("+++++++++++++++++")
    return sum / counter


def node_selection(mathcal_R, k):
    S_star_k = set()
    r_length = 0
    for i in mathcal_R:
        r_length += len(i)
    out_degree = [0 for _ in range(node_num)]
    for a in range(len(mathcal_R)):
        temp_set = mathcal_R[a]
        for key in temp_set.keys():
            out_degree[key - 1] += len(temp_set.get(key).neighbors)
    for b in range(k):
        max_id = out_degree.index(max(out_degree))
        S_star_k.add(max_id)
        out_degree[max_id] = 0
    count = 0
    for rrs in mathcal_R:
        for index in S_star_k:
            if index in rrs.keys():
                count += 1
    return list(S_star_k), count / r_length


def logcnk(n, k):
    up = 1
    down = 1
    for i in range(n - k + 1, n + 1):
        up = up * i
    for j in range(1, k + 1):
        down = down * j
    res = up / down
    return math.log(res)


def get_lambda_prime(epsilon_prime, k, mathcal_l):
    lambda_prime = ((2 + 2 * epsilon_prime / 3) * (
            logcnk(node_num, k) + mathcal_l * math.log(node_num) + math.log(math.log2(node_num))) * node_num) / pow(
        epsilon_prime, 2)
    return lambda_prime


def get_rr_IC(graph: list, node_index: int):
    np.random.seed(node_index)
    return_node_list = list()
    return_node_list.append(node_index)
    active_node = list()
    active_node.append(node_index)
    while return_node_list:
        new_active_set = list()
        for active_seed_index in return_node_list:
            for child_node_index in graph[active_seed_index].child_list:
                if child_node_index not in active_node:
                    if random.random() < graph[child_node_index].threshold:
                        active_node.append(child_node_index)
                        new_active_set.append(child_node_index)
        return_node_list = new_active_set
    return return_node_list


def get_rr_LT(graph: list, node_index: int):
    activity_nodes = list()
    activity_nodes.append(node_index)
    activity_set = list()
    activity_set.append(node_index)

    while activity_set != -1:
        new_activity_set = -1
        child_list = graph[node_index].child_list
        if len(child_list) == 0:
            break
        candidate = random.sample(child_list, 1)[0][0]
        if candidate not in activity_nodes:
            activity_nodes.append(candidate)
            new_activity_set = candidate
        activity_set = new_activity_set
    return activity_nodes


def get_rr_set(graph: list, node_index: int):
    rr_set = list()
    if model == 'IC':
        rr_set = get_rr_IC(graph, node_index)
    elif model == 'LT':
        rr_set = get_rr_LT(graph, node_index)
    return rr_set


def sampling(graph: list, k: int, epsilon: float, mathcal_l: float):
    mathcal_R = list()
    LB = 1
    epsilon_prime = math.sqrt(2) * epsilon
    for i in range(1, int(math.log2(node_num - 1)) + 1):
        x = node_num / (math.pow(2, i))
        lambda_prime = get_lambda_prime(epsilon_prime, k, mathcal_l)
        theta_i = lambda_prime / x
        while len(mathcal_R) <= theta_i:
            select_node_index = random.randint(1, node_num)
            rr_set = get_rr_set(graph, select_node_index)
            mathcal_R.append(rr_set)
        mathcal_S_i, F_mathcal_R = node_selection(mathcal_R)
        if node_num * F_mathcal_R >= (1 + epsilon_prime) * x:
            LB = node_num * F_mathcal_R / (1 + epsilon_prime)
            break
    alpha = math.sqrt(mathcal_l * math.log(node_num) + math.log(2))
    beta = math.sqrt((1 - 1 / math.e) * (logcnk(node_num, k) + mathcal_l * math.log(node_num) + math.log(2)))
    lambda_star = 2 * node_num * pow(((1 - 1 / math.e) * alpha + beta), 2) * pow(epsilon, -2)
    theta = lambda_star / LB
    while len(mathcal_R) <= theta:
        select_node_index = random.randint(1, node_num)
        rr_set = get_rr_set(select_node_index)
        mathcal_R.add(rr_set)
    return mathcal_R


def IMM(graph: list, k: int, epsilon: float, mathcal_l: float):
    mathcal_l = mathcal_l * (1 + math.log(2) / math.log(node_num))
    mathcal_R = sampling(graph, k, epsilon, mathcal_l)
    mathcal_S_k = node_selection(mathcal_R, k)
    return mathcal_S_k


if __name__ == '__main__':
    '''
    从命令行读参数示例
    '''
    # print("从命令行读参数示例")
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--file_name', type=str, default='network.txt')
    parser.add_argument('-k', '--seed_set_size', type=int, default=4)
    parser.add_argument('-m', '--model', type=str, default='IC')
    parser.add_argument('-t', '--time_limit', type=int, default=10)

    args = parser.parse_args()
    file_name = args.file_name
    seed_set_size = args.seed_set_size
    # global model
    model = args.model
    # global time_limit
    time_limit = args.time_limit

    with open(file_name, "r") as reader:
        file_network = reader.readlines()
    network_info = file_network[0].split(' ')

    graph = []
    # global node_num
    node_num = int(network_info[0]) + 1
    # global edge_num
    edge_num = int(network_info[1].replace("\n", ""))

    for node_counter in range(int(network_info[0]) + 1):
        graph.append(Node(node_counter))
    for edge_counter in range(int(network_info[1].replace("\n", ""))):
        edge_info = file_network[edge_counter + 1].split()
        node_father = graph[int(edge_info[0])]
        node_child = graph[int(edge_info[1])]
        node_father.child_list.append(int(edge_info[1]))
        node_father.child_weight.append(float(edge_info[2].replace("\n", "")))
        node_child.father_node = node_father
        node_father.out_degree += 1
        node_child.in_degree += 1

    # for node in graph:
    #     for child in node.child_list:
    #         if (child > 62):
    #             print(child)
    #             print(node.index)
    epsilon = 0.5
    mathcal_l = 1

    # seeds = IMM(epsilon, mathcal_l, epsilon, mathcal_l)
    seeds = IMM(graph, node_num, epsilon, mathcal_l)
    for seed in seeds:
        print(seed)

    '''
    程序结束后强制退出，跳过垃圾回收时间, 如果没有这个操作会额外需要几秒程序才能完全退出
    '''
    sys.stdout.flush()
