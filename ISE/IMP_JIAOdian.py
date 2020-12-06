import argparse
import random
import math


class Point:
    def __init__(self, key):
        self.id = key
        self.active = False
        self.visited = False
        self.neighbors = {}  # key是point value是激活概率

    def addNeighbor(self, nbr, val):
        self.neighbors[nbr] = val

    def setActive(self):
        self.active = True

    def setVisited(self):
        self.visited = True


def get_RRs(network, point_num):
    source = int(random.random() * point_num)
    RR_set, RR_set0 = {}, []
    for val in network.values():
        for key in val.neighbors.keys():
            pro = val.neighbors.get(key)
            if key.active is False:
                ran = random.random()
                if pro < ran:
                    key.setActive()
                    RR_set0.append(val)
    for point in RR_set0:
        visited = [False for _ in range(point_num)]
        queue = [point]
        while len(queue) != 0:
            if queue[0].id != source:
                visited[queue[0].id - 1] = True
                temp = queue[0]
                del (queue[0])
                for key in temp.neighbors.keys():
                    if visited[key.id - 1] is False:
                        queue.append(key)
            else:
                RR_set[point.id] = point
                break
    return RR_set


def IMM(g, k, e, l, n):
    l = l * (1 + math.log(2) / math.log(n))
    R = Sampling(g, k, e, l, n)
    S_star, FR = NodeSelection(R, k, n)
    return S_star


def Sampling(g, k, e, l, n):
    R = []
    lb = 1
    e0 = math.sqrt(2) * e
    alpha = math.sqrt(l * math.log(n) + math.log(2))
    beta = math.sqrt((1 - 1 / math.e) * (logNK(n, k) + l*math.log(n) + math.log(2)))
    # print(beta)
    for i in range(1, int(math.log2(n - 1))):
        x = n / (2 ** i)
        o = getlamda(e0, k, n, l) / x
        while len(R) <= o:
            R.append(get_RRs(g, n))
        si, FR = NodeSelection(R, k, n)
        if n * FR >= (1 + e0) * x:
            lb = (n * FR)/(1 + e0)
            break
    lambda_star = 2 * n * math.pow(((1 - 1/math.e)*alpha+beta), 2) * math.pow(e, -2)
    theta = lambda_star / lb
    while len(R) <= theta:
        R.append(get_RRs(g, n))
    print(R)
    return R


def NodeSelection(R, k, n):
    s = set()
    r_length = 0
    for i in R:
        r_length += len(i)
    out_degree = [0 for _ in range(n)]
    for a in range(len(R)):
        temp_set = R[a]
        for key in temp_set.keys():
            out_degree[key-1] += len(temp_set.get(key).neighbors)
    # print(out_degree)
    for b in range(k):
        max_id = out_degree.index(max(out_degree))
        s.add(max_id)
        out_degree[max_id] = 0
    count = 0
    for rrs in R:
        for index in s:
            if index in rrs.keys():
                count += 1

    return list(s), count / r_length


def getlamda(e0, k, n, l):
    temp = ((2 + 2 / 3 * e0) * (logNK(n, k) + l * math.log(n) + math.log(math.log2(n))) * n) / (e0 ** 2)
    return temp


def logNK(n, k):
    up = 1
    for i in range(n - k + 1, n + 1):
        up = up * i
    down = 1
    for j in range(1, k + 1):
        down = down * j
    return math.log(up / down)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--file_name', type=str, default='network.txt')
    parser.add_argument('-k', '--seed_num', type=int, default=4)
    parser.add_argument('-m', '--model', type=str, default='IC')
    parser.add_argument('-t', '--time_limit', type=int, default=60)
    args = parser.parse_args()
    net = open(args.file_name, 'r')  # 网络文件名
    seed_num = args.seed_num
    model = args.model  # 所用模型
    time_limit = args.time_limit  # 时间要求

    # 处理节点
    file_data = net.read().split('\n')
    net.close()  # 关闭网络文件连接
    point_num = int(file_data[0].split()[0])  # point数
    net_work = {}  # 网络图
    edge_num = int(file_data[0].split()[1])  # edge数

    # 建图
    net_list = []
    for i in range(point_num):
        net_list.append(Point(i + 1))
    for i in range(1, edge_num + 1):
        edge = file_data[i].split()
        begin = int(edge[0]) - 1
        end = int(edge[1]) - 1
        prob = float(edge[2])
        if begin in net_work.keys():
            net_work.get(begin).addNeighbor(net_list[end], prob)
        else:
            net_list[begin].addNeighbor(net_list[end], prob)
            net_work[begin] = net_list[begin]
    result = IMM(net_work, seed_num,  2, 1, point_num)
    print("----------------")
    for v in result:
        print(v+1)
    print("end")