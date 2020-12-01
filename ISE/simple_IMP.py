# -*- coding: utf-8 -*-
# written by mark zeng 2018-11-14
# modified by Yao Zhao 2019-10-30
# re-modified by Yiming Chen 2020-11-04

import multiprocessing as mp
import time
import sys
import argparse
import os
import random
import numpy as np
import math

core = 8
model = ''
# time_limit = 60
# time_limit = 10
graph = []


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


def node_selection(rr_set: list, k: int):
    Sk = set()
    r_set_length = 0
    for rr in rr_set:
        r_set_length += len(rr)
    out_degree = [0 for index in range(node_num)]
    for i in range(len(rr_set)):
        temp_rr = rr_set[i]
        for rr_list in temp_rr.keys():
            out_degree[rr_list - 1] += len(graph[rr_list].child_list)
    for b in range(k):
        max_index = out_degree.index(max(out_degree))
        Sk.add(max_index)
        out_degree[max_index] = 0
    count = 0
    for rrs in rr_set:
        for index in Sk:
            if index in rrs.keys():
                count += 1
    print("return selection")
    return list(Sk), count / r_set_length


def get_RRs():
    network = graph
    source = int(random.random() * node_num)
    RR_set, RR_set0 = {}, []
    # for val in network.values():
    for val in network:
        if val == 0: continue
        for key in val.child_list:
            key_node = graph[key]
            pro = key_node.threshold
            random_value = random.random()
            if key_node.active is False:
                if pro < random_value:
                    key_node.active = True
                    RR_set0.append(val.index)
    for point in RR_set0:
        visited = [False for _ in range(1, node_num + 1)]
        queue = [point]
        while len(queue) != 0:
            if queue[0] != source:
                visited[queue[0] - 1] = True
                temp = queue[0]
                del (queue[0])
                for key in graph[temp].child_list:
                    if visited[key - 1] is False:
                        queue.append(key)
            else:
                RR_set[point] = point
                break
    # print("return RR")
    return RR_set


def sampling(epsilon, l):
    global graph, seed_set_size, worker
    R = []
    LB = 1
    epsilon_p = epsilon * math.sqrt(2)
    alpha = math.sqrt(l * math.log(node_num) + math.log(2))
    beta = math.sqrt((1 - 1 / math.e) * (logcnk(node_num, seed_set_size) + l * math.log(node_num) + math.log(2)))

    for i in range(1, int(math.log2(node_num - 1)) + 1):
        x = node_num / (math.pow(2, i))
        lambda_p = ((2 + 2 * epsilon_p / 3) * (logcnk(node_num, seed_set_size) + l * math.log(node_num) + math.log(
            math.log2(node_num))) * node_num) / pow(epsilon_p, 2)
        beta = lambda_p / x / 100
        while len(R) <= beta:
            result_RR = get_RRs()
            if len(result_RR) > 0:
                R.append(get_RRs())
        si, FR = node_selection(rr_set=R, k=seed_set_size)
        if node_num * FR >= (1 + epsilon_p) * x:
            LB = node_num * FR / (1 + epsilon_p)
            break
    lambda_star = 2 * node_num * pow(((1 - 1 / math.e) * alpha + beta), 2) * pow(epsilon, -2)
    theta = lambda_star / LB
    while len(R) <= theta:
        R.append(get_RRs())
    print("return sample")
    return R


def IMM(k: int, l):
    l = l * (1 + math.log(2) / math.log(node_num))
    R_sampling_set = sampling(epsilon, l)
    S_star, FR = node_selection(R_sampling_set, k)
    return S_star


def logcnk(n, k):
    res = 0
    up = 1
    down = 1
    for i in range(n - k + 1, n + 1):
        up = up * i
    for j in range(1, k + 1):
        down = down * j
    res = up / down
    return math.log(res)


def ise_IC(activate_seed: list, run_round: int):
    activate_counter = len(activate_seed)
    return_activity_node_list = list()
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
                        return_activity_node_list.append(current_node.child_list[child_node_index])
        activate_counter += len(next_activate_seed)
        activate_seed = next_activate_seed
    # return float(activate_counter)
    return return_activity_node_list


def ise_LT(activate_seed: list, run_round: int):
    for node in graph:
        if node.threshold == 0:
            activate_seed.append(node)
    activate_counter = len(activate_seed)
    return_activity_node_list = list()
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
                    return_activity_node_list.append(current_node.child_list[child_node_index])
        activate_counter += len(next_activate_seed)
        activate_seed = next_activate_seed
    # return float(activate_counter)
    return return_activity_node_list


def refresh_activate_seed(activate_seed: list, run_round: int):
    for activate_index in activate_seed:
        graph[activate_index.index].iteration = run_round
    return graph


def initialize_LT():
    for node in graph:
        node.threshold = np.random.uniform(0, 1)
    return graph


def go(activate_seed: list, model: str, time_limit: int):
    sum = 0
    N = 1000000
    # N = 100
    start_time = time.time()
    counter = 0
    if model == "IC":
        for run_counter in range(N):
            np.random.seed(run_counter)
            graph = refresh_activate_seed(activate_seed=activate_seed, run_round=run_counter)
            # sum += ise_IC(activate_seed=activate_seed, run_round=run_counter)
            return_list = ise_IC(activate_seed=activate_seed, run_round=run_counter)
            current_time = time.time()
            counter = run_counter
            if current_time - start_time + 10 > time_limit:
                break
    else:
        # LT model
        for run_counter in range(N):
            np.random.seed(run_counter)
            graph = initialize_LT()
            graph = refresh_activate_seed(activate_seed=activate_seed, run_round=run_counter)
            # sum += ise_LT(activate_seed=activate_seed, run_round=run_counter)
            return_list = ise_LT(activate_seed=activate_seed, run_round=run_counter)
            current_time = time.time()
            counter = run_counter
            if current_time - start_time + 10 > time_limit:
                break
    # print("+++++++++++++++++")
    # print("total is ", sum/counter)
    # print("+++++++++++++++++")
    return return_list


if __name__ == '__main__':
    '''
    从命令行读参数示例
    '''
    # print("从命令行读参数示例")
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--file_name', type=str, default='network.txt')
    parser.add_argument('-k', '--seed_set_size', type=int, default=4)
    parser.add_argument('-m', '--model', type=str, default='IC')
    # parser.add_argument('-t', '--time_limit', type=int, default=60)
    parser.add_argument('-t', '--time_limit', type=int, default=10)

    args = parser.parse_args()
    file_name = args.file_name
    seed_set_size = args.seed_set_size
    # global model
    model = args.model
    time_limit = args.time_limit

    with open(file_name, "r") as reader:
        file_network = reader.readlines()
    network_info = file_network[0].split(' ')
    # global graph
    graph = []
    global node_num
    node_num = int(network_info[0]) + 1
    global edge_num
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

    '''
    多进程示例
    '''
    # print("多进程示例")
    # np.random.seed(0)
    # pool = mp.Pool(core)
    # worker = []
    epsilon = 0.5
    l = 1

    seeds = IMM(epsilon, l)
    for seed in seeds:
        print(seed + 1)

    '''
    程序结束后强制退出，跳过垃圾回收时间, 如果没有这个操作会额外需要几秒程序才能完全退出
    '''
    sys.stdout.flush()
