import random
import math
import time

BOARD_SIZE = 8

PLAYER_NUM = 2
MCTS_NUM = 1

MAX_THINK_TIME = 5


# ------------------------------------
# Print out the board
# ------------------------------------
def printBoard(board):
    mcts_stones = 0
    player_stones = 0

    print("  0 1 2 3 4 5 6 7 ")
    print(" +-+-+-+-+-+-+-+-+")

    for i in range(0, BOARD_SIZE):
        print("" + str(i) + "|", end="")
        for j in range(0, BOARD_SIZE):
            if board[i][j] == 0:
                print(" |", end="")
            elif board[i][j] == MCTS_NUM:
                print("x|", end="")
                mcts_stones += 1
            else:
                print("o|", end="")
                player_stones += 1
        print("")
        print(" +-+-+-+-+-+-+-+-+")

    print("Your stones:", player_stones, "  MCTS stones:", mcts_stones)


# ------------------------------------
# Return a new initialized board
# ------------------------------------
def getInitialBoard():
    board = {}

    for i in range(0, BOARD_SIZE):
        board[i] = {}

        for j in range(0, BOARD_SIZE):
            board[i][j] = 0

    board[BOARD_SIZE / 2 - 1][BOARD_SIZE / 2 - 1] = MCTS_NUM
    board[BOARD_SIZE / 2][BOARD_SIZE / 2] = MCTS_NUM

    board[BOARD_SIZE / 2 - 1][BOARD_SIZE / 2] = PLAYER_NUM
    board[BOARD_SIZE / 2][BOARD_SIZE / 2 - 1] = PLAYER_NUM

    return board


# ------------------------------------
# Return a copy of a board
# ------------------------------------
def copyBoard(dest_board, src_board):
    for i in range(0, BOARD_SIZE):
        for j in range(0, BOARD_SIZE):
            dest_board[i][j] = src_board[i][j]


# ------------------------------------
# Return the number of specified stones in a board
# ------------------------------------
def countStones(board, turn):
    stones = 0

    for i in range(0, BOARD_SIZE):
        for j in range(0, BOARD_SIZE):
            if board[i][j] == turn:
                stones += 1

    return stones


# ------------------------------------
# Return a list of all positions in which the specified player can place a stone.
# ------------------------------------
def checkPlacablePositions(board, turn):
    placable_positions = []

    for i in range(0, BOARD_SIZE):
        for j in range(0, BOARD_SIZE):
            if board[i][j] != 0:
                continue
            if updateBoard(board, turn, i, j, checkonly=True) > 0:
                placable_positions.append((i, j))
    return placable_positions


# ------------------------------------
# Place a stone (when checkonly is True, it only returns the number
# of stones to be turned and it does not modify the board)
#
# Return: the number of stones to be turned
# (The new stone placed is not contained in the number)
# ------------------------------------
def updateBoard(board, turn, i, j, checkonly=False):
    if not (checkonly):
        board[i][j] = turn

    reversed_stone = 0

    # -------------------------------------------------
    flag = False
    for i2 in range(i + 1, BOARD_SIZE):
        if board[i2][j] == 0:
            break
        if board[i2][j] == turn:
            flag = True
            break
    if flag:
        for i3 in range(i + 1, i2):
            if not (checkonly):
                board[i3][j] = turn
            reversed_stone += 1

    flag = False
    for i2 in reversed(range(0, i)):
        if board[i2][j] == 0:
            break
        if board[i2][j] == turn:
            flag = True
            break
    if flag:
        for i3 in reversed(range(i2 + 1, i)):
            if not (checkonly):
                board[i3][j] = turn
            reversed_stone += 1

    # -------------------------------------------------
    flag = False
    for j2 in range(j + 1, BOARD_SIZE):
        if board[i][j2] == 0:
            break
        if board[i][j2] == turn:
            flag = True
            break
    if flag:
        for j3 in range(j + 1, j2):
            if not (checkonly):
                board[i][j3] = turn
            reversed_stone += 1

    flag = False
    for j2 in reversed(range(0, j)):
        if board[i][j2] == 0:
            break
        if board[i][j2] == turn:
            flag = True
            break
    if flag:
        for j3 in reversed(range(j2 + 1, j)):
            if not (checkonly):
                board[i][j3] = turn
            reversed_stone += 1
    # -------------------------------------------------

    flag = False
    for m in range(1, min(BOARD_SIZE - i, BOARD_SIZE - j)):
        if board[i + m][j + m] == 0:
            break
        if board[i + m][j + m] == turn:
            flag = True
            break
    if flag:
        for m3 in range(1, m):
            if not (checkonly):
                board[i + m3][j + m3] = turn
            reversed_stone += 1

    flag = False
    for m in range(1, min(i, j) + 1):
        if board[i - m][j - m] == 0:
            break
        if board[i - m][j - m] == turn:
            flag = True
            break
    if flag:
        for m3 in range(1, m):
            if not (checkonly):
                board[i - m3][j - m3] = turn
            reversed_stone += 1

    flag = False
    for m in range(1, min(i + 1, BOARD_SIZE - j)):
        if board[i - m][j + m] == 0:
            break
        if board[i - m][j + m] == turn:
            flag = True
            break
    if flag:
        for m3 in range(1, m):
            if not (checkonly):
                board[i - m3][j + m3] = turn
            reversed_stone += 1

    flag = False
    for m in range(1, min(BOARD_SIZE - i, j + 1)):
        if board[i + m][j - m] == 0:
            break
        if board[i + m][j - m] == turn:
            flag = True
            break
    if flag:
        for m3 in range(1, m):
            if not (checkonly):
                board[i + m3][j - m3] = turn
            reversed_stone += 1
    # -------------------------------------------------

    return reversed_stone


