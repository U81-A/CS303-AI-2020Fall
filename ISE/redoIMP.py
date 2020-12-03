import multiprocessing as mp
import time
import sys
import argparse
import os
import random
import numpy as np
import math


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
    node_num = int(network_info[0]) + 1
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
    l = 1

    seeds = IMM(epsilon, l)
    for seed in seeds:
        print(seed + 1)

    '''
    程序结束后强制退出，跳过垃圾回收时间, 如果没有这个操作会额外需要几秒程序才能完全退出
    '''
    sys.stdout.flush()
