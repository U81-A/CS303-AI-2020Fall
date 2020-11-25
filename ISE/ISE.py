# -*- coding: utf-8 -*-
# written by mark zeng 2018-11-14
# modified by Yao Zhao 2019-10-30
# re-modified by Yiming Chen 2020-11-04

import multiprocessing as mp
import time
import sys
import argparse
import os
import numpy as np

core = 8


class Node(object):
    def __init__(self, index: int):
        self.index = index
        self.iteration = -1
        self.child_list = []
        self.child_weight = []
        # self.father_node = None
        self.threshold = 0


def sum_and_product(x, y):
    '''
    计算两个数的和与积
    '''
    while True:
        x = x + y
    return x + y, x * y


def ise_IC(graph: list, activate_seed: list, run_round: int):
    activate_counter = len(activate_seed)
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
        activate_counter += len(next_activate_seed)
        activate_seed = next_activate_seed
    return float(activate_counter)


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


if __name__ == '__main__':
    '''
    从命令行读参数示例
    '''
    # print("从命令行读参数示例")
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--file_name', type=str, default='network.txt')
    parser.add_argument('-s', '--seed', type=str, default='network_seeds.txt')
    parser.add_argument('-m', '--model', type=str, default='IC')
    # parser.add_argument('-t', '--time_limit', type=int, default=6)
    parser.add_argument('-t', '--time_limit', type=int, default=60)

    args = parser.parse_args()
    file_name = args.file_name
    seed = args.seed
    model = args.model
    time_limit = args.time_limit

    # print(file_name, seed, model, time_limit)

    # read the files
    with open(file_name, "r") as reader:
        file_network = reader.readlines()
    network_info = file_network[0].split(' ')
    graph = []
    for node_counter in range(int(network_info[0]) + 1):
        graph.append(Node(node_counter))
    for edge_counter in range(int(network_info[1].replace("\n", ""))):
        edge_info = file_network[edge_counter + 1].split()
        node_father = graph[int(edge_info[0])]
        node_child = graph[int(edge_info[1])]
        node_father.child_list.append(int(edge_info[1]))
        node_father.child_weight.append(float(edge_info[2].replace("\n", "")))
        # node_child.father_node = node_father

    with open(seed, "r") as reader:
        file_seed = reader.readlines()
    activate_seed = []
    for line in file_seed:
        # graph[int(line.replace("\n", ""))].iteration = 0
        activate_seed.append(graph[int(line.replace("\n", ""))])
    '''
    多进程示例
    '''
    # print("多进程示例")
    np.random.seed(0)
    pool = mp.Pool(core)
    result = []

    # def go(graph: list, activate_seed: list, model: str, time_limit: int):
    for i in range(core):
        result.append(pool.apply_async(go, args=(graph, activate_seed, model, time_limit)))
    pool.close()
    pool.join()

    total_score = 0.0
    for score in result:
        print(score.get())
        total_score += score.get()
    print(float(total_score / 8))

    '''
    程序结束后强制退出，跳过垃圾回收时间, 如果没有这个操作会额外需要几秒程序才能完全退出
    '''
    sys.stdout.flush()