# ---------------------------------------------------------------------------------------------

# ------------------------------------
# Get a hand-input position
# ------------------------------------
def handinputNextPosition(board, turn):
    while True:
        print("Possible positions are ", checkPlacablePositions(board, turn))
        print("")

        while True:
            stri = input("Input vertical position[0-" + str(BOARD_SIZE - 1) + "]: ")
            if stri.isdigit() and int(stri) >= 0 and int(stri) < BOARD_SIZE:
                break
        while True:
            strj = input("Input horizontal position[0-" + str(BOARD_SIZE - 1) + "]: ")
            if strj.isdigit() and int(strj) >= 0 and int(strj) < BOARD_SIZE:
                break

        i = int(stri)
        j = int(strj)

        print("Your input : (", i, ",", j, ")")

        if board[i][j] == 0 and updateBoard(board, turn, i, j, checkonly=True) > 0:
            break
        print("not correct position!!")

    return (i, j)


# ------------------------------------
# Decide the next position utilizing MCTS
# ------------------------------------
def mctsNextPosition(board):
    def calc_ucb1(node_tuple, t, cval):
        name, nplayout, reward, childrens = node_tuple

        if nplayout == 0:
            nplayout = 0.00000000001

        if t == 0:
            t = 1

        return (reward / nplayout) + cval * math.sqrt(2 * math.log(t) / nplayout)

    def find_playout(brd, turn, depth=0):
        def eval_board(brd):
            player_stone = countStones(brd, PLAYER_NUM)
            mcts_stone = countStones(brd, MCTS_NUM)

            if mcts_stone > player_stone:
                return True
            return False

        # Playouts are stoped at the threshold depth.
        # In early stages of a game, detailed evaluation seems to be not necessary.
        if depth > 32:
            return eval_board(brd)

        turn_positions = checkPlacablePositions(brd, turn)

        # Check if the player can place a stone
        if len(turn_positions) == 0:
            if turn == MCTS_NUM:
                neg_turn = PLAYER_NUM
            else:
                neg_turn = MCTS_NUM

            neg_turn_positions = checkPlacablePositions(brd, neg_turn)

            if len(neg_turn_positions) == 0:
                # Return the result when both player cannot place a stone
                return eval_board(brd)
            else:
                # Change the turn when the other can place a stone
                turn = neg_turn
                turn_positions = neg_turn_positions

        # Place a stone randomly
        ijpair = turn_positions[random.randrange(0, len(turn_positions))]
        updateBoard(brd, turn, ijpair[0], ijpair[1])

        # Change the turn
        if turn == MCTS_NUM:
            turn = PLAYER_NUM
        else:
            turn = MCTS_NUM

        return find_playout(brd, turn, depth=depth + 1)

    def expand_node(brd, turn):
        positions = checkPlacablePositions(brd, turn)
        result = []

        for ijpair in positions:
            result.append((ijpair, 0, 0, []))

        return result

    def find_path_default_policy(root, total_playout):
        current_path = []
        current_childrens = root

        parent_playout = total_playout

        isMCTSTurn = True

        while True:
            if len(current_childrens) == 0:
                break

            maxidxlist = [0]
            cidx = 0
            if isMCTSTurn:
                maxval = -1
            else:
                maxval = 2

            for n_tuple in current_childrens:
                t_ijpair, t_nplayout, t_reward, t_childrens = n_tuple

                # In MCTS's turn, the node with the largest value is selected.
                # In the other's turn, the node with the least value is selected.

                if isMCTSTurn:
                    cval = calc_ucb1(n_tuple, parent_playout, 0.1)

                    if cval >= maxval:
                        if cval == maxval:
                            maxidxlist.append(cidx)
                        else:
                            maxidxlist = [cidx]
                            maxval = cval
                else:
                    cval = calc_ucb1(n_tuple, parent_playout, -0.1)

                    if cval <= maxval:
                        if cval == maxval:
                            maxidxlist.append(cidx)
                        else:
                            maxidxlist = [cidx]
                            maxval = cval

                cidx += 1

            # When plural candidates exist, a position is chosen randomly
            maxidx = maxidxlist[random.randrange(0, len(maxidxlist))]
            t_ijpair, t_nplayout, t_reward, t_childrens = current_childrens[maxidx]

            current_path.append(t_ijpair)
            parent_playout = t_nplayout
            current_childrens = t_childrens

            isMCTSTurn = not (isMCTSTurn)

        return current_path

    # -----------------------------------------------------
    root = expand_node(board, MCTS_NUM)
    current_board = getInitialBoard()
    current_board2 = getInitialBoard()

    start_time = time.time()

    for loop in range(0, 5000):

        # Check the time limit
        if (time.time() - start_time) >= MAX_THINK_TIME:
            break

        # --------------------------------------
        # Default policy
        current_path = find_path_default_policy(root, loop)

        # current_path contains a list of positions to be placed stones.
        # Following lines places stones according to the list.
        #
        # Note that the turn changes alternately.
        # Currently, a node corresponding to the situation requesting "pass" has no child nodes.
        # Thus it is not necessary to consider a player placing multiple stones at once.

        copyBoard(current_board, board)
        turn = MCTS_NUM
        for ijpair in current_path:
            updateBoard(current_board, turn, ijpair[0], ijpair[1])
            if turn == MCTS_NUM:
                turn = PLAYER_NUM
            else:
                turn = MCTS_NUM

        # --------------------------------------
        # Playout

        # the board needs to be copied because the board data is modified in find_playout

        copyBoard(current_board2, current_board)
        isWon = find_playout(current_board2, turn)
        # --------------------------------------

        if loop % 500 == 0 and loop > 0:
            print("loop:", loop, current_path, len(current_path), " eval val: ", isWon)

        # --------------------------------------
        # Up date of the tree (from the root of the tree to leafs)

        current_childrens = root

        for ijpair in current_path:
            idx = 0
            for n_tuple in current_childrens:
                t_ijpair, t_nplayout, t_reward, t_childrens = n_tuple
                if ijpair[0] == t_ijpair[0] and ijpair[1] == t_ijpair[1]:
                    break
                idx += 1

            if ijpair[0] == t_ijpair[0] and ijpair[1] == t_ijpair[1]:
                t_nplayout += 1
                if isWon:
                    t_reward += 1

                if t_nplayout >= 5 and len(t_childrens) == 0:
                    t_childrens = expand_node(current_board, turn)

                current_childrens[idx] = (t_ijpair, t_nplayout, t_reward, t_childrens)
            else:
                print("failed")

            current_childrens = t_childrens
    # --------------------------------------
    # -----------------------------------------------------

    print("loop count: ", loop)

    max_avg_reward = -1
    result_ij_pair = (0, 0)

    for n_tuple in root:
        t_ijpair, t_nplayout, t_reward, t_childrens = n_tuple

        if (t_nplayout > 0) and (t_reward / t_nplayout > max_avg_reward):
            result_ij_pair = t_ijpair
            max_avg_reward = t_reward / t_nplayout

    return result_ij_pair


