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
time_limit = 10
graph = []


class Worker(mp.Process):
    def __init__(self, inQ, outQ, node_num):
        super(Worker, self).__init__(target=self.start)
        self.inQ = inQ
        self.outQ = outQ
        self.R = []
        self.count = 0
        self.node_num = node_num

    def run(self):
        global model
        while True:
            theta = self.inQ.get()
            # print(theta)
            while self.count < theta:
                v = random.randint(1, self.node_num)
                # print(v)
                rr = go(activate_seed=self.R, model=model, time_limit=time_limit)
                for seed_index in rr:
                    self.R.append(rr)
                self.count += 1
            self.count = 0
            self.outQ.put(self.R)
            self.R = []


def create_worker(num):
    """
        create processes
        :param num: process number
        :param task_num: the number of tasks assigned to each worker
    """
    global worker
    for i in range(num):
        # print(i)
        worker.append(Worker(mp.Queue(), mp.Queue(), node_num))
        worker[i].start()


def finish_worker():
    """
    关闭所有子进程
    :return:
    """
    for w in worker:
        w.terminate()


class Node(object):
    def __init__(self, index: int):
        self.index = index
        self.iteration = -1
        self.child_list = []
        self.child_weight = []
        self.father_node = None
        self.threshold = 0
        self.in_degree = 0
        self.out_degree = 0


def node_selection(rr_set: list, k: int):
    Sk = set()
    rr_degree = []
    for i in range(node_num + 1):
        rr_degree.append(0)
    node_rr_set = dict()
    matched_count = 0
    for i in range(0, len(rr_set)):
        rr = rr_set[i]
        for rr_node in rr:
            rr_degree[rr_node] += 1
            if rr_node not in node_rr_set:
                node_rr_set[rr_node] = list()
            node_rr_set[rr_node].append(i)
    for i in range(k):
        max_point = rr_degree.index(max(rr_degree))
        Sk.add(max_point)
        matched_count += len(node_rr_set[max_point])
        index_set = []
        for node_rr in node_rr_set[max_point]:
            index_set.append(node_rr)
        for jj in index_set:
            rr = rr_set[jj]
            for rr_node in rr:
                rr_degree[rr_node] -= 1
                node_rr_set[rr_node].remove(jj)
    return Sk, matched_count / len(rr_set)


def sampling(epsilon, l):
    global graph, seed_set_size, worker
    R = []
    LB = 1
    epsilon_p = epsilon * math.sqrt(2)
    worker_num = 2
    print(node_num)
    create_worker(worker_num)

    for i in range(1, int(math.log2(node_num - 1)) + 1):
        # s = time.time()
        x = node_num / (math.pow(2, i))
        lambda_p = ((2 + 2 * epsilon_p / 3) * (logcnk(node_num, seed_set_size) + l * math.log(node_num) + math.log(
            math.log2(node_num))) * node_num) / pow(
            epsilon_p, 2)
        theta = lambda_p / x

        for ii in range(worker_num):
            worker[ii].inQ.put((theta - len(R)) / worker_num)
        for w in worker:
            R_list = w.outQ.get()
            R += R_list
        end = time.time()
        start = time.time()
        Si, f = node_selection(R, seed_set_size)
        print(f)
        end = time.time()
        print('node selection time', time.time() - start)

        if node_num * f >= (1 + epsilon_p) * x:
            LB = node_num * f / (1 + epsilon_p)
            break

    alpha = math.sqrt(l * math.log(node_num) + math.log(2))
    beta = math.sqrt((1 - 1 / math.e) * (logcnk(node_num, seed_set_size) + l * math.log(node_num) + math.log(2)))
    lambda_aster = 2 * node_num * pow(((1 - 1 / math.e) * alpha + beta), 2) * pow(epsilon, -2)
    theta = lambda_aster / LB
    length_r = len(R)
    diff = theta - length_r
    # print(diff)
    _start = time.time()

    if diff > 0:
        # print('j')
        for ii in range(worker_num):
            worker[ii].inQ.put(diff / worker_num)
        for w in worker:
            R_list = w.outQ.get()
            R += R_list
    _end = time.time()
    # print(_end - _start)
    finish_worker()
    return R


def IMM(k: int, l):
    l = l * (1 + math.log(2) / math.log(node_num))
    sampling_set = sampling(epsilon, l)
    Sk, z = node_selection(sampling_set, k)
    return Sk


def logcnk(n, k):
    res = 0
    for i in range(n - k + 1, n + 1):
        res += math.log(i)
    for i in range(1, k + 1):
        res -= math.log(i)
    return res


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
    parser.add_argument('-k', '--seed_set_size', type=int, default=1)
    parser.add_argument('-m', '--model', type=str, default='IC')
    # parser.add_argument('-t', '--time_limit', type=int, default=60)
    parser.add_argument('-t', '--time_limit', type=int, default=10)

    # global model, node_num, edge_num, time_limit, seed_set_size, graph, seed_set

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
    np.random.seed(0)
    pool = mp.Pool(core)
    worker = []
    epsilon = 0.5
    l = 1

    # for i in range(core):
    #     result.append(pool.apply_async(go, args=(graph, seed_set_size, model, time_limit)))
    # pool.close()
    # pool.join()

    # total_score = 0.0
    # for score in result:
    #     print(score.get())
    #     total_score += score.get()
    # print(float(total_score / 8))

    seeds = IMM(epsilon, l)
    for seed in seeds:
        print(seed)

    '''
    程序结束后强制退出，跳过垃圾回收时间, 如果没有这个操作会额外需要几秒程序才能完全退出
    '''
    sys.stdout.flush()
