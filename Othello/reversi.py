import numpy as np
import random
import time

COLOR_BLACK = -1
COLOR_WHITE = 1
COLOR_NONE = 0
random.seed(0)


# don't change the class name
class AI(object):
    direction = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
    value = [[250, -50, 8, 6], [-50, -200, -4, -3], [8, -4, 7, 4], [6, -3, 4, 0]]
    reverse_value = [[-250, 48, -8, 6], [48, 200, -16, 3], [-8, -16, 4, 4], [6, 3, 4, 0]]
    max_int = 2147483647
    min_int = -2147483648

    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        # You are white or black
        self.color = color
        # the max time you should use, your algorithm's run time must not exceed the time limit.
        self.time_out = time_out
        # You need add your decision into your candidate_list.
        # System will get the end of your candidate_list as your decision .
        self.candidate_list = []

    # get the chessboard reversed according to the playing color_role
    def reverse_by_role(self, origin_chessboard, color_role):
        chessboard_reverse_by_role = origin_chessboard.copy()
        for row in range(8):
            for column in range(8):
                if chessboard_reverse_by_role[row][column] == ~color_role + 1:
                    chessboard_reverse_by_role[row][column] = -1
                elif chessboard_reverse_by_role[row][column] == color_role:
                    chessboard_reverse_by_role[row][column] = 1
                else:
                    chessboard_reverse_by_role[row][column] = 0
        return chessboard_reverse_by_role

    class MCTSnode(object):
        def __init__(self, current_color: int, origin_color: int, origin_chessboard, parent_node, T_from_parent):
            # the playing color, can use it to reverse the chessboard
            self.current_color = current_color
            # the origin color, to decide the value of position is positive or negative
            self.origin_color = origin_color
            # the origin_chessboard without put a chess at certain position
            self.origin_chessboard = origin_chessboard
            # need to roll back and use its parent_node
            self.parent_node = parent_node
            # after put the chess, what is legal for the next step for another player
            self.child_legal_list = []
            # contains the node of its children and filled by def get_child_legal_list
            self.children_state_list = []
            self.value_list = []
            # self.printer()
            # W: number of wins after the i-th move
            self.W = 0
            # N: number of simulations after the i-th move
            self.N = 0
            # C: exploration parameter, can chose it as 2
            self.C = 0
            # T: total number of simulations for the parent node
            self.T = T_from_parent

        def get_N(self):
            if self.parent_node is None:
                return 0
            else:
                return self.parent_node.N

        def selection(self):
            None

        def expansion(self):
            None

        def simulation(self):
            None

        def back_propagation(self):
            None

    # the NODE of chessboard, only used when searching a tree
    # its for Minimax
    class ChessboardNode(object):
        priority_position = [(3, 3), (3, 4), (4, 3), (4, 4)]

        def __init__(self, current_color: int, origin_color: int, chess_position, origin_chessboard, deep, progress):
            # hierarchy is for row-back and it's get from its child's hierarchy
            self.hierarchy_evaluate = 0
            # use for search
            self.deep = deep
            # get progress
            self.progress = progress
            # the playing color, can use it to reverse the chessboard
            self.current_color = current_color
            # the origin color, to decide the value of position is positive or negative
            self.origin_color = origin_color
            # is the position going to put in this (child) node
            self.chess_position = chess_position
            # get the value cuz by reverse the chess
            self.value_reverse_chess_by_chess = 0
            # state_value is the position's value depends on current playing color
            # self.chess_state_value = self.get_chess_state_value_base_origin_color(current_color=current_color,origin_color=origin_color)
            # update the state_value by dynamic advance after after_chessboard
            # self.chess_state_value = self.center_advance_get_chess_state_value()
            # update it by counting the stable part
            # self.chess_state_value = self.stable_advance_get_chess_state_value()
            # the origin_chessboard without put a chess at certain position
            self.origin_chessboard = origin_chessboard
            # the chessboard after put the chess this child node hold and work by reverse_chess_by_chess
            self.after_chessboard = self.reverse_chess_by_chess(origin_chessboard)
            # get the state_value according to 3 different def
            self.chess_state_value = self.state_value_calculate(current_color=current_color, origin_color=origin_color)
            # after put the chess, what is legal for the next step for another player
            self.child_legal_list = []
            # contains the node of its children and filled by def get_child_legal_list
            self.children_state_list = []
            self.child_legal_list = self.get_child_legal_list(after_chessboard=self.after_chessboard)
            self.value_list = []
            # self.printer()

        def state_value_calculate(self, current_color, origin_color):
            parameter = self.progress / 64
            base_parameter = 0.5 * parameter + 0.1
            if self.progress > 45:
                base_parameter += self.progress / 10
            base_value = self.value_reverse_chess_by_chess
            center_parameter = -0.5 * parameter * parameter + 1
            center_value = self.center_advance_get_chess_state_value()
            stable_parameter = 1.6
            stable_value = self.stable_advance_get_chess_state_value()
            bonus_parameter = 1.2
            bonus_value = self.bonus_corner_advance_get_chess_state_value()
            return_value = 0
            return_value += base_parameter * base_value
            return_value += center_parameter * center_value
            return_value += stable_parameter * stable_value
            return_value += bonus_parameter * bonus_value
            self.chess_state_value = return_value
            # self.printer()
            # if self.origin_color == self.current_color:
            #     print("now it's my turn")
            # else:
            #     print("it's NOT my turn")
            # print("base value is ", base_value)
            # print("center value is ", center_value)
            # print("stable value is ", stable_value)
            # print("bonus value is ", bonus_value)
            # print("========================================")
            return return_value

        def printer(self):
            print("|----------------------------------------|")
            print("hierarchy evaluate is: ", self.hierarchy_evaluate)
            print("current color is:", self.current_color, " and origin color is:", self.origin_color)
            print(self.origin_chessboard)
            print("going to position ", self.chess_position)
            print(self.after_chessboard)
            print("state value now is ", self.chess_state_value)
            print("current deep is ", self.deep)
            print("|----------------------------------------|")

        # the node of chessboard contain the position particularly now
        # use this def to find what is the value in this position depends on color
        def get_chess_state_value_base_origin_color(self, current_color, origin_color):
            return_value = 0
            if current_color == origin_color:
                return_value = AI.value[int(min(self.chess_position[0], 7 - self.chess_position[0]))][
                    int(min(self.chess_position[1], 7 - self.chess_position[1]))]
            else:
                return_value = AI.reverse_value[int(min(self.chess_position[0], 7 - self.chess_position[0]))][
                    int(min(self.chess_position[1], 7 - self.chess_position[1]))]
            return return_value

        # get the after_chessboard which means the player already put down the chess
        # also calculate the dynamic state_value
        # dynamic state_value means count all value including the chess being reversed
        def reverse_chess_by_chess(self, origin_chessboard):
            after_reverse_chess_chessboard = origin_chessboard.copy()
            legal_direction_list = AI.legal(self, origin_chessboard=origin_chessboard, color_role=self.current_color,
                                            position=self.chess_position)
            for index_direction in range(8):
                if legal_direction_list[index_direction + 1] > 0:
                    for step in range(int(legal_direction_list[index_direction + 1])):
                        row_index = self.chess_position[0] + AI.direction[index_direction][0] * (step + 1)
                        column_index = self.chess_position[1] + AI.direction[index_direction][1] * (step + 1)
                        after_reverse_chess_chessboard[row_index][column_index] = self.current_color
                        if self.current_color == self.origin_color:
                            self.value_reverse_chess_by_chess += AI.value[int(min(row_index, 7 - row_index))][
                                int(min(column_index, 7 - column_index))]
                        else:
                            self.value_reverse_chess_by_chess += AI.reverse_value[int(min(row_index, 7 - row_index))][
                                int(min(column_index, 7 - column_index))]
            after_reverse_chess_chessboard[self.chess_position[0]][self.chess_position[1]] = self.current_color
            if self.current_color == self.origin_color:
                self.value_reverse_chess_by_chess += \
                    AI.value[int(min(self.chess_position[0], 7 - self.chess_position[0]))][
                        int(min(self.chess_position[1], 7 - self.chess_position[1]))]
            else:
                self.value_reverse_chess_by_chess += \
                    AI.reverse_value[int(min(self.chess_position[0], 7 - self.chess_position[0]))][
                        int(min(self.chess_position[1], 7 - self.chess_position[1]))]
            return after_reverse_chess_chessboard

        # focus on centre four places
        def center_advance_get_chess_state_value(self):
            return_value = 0
            for priority_index in range(len(self.priority_position)):
                if self.origin_chessboard[self.priority_position[priority_index][0]][
                    self.priority_position[priority_index][1]] != \
                        self.after_chessboard[self.priority_position[priority_index][0]][
                            self.priority_position[priority_index][1]]:
                    if self.origin_chessboard[self.priority_position[priority_index][0]][
                        self.priority_position[priority_index][1]] != self.origin_color:
                        return_value += 25
                    else:
                        return_value -= 25
            return return_value

        # return the bonus value (optional)
        def bonus_corner_advance_get_chess_state_value(self):
            corner = [(0, 0), (0, 7), (7, 0), (7, 7)]
            pre_corner = [(1, 1), (1, 6), (6, 1), (6, 6), (1, 0), (0, 1), (0, 6), (1, 7), (6, 0), (7, 1), (7, 6),
                          (6, 7)]
            return_value = 0
            for i in range(len(corner)):
                if self.origin_chessboard[corner[i][0]][corner[i][1]] == 0:
                    if self.after_chessboard[corner[i][0]][corner[i][1]] == self.origin_color:
                        return_value += 100
                    elif self.after_chessboard[corner[i][0]][corner[i][1]] == ~self.origin_color + 1:
                        return_value -= 100
            for i in range(len(pre_corner)):
                if self.origin_chessboard[pre_corner[i][0]][pre_corner[i][1]] == 0:
                    if self.after_chessboard[pre_corner[i][0]][pre_corner[i][1]] == self.origin_color:
                        return_value -= 120
                    elif self.after_chessboard[pre_corner[i][0]][pre_corner[i][1]] == ~self.origin_color + 1:
                        return_value += 120
            if self.origin_chessboard[0][0] == ~self.current_color + 1:
                if self.origin_chessboard[0][7] == ~self.current_color + 1:
                    origin_tag = True
                    after_tage = True
                    for i in range(6):
                        if self.origin_chessboard[0][1 + i] != self.origin_color:
                            origin_tag = False
                        if self.after_chessboard[0][1 + i] != self.origin_color:
                            after_tage = False
                        if origin_tag is False and after_tage is False:
                            break
                    if origin_tag is False and after_tage is True:
                        return_value += 80
                if self.origin_chessboard[7][0] == ~self.current_color + 1:
                    origin_tag = True
                    after_tage = True
                    for i in range(6):
                        if self.origin_chessboard[1 + i][0] != self.origin_color:
                            origin_tag = False
                        if self.after_chessboard[1 + i][0] != self.origin_color:
                            after_tage = False
                        if origin_tag is False and after_tage is False:
                            break
                    if origin_tag is False and after_tage is True:
                        return_value += 80
            if self.origin_chessboard[7][7] == ~self.current_color + 1:
                if self.origin_chessboard[7][0] == ~self.current_color + 1:
                    origin_tag = True
                    after_tage = True
                    for i in range(6):
                        if self.origin_chessboard[7][6 - i] != self.origin_color:
                            origin_tag = False
                        if self.after_chessboard[7][6 - i] != self.origin_color:
                            after_tage = False
                        if origin_tag is False and after_tage is False:
                            break
                    if origin_tag is False and after_tage is True:
                        return_value += 80
                if self.origin_chessboard[0][7] == ~self.current_color + 1:
                    origin_tag = True
                    after_tage = True
                    for i in range(6):
                        if self.origin_chessboard[6 - i][7] != self.origin_color:
                            origin_tag = False
                        if self.after_chessboard[6 - i][7] != self.origin_color:
                            after_tage = False
                        if origin_tag is False and after_tage is False:
                            break
                    if origin_tag is False and after_tage is True:
                        return_value += 80
            return return_value

        # return the stable chess evaluation
        def stable_advance_get_chess_state_value(self):
            return_value = 0
            origin_state_evaluate = self.get_stable_chess_counter(self.origin_chessboard)
            after_state_evaluate = self.get_stable_chess_counter(self.after_chessboard)
            return_value = after_state_evaluate - origin_state_evaluate
            return return_value

        # count the stable chess separately
        def get_stable_chess_counter(self, chessboard):
            return_value = 0
            if chessboard[0][0] == self.origin_color:
                # horizon
                # left_up_horizon shows the index of horizon
                left_up_horizon = 0
                chess_position_row = 0
                chess_position_column = 1
                while chessboard[chess_position_row][chess_position_column] == self.origin_color:
                    return_value += 10
                    left_up_horizon += 1
                    chess_position_column += 1
                    if chess_position_column > 7:
                        break
                chess_position_row = 1
                chess_position_column = 0
                serial_counter = left_up_horizon
                for storey_counter in range(left_up_horizon):
                    chess_position_row = storey_counter + 1
                    if serial_counter < 1:
                        break
                    for serial in range(serial_counter - 1):
                        if chessboard[chess_position_row][serial] == self.origin_color:
                            return_value += 5
                        else:
                            serial_counter = serial - 1
                            break
                # vertical
                left_up_vertical = 0
                chess_position_row = 1
                chess_position_column = 0
                while self.origin_chessboard[chess_position_row][chess_position_column] == self.origin_color:
                    return_value += 10
                    left_up_horizon += 1
                    chess_position_row += 1
                    if chess_position_row > 7:
                        break
                chess_position_column = 1
                chess_position_row = 0
                serial_counter = left_up_vertical
                for storey_counter in range(left_up_vertical):
                    chess_position_column = storey_counter + 1
                    if serial_counter < 1:
                        break
                    for serial in range(serial_counter - 1):
                        if chessboard[serial][chess_position_column] == self.origin_color:
                            return_value += 5
                        else:
                            serial_counter = serial - 1
                            break

            elif chessboard[0][0] == ~self.origin_color + 1:
                # horizon
                # left_up_horizon shows the index of horizon
                left_up_horizon = 0
                chess_position_row = 0
                chess_position_column = 1
                while chessboard[chess_position_row][chess_position_column] == self.origin_color:
                    return_value -= 10
                    left_up_horizon += 1
                    chess_position_column += 1
                    if chess_position_column > 7:
                        break
                chess_position_row = 1
                chess_position_column = 0
                serial_counter = left_up_horizon
                for storey_counter in range(left_up_horizon):
                    chess_position_row = storey_counter + 1
                    if serial_counter < 1:
                        break
                    for serial in range(serial_counter - 1):
                        if chessboard[chess_position_row][serial] == self.origin_color:
                            return_value -= 5
                        else:
                            serial_counter = serial - 1
                            break
                # vertical
                left_up_vertical = 0
                chess_position_row = 1
                chess_position_column = 0
                while self.origin_chessboard[chess_position_row][chess_position_column] == self.origin_color:
                    return_value -= 10
                    left_up_horizon += 1
                    chess_position_row += 1
                    if chess_position_row > 7:
                        break
                chess_position_column = 1
                chess_position_row = 0
                serial_counter = left_up_vertical
                for storey_counter in range(left_up_vertical):
                    chess_position_column = storey_counter + 1
                    if serial_counter < 1:
                        break
                    for serial in range(serial_counter - 1):
                        if chessboard[serial][chess_position_column] == self.origin_color:
                            return_value -= 5
                        else:
                            serial_counter = serial - 1
                            break

            if chessboard[0][7] == self.origin_color:
                # horizon
                right_up_horizon = 0
                chess_position_row = 0
                chess_position_column = 6
                while self.origin_chessboard[chess_position_row][chess_position_column] == self.origin_color:
                    return_value += 10
                    right_up_horizon += 1
                    chess_position_column -= 1
                    if chess_position_column < 0:
                        break
                chess_position_row = 1
                chess_position_column = 7
                serial_counter = right_up_horizon
                for storey_counter in range(right_up_horizon):
                    chess_position_row = 7 - storey_counter
                    if serial_counter < 1:
                        break
                    for serial in range(serial_counter - 1):
                        if chessboard[chess_position_row][7 - serial] == self.origin_color:
                            return_value += 5
                        else:
                            serial_counter = serial - 1
                            break
                # vertical
                right_up_vertical = 0
                chess_position_row = 1
                chess_position_column = 7
                while self.origin_chessboard[chess_position_row][chess_position_column] == self.origin_color:
                    return_value += 10
                    right_up_vertical += 1
                    chess_position_row += 1
                    if chess_position_row > 7:
                        break
                chess_position_column = 7
                chess_position_row = 0
                serial_counter = right_up_vertical
                for storey_counter in range(right_up_vertical):
                    chess_position_column = 7 - storey_counter
                    if serial_counter < 1:
                        break
                    for serial in range(serial_counter - 1):
                        if chessboard[serial][chess_position_column] == self.origin_color:
                            return_value += 5
                        else:
                            serial_counter = serial - 1
                            break

            elif chessboard[0][7] == ~self.origin_color + 1:
                # horizon
                right_up_horizon = 0
                chess_position_row = 0
                chess_position_column = 6
                while self.origin_chessboard[chess_position_row][chess_position_column] == self.origin_color:
                    return_value -= 10
                    right_up_horizon += 1
                    chess_position_column -= 1
                    if chess_position_column < 0:
                        break
                chess_position_row = 1
                chess_position_column = 7
                serial_counter = right_up_horizon
                for storey_counter in range(right_up_horizon):
                    chess_position_row = 7 - storey_counter
                    if serial_counter < 1:
                        break
                    for serial in range(serial_counter - 1):
                        if chessboard[chess_position_row][7 - serial] == self.origin_color:
                            return_value -= 10
                        else:
                            serial_counter = serial - 1
                            break
                # vertical
                right_up_vertical = 0
                chess_position_row = 1
                chess_position_column = 7
                while self.origin_chessboard[chess_position_row][chess_position_column] == self.origin_color:
                    return_value -= 5
                    right_up_vertical += 1
                    chess_position_row += 1
                    if chess_position_row > 7:
                        break
                chess_position_column = 7
                chess_position_row = 0
                serial_counter = right_up_vertical
                for storey_counter in range(right_up_vertical):
                    chess_position_column = 7 - storey_counter
                    if serial_counter < 1:
                        break
                    for serial in range(serial_counter - 1):
                        if chessboard[serial][chess_position_column] == self.origin_color:
                            return_value -= 5
                        else:
                            serial_counter = serial - 1
                            break

            if chessboard[7][0] == self.origin_color:
                # horizon
                left_down_horizon = 0
                chess_position_row = 7
                chess_position_column = 1
                while self.origin_chessboard[chess_position_row][chess_position_column] == self.origin_color:
                    return_value += 10
                    left_down_horizon += 1
                    chess_position_column += 1
                    if chess_position_column > 7:
                        break
                chess_position_row = 6
                chess_position_column = 0
                serial_counter = left_down_horizon
                for storey_counter in range(left_down_horizon):
                    chess_position_row = 6 - storey_counter
                    if serial_counter < 1:
                        break
                    for serial in range(serial_counter - 1):
                        if chessboard[chess_position_row][serial] == self.origin_color:
                            return_value += 5
                        else:
                            serial_counter = serial - 1
                            break
                # vertical
                left_down_vertical = 0
                chess_position_row = 6
                chess_position_column = 0
                while self.origin_chessboard[chess_position_row][chess_position_column] == self.origin_color:
                    return_value += 10
                    left_down_vertical += 1
                    chess_position_row -= 1
                    if chess_position_row < 0:
                        break
                chess_position_column = 1
                chess_position_row = 7
                serial_counter = left_down_vertical
                for storey_counter in range(left_down_vertical):
                    chess_position_column = storey_counter + 1
                    if serial_counter < 1:
                        break
                    for serial in range(serial_counter - 1):
                        if chessboard[7 - serial][chess_position_column] == self.origin_color:
                            return_value += 5
                        else:
                            serial_counter = serial - 1
                            break

            elif chessboard[7][0] == ~self.origin_color + 1:
                # horizon
                left_down_horizon = 0
                chess_position_row = 7
                chess_position_column = 1
                while self.origin_chessboard[chess_position_row][chess_position_column] == self.origin_color:
                    return_value -= 10
                    left_down_horizon += 1
                    chess_position_column += 1
                    if chess_position_column > 7:
                        break
                chess_position_row = 6
                chess_position_column = 0
                serial_counter = left_down_horizon
                for storey_counter in range(left_down_horizon):
                    chess_position_row = 6 - storey_counter
                    if serial_counter < 1:
                        break
                    for serial in range(serial_counter - 1):
                        if chessboard[chess_position_row][serial] == self.origin_color:
                            return_value -= 5
                        else:
                            serial_counter = serial - 1
                            break
                # vertical
                left_down_vertical = 0
                chess_position_row = 6
                chess_position_column = 0
                while self.origin_chessboard[chess_position_row][chess_position_column] == self.origin_color:
                    return_value -= 10
                    left_down_vertical += 1
                    chess_position_row -= 1
                    if chess_position_row < 0:
                        break
                chess_position_column = 1
                chess_position_row = 7
                serial_counter = left_down_vertical
                for storey_counter in range(left_down_vertical):
                    chess_position_column = storey_counter + 1
                    if serial_counter < 1:
                        break
                    for serial in range(serial_counter - 1):
                        if chessboard[7 - serial][chess_position_column] == self.origin_color:
                            return_value -= 5
                        else:
                            serial_counter = serial - 1
                            break

            if chessboard[7][7] == self.origin_color:
                # horizon
                right_down_horizon = 0
                chess_position_row = 7
                chess_position_column = 6
                while self.origin_chessboard[chess_position_row][chess_position_column] == self.origin_color:
                    return_value += 10
                    right_down_horizon += 1
                    chess_position_column -= 1
                    if chess_position_column < 0:
                        break
                chess_position_row = 6
                chess_position_column = 7
                serial_counter = right_down_horizon
                for storey_counter in range(right_down_horizon):
                    chess_position_row = 6 - right_down_horizon
                    if serial_counter < 1:
                        break
                    for serial in range(serial_counter - 1):
                        if chessboard[chess_position_row][7 - serial] == self.origin_color:
                            return_value += 5
                        else:
                            serial_counter = serial - 1
                            break
                # vertical
                right_down_vertical = 0
                chess_position_row = 6
                chess_position_column = 7
                while self.origin_chessboard[chess_position_row][chess_position_column] == self.origin_color:
                    return_value += 10
                    right_down_vertical += 1
                    chess_position_row -= 1
                    if chess_position_row < 0:
                        break
                chess_position_column = 6
                chess_position_row = 0
                serial_counter = right_down_vertical
                for storey_counter in range(right_down_vertical):
                    chess_position_column = 6 - storey_counter
                    if serial_counter < 1:
                        break
                    for serial in range(serial_counter - 1):
                        if chessboard[7 - serial][chess_position_column] == self.origin_color:
                            return_value += 5
                        else:
                            serial_counter = serial - 1
                            break

            elif chessboard[7][7] == ~self.origin_color + 1:
                # horizon
                right_down_horizon = 0
                chess_position_row = 7
                chess_position_column = 6
                while self.origin_chessboard[chess_position_row][chess_position_column] == self.origin_color:
                    return_value -= 10
                    right_down_horizon += 1
                    chess_position_column -= 1
                    if chess_position_column < 0:
                        break
                chess_position_row = 6
                chess_position_column = 7
                serial_counter = right_down_horizon
                for storey_counter in range(right_down_horizon):
                    chess_position_row = 6 - right_down_horizon
                    if serial_counter < 1:
                        break
                    for serial in range(serial_counter - 1):
                        if chessboard[chess_position_row][7 - serial] == self.origin_color:
                            return_value -= 5
                        else:
                            serial_counter = serial - 1
                            break
                # vertical
                right_down_vertical = 0
                chess_position_row = 6
                chess_position_column = 7
                while self.origin_chessboard[chess_position_row][chess_position_column] == self.origin_color:
                    return_value -= 10
                    right_down_vertical += 1
                    chess_position_row -= 1
                    if chess_position_row < 0:
                        break
                chess_position_column = 6
                chess_position_row = 0
                serial_counter = right_down_vertical
                for storey_counter in range(right_down_vertical):
                    chess_position_column = 6 - storey_counter
                    if serial_counter < 1:
                        break
                    for serial in range(serial_counter - 1):
                        if chessboard[7 - serial][chess_position_column] == self.origin_color:
                            return_value -= 5
                        else:
                            serial_counter = serial - 1
                            break

            return return_value

        # firstly find the null point then find the legal ones
        def get_child_legal_list(self, after_chessboard):
            # print(after_chessboard)
            # print(type(after_chessboard))
            children_null_point = AI.find_null_point(self, chessboard=self.after_chessboard)
            # get the right chessboard by reverse the after_chessboard depends on player
            # this is to find the legal child position by AI.reverse_chessboard_legal
            reverse_after_chessboard = AI.reverse_by_role(self, origin_chessboard=after_chessboard,
                                                          color_role=~self.current_color + 1)
            for i in range(len(children_null_point)):
                children_chess_position = children_null_point[i]
                if AI.reverse_chessboard_legal(self, reverse_chessboard=reverse_after_chessboard,
                                               position=children_chess_position)[0] and self.deep > 0:
                    self.child_legal_list.append(children_chess_position)
                    children_node = AI.ChessboardNode(current_color=~self.current_color + 1,
                                                      origin_color=self.origin_color,
                                                      chess_position=children_chess_position,
                                                      origin_chessboard=after_chessboard,
                                                      deep=self.deep - 1,
                                                      progress=self.progress + 1)
                    self.children_state_list.append(children_node)
            # legal_list = AI.legal(origin_chessboard, current_color, chess_position)
            return self.child_legal_list

        # seems nonsense
        def return_minimax_value(self):
            value = -100
            return_children_value_list = [-100, None]
            for i in range(len(self.children_value_list)):
                if self.children_value_list[i] > value:
                    return_children_value_list = [value, self.children_state_list[i]]
            return return_children_value_list

    def evaluate_similation(self, chessboard, color_role):
        score = 0
        for row in range(8):
            for column in range(8):
                if chessboard[row][column] == color_role:
                    score += 1
                if chessboard[row][column] == ~color_role + 1:
                    score -= 1
        return score

    # get the after_chessboard which means the player already put down the chess
    # also calculate the dynamic state_value
    # dynamic state_value means count all value including the chess being reversed
    def reverse_chess_by_chess_MCTS(self, origin_chessboard, legal_direction_list, current_color,
                                    chess_position):
        after_reverse_chess_chessboard = origin_chessboard.copy()
        # legal_direction_list = AI.legal(self, origin_chessboard=origin_chessboard, color_role=current_color,
        #                                 position=chess_position)
        for index_direction in range(8):
            if legal_direction_list[index_direction + 1] > 0:
                for step in range(int(legal_direction_list[index_direction + 1])):
                    row_index = chess_position[0] + AI.direction[index_direction][0] * (step + 1)
                    column_index = chess_position[1] + AI.direction[index_direction][1] * (step + 1)
                    after_reverse_chess_chessboard[row_index][column_index] = current_color
                    # if current_color == origin_color:
                    #     self.chess_state_value += AI.value[int(min(row_index, 7 - row_index))][
                    #         int(min(column_index, 7 - column_index))]
                    # else:
                    #     self.chess_state_value += AI.reverse_value[int(min(row_index, 7 - row_index))][
                    #         int(min(column_index, 7 - column_index))]
        after_reverse_chess_chessboard[chess_position[0]][chess_position[1]] = current_color
        return after_reverse_chess_chessboard

    # use for simulation
    # originally $is_leaf_node$ is [True, True]
    # when is_leaf_node comes to [False, False], it's a leaf node
    # is_leaf_node will be checked after every step and then decide to return it or not
    def simulator_MCTS(self, origin_chessboard, color_role, progress, simulation_result_value, is_leaf_node):
        if progress >= 64:
            simulation_result_value = self.evaluate_similation(chessboard=origin_chessboard, color_role=color_role)
            return simulation_result_value

        after_chessboard = origin_chessboard
        after_after_chessboard = origin_chessboard

        # self_play part
        is_leaf_node[0] = is_leaf_node[1]
        self_play_legal_position_list = self.find_legal_answer_list(self, origin_chessboard=origin_chessboard,
                                                                    idx=AI.find_null_point(
                                                                        chessboard=origin_chessboard),
                                                                    color_role=color_role)
        if len(self_play_legal_position_list) > 0:
            best_score = self.min_int
            best_legal_position_direction_list = self_play_legal_position_list[0]
            for i in range(len(self_play_legal_position_list)):
                current_position = self_play_legal_position_list[i][0]
                current_score = self.value[int(min(current_position[0], 8 - current_position[0] - 1))][
                    int(min(current_position[1], 8 - current_position[1] - 1))]
                if current_score > best_score:
                    best_legal_position_direction_list = self_play_legal_position_list[i]
                    best_score = current_score
            after_chessboard = self.reverse_chess_by_chess_MCTS(origin_chessboard=origin_chessboard,
                                                                legal_direction_list=best_legal_position_direction_list[
                                                                    1],
                                                                current_color=color_role,
                                                                chess_position=best_legal_position_direction_list[0])
            is_leaf_node[1] = True
            progress += 1
        else:
            is_leaf_node[1] = False
        after_after_chessboard = after_chessboard

        if is_leaf_node[0] == False and is_leaf_node[1] == False:
            simulation_result_value = self.evaluate_similation(chessboard=after_chessboard, color_role=color_role)
            return simulation_result_value

        # opponent_play part
        is_leaf_node[0] = is_leaf_node[1]
        rival_play_legal_position_list = self.find_legal_answer_list(self, origin_chessboard=after_chessboard,
                                                                     idx=AI.find_null_point(
                                                                         chessboard=after_chessboard),
                                                                     color_role=~color_role + 1)
        if len(rival_play_legal_position_list) > 0:
            best_score = self.max
            best_legal_position_direction_list = self_play_legal_position_list[0]
            for i in range(len(self_play_legal_position_list)):
                current_position = self_play_legal_position_list[i][0]
                current_score = self.reverse_value[int(min(current_position[0], 8 - current_position[0] - 1))][
                    int(min(current_position[1], 8 - current_position[1] - 1))]
                if current_score < best_score:
                    best_legal_position_direction_list = self_play_legal_position_list[i]
                    best_score = current_score
            after_after_chessboard = self.reverse_chess_by_chess_MCTS(origin_chessboard=after_chessboard,
                                                                      legal_direction_list=
                                                                      best_legal_position_direction_list[1],
                                                                      current_color=~color_role + 1,
                                                                      chess_position=best_legal_position_direction_list[
                                                                          0])
            is_leaf_node[1] = True
            progress += 1
        else:
            is_leaf_node[1] = False

        if is_leaf_node[0] == False and is_leaf_node[1] == False:
            simulation_result_value = self.evaluate_similation(chessboard=after_after_chessboard, color_role=color_role)
            return simulation_result_value

        simulation_result_value = self.simulator_MCTS(origin_chessboard=after_after_chessboard, color_role=color_role,
                                                      progress=progress,
                                                      simulation_result_value=simulation_result_value,
                                                      is_leaf_node=is_leaf_node)
        return simulation_result_value

    # firstly find whether this position is legal or not
    # then record this position is legal in which direction among the eight directions
    def legal(self, origin_chessboard, color_role, position):
        loop_total_list = [0, 0]
        return_list = [False, -1, -1, -1, -1, -1, -1, -1, -1]
        # the reverse_chessboard is reversed according to the player's color
        # bud does this really make sense
        # just remember to input the origin chessboard and this def will help you to reverse it automatically
        reverse_chessboard = AI.reverse_by_role(self, origin_chessboard=origin_chessboard, color_role=color_role)
        for direction_order_index in range(8):
            current_direction = AI.direction[direction_order_index]
            for i in range(2):
                if current_direction[i] == 0:
                    loop_total_list[i] = 8 + 1
                else:
                    loop_total_list[i] = max(-position[i] / current_direction[i],
                                             (-position[i] + 8 - 1) / current_direction[i])
            loop_total = min(loop_total_list[0], loop_total_list[1])
            for loop_counter in range(int(loop_total)):
                row_index = position[0] + current_direction[0] * (loop_counter + 1)
                column_index = position[1] + current_direction[1] * (loop_counter + 1)
                if reverse_chessboard[row_index][column_index] == 0:
                    return_list[direction_order_index + 1] = 0
                    break
                if reverse_chessboard[row_index][column_index] == 1 and loop_counter == 0:
                    return_list[direction_order_index + 1] = 0
                    break
                elif reverse_chessboard[row_index][column_index] == 1 and loop_counter != 0:
                    return_list[direction_order_index + 1] = loop_counter
                    return_list[0] = True
                    break
        return return_list

    # similar to the above def
    # the chessboard has been reversed in advance
    def reverse_chessboard_legal(self, reverse_chessboard, position):
        loop_total_list = [0, 0]
        return_list = [False, -1, -1, -1, -1, -1, -1, -1, -1]
        for direction_order_index in range(8):
            current_direction = AI.direction[direction_order_index]
            for i in range(2):
                if current_direction[i] == 0:
                    loop_total_list[i] = 8 + 1
                else:
                    loop_total_list[i] = max(-position[i] / current_direction[i],
                                             (-position[i] + 8 - 1) / current_direction[i])
            loop_total = min(loop_total_list[0], loop_total_list[1])
            for loop_counter in range(int(loop_total)):
                row_index = position[0] + current_direction[0] * (loop_counter + 1)
                column_index = position[1] + current_direction[1] * (loop_counter + 1)
                if reverse_chessboard[row_index][column_index] == 0:
                    return_list[direction_order_index + 1] = 0
                    break
                if reverse_chessboard[row_index][column_index] == 1 and loop_counter == 0:
                    return_list[direction_order_index + 1] = 0
                    break
                elif reverse_chessboard[row_index][column_index] == 1 and loop_counter != 0:
                    return_list[direction_order_index + 1] = loop_counter + 1
                    return_list[0] = True
                    break
        return return_list

    # used when need to find child position among null positions
    def find_null_point(self, chessboard):
        return_null_point_list = []
        for row in range(len(chessboard)):
            for column in range(len(chessboard[0])):
                if chessboard[row][column] == 0:
                    return_null_point_list.append((row, column))
        return return_null_point_list

    # find all the answer to candidate_list without valuation
    def find_legal_answer(self, origin_chessboard, idx, color_role):
        reverse_chessboard = self.reverse_by_role(origin_chessboard, color_role)
        legal_position_list = []
        for order in range(len(idx)):
            position = idx[order]
            if self.reverse_chessboard_legal(reverse_chessboard, position)[0]:
                legal_position_list.append(idx[order])
        return legal_position_list

    # find all the answer and their detail direction which is available
    # will be used in MCTS as its simulation will use it to generate next step
    # it will return [(tuple),[answer like find_legal_answer]] and (tuple) is the position
    def find_legal_answer_list(self, origin_chessboard, idx, color_role):
        reverse_chessboard = self.reverse_by_role(origin_chessboard, color_role)
        legal_position_list = []
        for order in range(len(idx)):
            position = idx[order]
            is_legal_list = self.reverse_chessboard_legal(reverse_chessboard, position)
            if is_legal_list[0]:
                legal_position_list.append([position, is_legal_list])
        return legal_position_list

    # The input is current chessboard.
    def go(self, chessboard):
        # Clear candidate_list, must do this step
        self.candidate_list.clear()
        # ==================================================================
        # #Write your algorithm here
        # Here is the simplest sample:Random decision
        idx = np.where(chessboard == COLOR_NONE)
        idx = list(zip(idx[0], idx[1]))
        # chessboard_reverse_by_role = self.reverse_by_role(chessboard, self.color)
        # self.candidate_list.append(self.find_legal_answer(chessboard, idx, self.color))
        legal_answer_list = self.find_legal_answer(chessboard, idx, self.color)
        for i in range(len(legal_answer_list)):
            self.candidate_list.append(legal_answer_list[i])
        # self.candidate_list = self.first_edition(candidate_list=self.candidate_list)
        # self.candidate_list = self.second_edition(candidate_list=self.candidate_list)
        # print(self.candidate_list)
        self.candidate_list = self.third_edition(candidate_list=self.candidate_list, origin_chessboard=chessboard,
                                                 idx=idx)
        # self.candidate_list.append(self.minimax())
        return self.candidate_list

    def first_edition(self, candidate_list):
        distance_square = 0
        standard_distance = 8 / 2
        for i in range(len(candidate_list)):
            if (candidate_list[i][0] - standard_distance) ** 2 + (
                    candidate_list[i][1] - standard_distance) ** 2 > distance_square:
                if candidate_list[i] not in [(0, 1), (1, 0), (1, 1), (0, 6), (1, 6), (1, 7), (6, 0), (6, 1), (7, 1),
                                             (6, 6), (6, 7), (7, 6)]:
                    candidate_list.append(candidate_list[i])
                    distance_square = (candidate_list[i][0] - 4.5) ** 2 + (candidate_list[i][1] - 4.5) ** 2
        return candidate_list

    def second_edition(self, candidate_list):
        best_score = 0
        for i in range(len(candidate_list)):
            current_position = candidate_list[i]
            current_score = self.value[int(min(current_position[0], 8 - current_position[0] - 1))][
                int(min(current_position[1], 8 - current_position[1] - 1))]
            if current_score > best_score:
                candidate_list.append(current_position)
                best_score = current_score
        return candidate_list

    def third_edition(self, candidate_list, origin_chessboard, idx):
        final_chose_evaluate = self.min_int
        # self.candidate_list.clear()
        for i in range(len(candidate_list)):
            current_chessboard_node = self.ChessboardNode(current_color=self.color, origin_color=self.color,
                                                          chess_position=self.candidate_list[i],
                                                          origin_chessboard=origin_chessboard, deep=2,
                                                          progress=64 - len(idx))
            current_chose_node_evaluate = self.minimax(current_chessboard_node, 1, True, 64 - len(idx))
            current_chose_node_evaluate += current_chessboard_node.stable_advance_get_chess_state_value()
            current_chose_node_evaluate += current_chessboard_node.bonus_corner_advance_get_chess_state_value()
            # print(current_chessboard_node.hierarchy_evaluate, "and its position is ",
            #       current_chessboard_node.chess_position)
            # print("position is ", candidate_list[i], " and hierarchy is ", current_chose_node_evaluate)
            if current_chose_node_evaluate > final_chose_evaluate:
                final_chose_node_position = current_chessboard_node.chess_position
                final_chose_evaluate = current_chose_node_evaluate
                candidate_list.append(final_chose_node_position)
                # print("chose one: ==============")
                # print(current_chessboard_node.hierarchy_evaluate, "and its position is ",
                #       current_chessboard_node.chess_position)
                # print("chose one: ==============")
        # for i in range(len(candidate_list)):
        #     if candidate_list[i] == (0, 0) or candidate_list[i] == (0, 7) or candidate_list[i] == (7, 0) or \
        #             candidate_list[i] == (7, 7):
        #         candidate_list.append(candidate_list[i])
                # print("bingo")
        return candidate_list

    # def fourth_edition(self, candidate_list, origin_chessboard, idx):
    #     progress = 64 - len(idx)
    #     if progress > 36:
    #         self.third_edition(candidate_list=candidate_list, origin_chessboard=origin_chessboard, idx=idx)
    #     else:
    #         self.MCTSnode()

    def minimax(self, chessboard_node: ChessboardNode, deep: int, maximizing_player: bool, progress: int):
        # print("++++++++++++++++++")
        # print("deep is ", deep)
        # print("player is origin? ", maximizing_player)
        # print("progress: ", progress)
        # print("++++++++++++++++++")
        if deep == 0 or progress == 64:
            # print("return value is: ", chessboard_node.chess_state_value, " and the position is",chessboard_node.chess_position)
            chessboard_node.hierarchy_evaluate = chessboard_node.chess_state_value
            return chessboard_node.hierarchy_evaluate

        # maximizing_player is also the origin player
        if maximizing_player:
            max_evaluate = self.min_int
            # max_evaluate_node = chessboard_node
            for index_find_max in range(len(chessboard_node.children_state_list)):
                evaluate_node_value = self.minimax(chessboard_node.children_state_list[index_find_max], deep - 1,
                                                   False, progress + 1)
                if evaluate_node_value > max_evaluate:
                    max_evaluate = evaluate_node_value
                chessboard_node.hierarchy_evaluate = max_evaluate + chessboard_node.chess_state_value * (deep + 1)
                # chessboard_node.hierarchy_evaluate = max_evaluate
            return chessboard_node.hierarchy_evaluate
        else:
            min_evaluate = self.max_int
            # min_evaluate_node = chessboard_node
            for index_find_min in range(len(chessboard_node.children_state_list)):
                evaluate_node_value = self.minimax(chessboard_node.children_state_list[index_find_min], deep - 1,
                                                   True, progress + 1)
                if evaluate_node_value < min_evaluate:
                    min_evaluate = evaluate_node_value
                chessboard_node.hierarchy_evaluate = min_evaluate + chessboard_node.chess_state_value * (deep + 1)
                # chessboard_node.hierarchy_evaluate = min_evaluate
            return chessboard_node.hierarchy_evaluate