# ---------------------------------------------------------------------------------------------
if __name__ == "__main__":

    random.seed(200)

    current_board = getInitialBoard()

    printBoard(current_board)

    isPlayerTurn = True

    while True:
        player_possibility = len(checkPlacablePositions(current_board, PLAYER_NUM))
        mcts_possibility = len(checkPlacablePositions(current_board, MCTS_NUM))

        # print(player_possibility)
        # print(mcts_possibility)

        if player_possibility == 0 and mcts_possibility == 0:
            break
        if (isPlayerTurn and player_possibility == 0) or (not (isPlayerTurn) and mcts_possibility == 0):
            isPlayerTurn = not (isPlayerTurn)
            continue

        if isPlayerTurn:
            print("Your turn:  ")
        else:
            print("MCTS's turn:  ")

        if isPlayerTurn:
            stone_pos = handinputNextPosition(current_board, PLAYER_NUM)
            updateBoard(current_board, PLAYER_NUM, stone_pos[0], stone_pos[1])
        else:
            stone_pos = mctsNextPosition(current_board)
            print("MCTS's answer: ", stone_pos)
            updateBoard(current_board, MCTS_NUM, stone_pos[0], stone_pos[1])

        printBoard(current_board)
        isPlayerTurn = not (isPlayerTurn)

    player_stone = countStones(current_board, PLAYER_NUM)
    mcts_stone = countStones(current_board, MCTS_NUM)

    print("RESULT:")
    print("  Your stones   : ", player_stone)
    print("  MCTS's stones : ", mcts_stone)

    if player_stone > mcts_stone:
        print("You won")
    elif player_stone == mcts_stone:
        print("Draw")
    else:
        print("You lose")

    printBoard(current_board)