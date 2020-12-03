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

def node_selection(mathcal_R, k):
    S_star_k = set()
    for i in range(1,)

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


def get_rr_set(node_index: int):
    rr_set = set()
    rr_set.add(node_index)
    return rr_set


def sampling(graph: list, k: int, epsilon: float, mathcal_l: float):
    mathcal_R = set()
    LB = 1
    epsilon_prime = math.sqrt(2) * epsilon
    for i in range(1, int(math.log2(node_num - 1)) + 1):
        x = node_num / (math.pow(2, i))
        lambda_prime = get_lambda_prime(epsilon_prime, k, mathcal_l)
        theta_i = lambda_prime / x
        while len(mathcal_R) <= theta_i:
            select_node_index = random.randint(1, node_num)
            rr_set = get_rr_set(select_node_index)
            mathcal_R.add(rr_set)
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
    model = args.model
    time_limit = args.time_limit

    with open(file_name, "r") as reader:
        file_network = reader.readlines()
    network_info = file_network[0].split(' ')

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

    epsilon = 0.5
    mathcal_l = 1

    seeds = IMM(epsilon, mathcal_l)
    for seed in seeds:
        print(seed)

    '''
    程序结束后强制退出，跳过垃圾回收时间, 如果没有这个操作会额外需要几秒程序才能完全退出
    '''
    sys.stdout.flush()