# ==============Find new pos========================================
# Make sure that the position of your decision in chess board is empty.
# If not, the system will return error.
# Add your decision into candidate_list, Records the chess board
# You need add all the positions which is valid
# candidate_list example: [(3,3),(4,4)]
# You need append your decision at the end of the candidate_list,
# we will choose the last element of the candidate_list as the position you choose
# If there is no valid position, you must return a empty list.


if __name__ == '__main__':
    # COLOR_BLACK = -1
    # COLOR_WHITE = 1
    chessboard_example = np.ndarray(shape=(8, 8), dtype=int, buffer=np.array(
        [0, 0, 0, 0, 0, 0, 1, 0,
         0, -1, 0, 1, 0, 1, 1, 0,
         -1, -1, 1, 1, 1, -1, 1, 0,
         0, 1, -1, 1, -1, 0, 0, 0,
         1, 1, -1, -1, -1, -1, -1, 0,
         0, 1, -1, 1, 0, -1, -1, 0,
         0, 1, 1, 1, 0, 0, -1, 0,
         0, 0, 0, 0, 0, 0, 0, 0]), offset=0, order="C")
    ai = AI(8, -1, 10)
    print(ai.go(chessboard_example))
    row_index = 6
    column_index = 1
    print(AI.value[int(min(row_index, 7 - row_index))][int(min(column_index, 7 - column_index))])
