class TreeStructure(object):
    def __init__(self, value):
        self.value = value
        self.left_child = None
        self.right_child = None


if __name__ == '__main__':
    print("hello world")
    test_tree = TreeStructure(1)
    test_child = TreeStructure(2)
    test_tree.left_child = test_child
    print(test_tree.left_child.value)
