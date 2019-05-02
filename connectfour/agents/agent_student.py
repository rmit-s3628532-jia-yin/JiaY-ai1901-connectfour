from connectfour.agents.computer_player import RandomAgent
import random
import copy

class StudentAgent(RandomAgent):
    def __init__(self, name):
        super().__init__(name)
        self.MaxDepth = 4

    def get_move(self, board):
        """
        Args:
            board: An instance of `Board` that is the current state of the board.

        Returns:
            A tuple of two integers, (row, col)
        """

        valid_moves = board.valid_moves()
        vals = []
        moves = []

        for move in valid_moves:
            next_state = board.next_state(self.id, move[1])
            moves.append( move )
            vals.append( self.dfMiniMax(next_state, 1) )

        bestMove = moves[vals.index( max(vals) )]
        return bestMove

    def dfMiniMax(self, board, depth):
        # Goal return column with maximized scores of all possible next states
        
        if depth == self.MaxDepth:
            return self.evaluateBoardState(board)

        valid_moves = board.valid_moves()
        vals = []
        moves = []

        for move in valid_moves:
            if depth % 2 == 1:
                next_state = board.next_state(self.id % 2 + 1, move[1])
            else:
                next_state = board.next_state(self.id, move[1])
                
            moves.append( move )
            vals.append( self.dfMiniMax(next_state, depth + 1) )

        
        if depth % 2 == 1:
            bestVal = min(vals)
        else:
            bestVal = max(vals)

        return bestVal

    def evaluateBoardState(self, board):
        """
        Your evaluation function should look at the current state and return a score for it. 
        As an example, the random agent provided works as follows:
            If the opponent has won this game, return -1.
            If we have won the game, return 1.
            If neither of the players has won, return a random number.
        """
        
        """
        These are the variables and functions for board objects which may be helpful when creating your Agent.
        Look into board.py for more information/descriptions of each, or to look for any other definitions which may help you.

        Board Variables:
            board.width 
            board.height
            board.last_move
            board.num_to_connect
            board.winning_zones
            board.score_array 
            board.current_player_score

        Board Functions:
            get_cell_value(row, col)
            try_move(col)
            valid_move(row, col)
            valid_moves()
            terminal(self)
            legal_moves()
            next_state(turn)
            winner()
        """
        
        sum_heuristics = 0   # sum of heuristics
        sum_old_max = 0     # sum of max value of each heuristic
        
        heuristic = 0
        old_max = 0
        
        """
        best state is winning the game by connecting 4 tokens
        worst state is opponent winning the game
        """
        if self.winner(board) == self.id % 2 + 1:
            # print("losing!")
            return -1.0
        if self.winner(board) == self.id:
            # print("winning!")
            return 1.0
        
        #   put tokens in the center column as much as possible
        #   get points for my tokens in the middle, lose points for opponent tokens
        heuristic, old_max = self.control_center(board)
        sum_heuristics += heuristic
        sum_old_max += old_max
        
        #   try to connect four tokens
        heuristic, old_max = self.can_get_4_in_a_line(board)
        sum_heuristics += heuristic
        sum_old_max += old_max
        
        # set up multidirectional attack by placing 3 tokens in a line while the cells to the left and right are empty
        heuristic, old_max = self.set_up_multidirectional_attack(board)
        sum_heuristics += heuristic
        sum_old_max += old_max
        
        """
        fit the value between -1 and 1
        """
        new_max = 1.0
        new_min = -1.0
        
        value = self.fit_range(sum_old_max, 0 - sum_old_max, new_max, new_min, sum_heuristics)
        
        return value
    
    def control_center(self, board):
        """
        count the number of my tokens and opponent's tokens
        the closer my tokens to the middle, the higher score it gets
        get score for my tokens
        lose score for opponent's tokens
        """
        heuristic = 0   # value of this heuristic function
        center_column = 3
        score_center_col = 6
        score_2_4_col = 4
        score_1_5_col = 2
        
        max = 0     #   maximum value of this heuristic
        
        for x in range(board.height):
            #   center column
            if board.get_cell_value(x, center_column) == self.id:
                heuristic += score_center_col
            if board.get_cell_value(x, center_column) == self.id % 2 + 1:
                heuristic -= score_center_col
        
            #   2nd and 4th column
            if board.get_cell_value(x, 2) == self.id or board.get_cell_value(x, 4) == self.id:
                heuristic += score_2_4_col
            if board.get_cell_value(x, 2) == self.id % 2 + 1 or board.get_cell_value(x, 4) == self.id % 2 + 1:
                heuristic -= score_2_4_col
                
            #   1st and 5th column
            if board.get_cell_value(x, 1) == self.id or board.get_cell_value(x, 5) == self.id:
                heuristic += score_1_5_col
            if board.get_cell_value(x, 1) == self.id % 2 + 1 or board.get_cell_value(x, 5) == self.id % 2 + 1:
                heuristic -= score_1_5_col
    
        max = score_center_col * board.height + score_2_4_col * board.height * 2.0 + score_1_5_col * board.height * 2.0

        return heuristic, max

    def can_get_4_in_a_line(self, board):
        """
        check if it's possible to get 4 of my tokens to be adjacent horizontally, vertically or diagonally
        if so, get points based on the number of my tokens in place i.e. if 2 tokens are in place, gain 3 points. if 3 tokens are in place, gain 10 points
        do the same for opponent tokens except that we lose score based on the number of tokens in place
        """
        heuristic = 0
        #   horizontal gets the most points because we can place token in the middle, on the left, or on the right to form a line
        #   diagonal gets the second most points because the chance of forming a diagonal is not as much as forming a line horizontally
        #   vertical gets the least points becase we can only place a token on the top to form a line, and it's easily blocked
        horizontal_points_2_in_place = 4    #  points added to heuristic when 2 tokens are in place
        horizontal_points_3_in_place = 30
        vertical_points_2_in_place = 1
        vertical_points_3_in_place = 2
        diagonal_points_2_in_place = 3
        diagonal_points_3_in_place = 20
        
        max_horizontal, max_vertical, max_diagonal = horizontal_points_3_in_place * 4 * board.height, vertical_points_3_in_place * 3 * board.width, diagonal_points_3_in_place * 4 * 3 * 2
        
        max = max_horizontal + max_vertical + max_diagonal
        
        heuristic += self._horizontal_check(board, horizontal_points_2_in_place, horizontal_points_3_in_place)
        heuristic += self._vertical_check(board, vertical_points_2_in_place, vertical_points_3_in_place)
        heuristic += self._diagonal_check(board, diagonal_points_2_in_place, diagonal_points_3_in_place)
        
        return heuristic, max
    
    def _horizontal_check(self, board, points_2_in_place, points_3_in_place):
        """
        for each row, there are 4 possible ways to connect 4 tokens
        check each of these 4 possibilities, and count how many tokens are in place
        get or lose points based on the number of my tokens and opponent tokens
        """
        heuristic = 0
        count_ways_to_connect4 = 4
        num_tokens_in_place = 0
        can_connect_4 = True	# if there is an opponent token in the line, make it false
        
        #   calculate points for me
        for row in range(board.height):
            start = 0
            end = 4
            for i in range(count_ways_to_connect4):
                for col in range(start + i, end + i):
                	# if there is an opponent token in the line, don't check the following cells
                	# and don't get any points for the current check
                    if board.get_cell_value(row, col) == self.id % 2 + 1:
                    	can_connect_4 = False
                    	break
                    if board.get_cell_value(row, col) == self.id:
                        num_tokens_in_place += 1

                if can_connect_4 == False:
                	num_tokens_in_place = 0
                	can_connect_4 = True
                	continue
                if num_tokens_in_place == 2:
#                    print("2 tokens")
                    heuristic += points_2_in_place  # get points
                if num_tokens_in_place == 3:
#                    print("3 tokens")
                    heuristic += points_3_in_place
                num_tokens_in_place = 0
        
        can_connect_4 = True
        num_tokens_in_place = 0
        #   calculate points for opponent
        for row in range(board.height):
            start = 0
            end = 4
            for i in range(count_ways_to_connect4):
                for col in range(start + i, end + i):
                    if board.get_cell_value(row, col) == self.id:
                    	can_connect_4 = False
                    	break
                    if board.get_cell_value(row, col) == self.id % 2 + 1:
                        num_tokens_in_place += 1

                if can_connect_4 == False:
                    num_tokens_in_place = 0
                    can_connect_4 = True
                    continue
                if num_tokens_in_place == 2:
#                    print("2 opponent tokens")
                    heuristic -= points_2_in_place  #   lose points
                if num_tokens_in_place == 3:
#                    print("3 opponent tokens")
                    heuristic -= points_3_in_place
                num_tokens_in_place = 0
    
    
        return heuristic
    
    def _vertical_check(self, board, points_2_in_place, points_3_in_place):
        """
        for each column, do the same as in horizontal check
        """
        heuristic = 0
        count_ways_to_connect4 = 3
        num_tokens_in_place = 0
        can_connect_4 = True    # if there is an opponent token in the line, make it false
        
        #   calculate points for me
        for col in range(board.width):
            start = 0
            end = 4
            for i in range(count_ways_to_connect4):
                for row in range(start + i, end + i):
                    # if there is an opponent token in the line, don't check the following cells
                    # and don't get any points for the current check
                    if board.get_cell_value(row, col) == self.id % 2 + 1:
                        can_connect_4 = False
                        break
                    if board.get_cell_value(row, col) == self.id:
                        num_tokens_in_place += 1
            
                if can_connect_4 == False:
                    num_tokens_in_place = 0
                    can_connect_4 = True
                    continue
                if num_tokens_in_place == 2:
                    # print("2 tokens are in place")
                    heuristic += points_2_in_place  # get points
                if num_tokens_in_place == 3:
                    # print("3 tokens are in place")
                    heuristic += points_3_in_place
                num_tokens_in_place = 0
                
        can_connect_4 = True
        num_tokens_in_place = 0
        
        #   calculate points for opponent
        for column in range(board.width):
            start = 0
            end = 4
            for i in range(count_ways_to_connect4):
                for row in range(start + i, end + i):
                    if board.get_cell_value(row, col) == self.id:
                        can_connect_4 = False
                        break
                    if board.get_cell_value(row, col) == self.id % 2 + 1:
                        num_tokens_in_place += 1
            
                if can_connect_4 == False:
                    num_tokens_in_place = 0
                    can_connect_4 = True
                    continue
                if num_tokens_in_place == 2:
                    # print("2 opponent tokens are in place")
                    heuristic -= points_2_in_place  #   lose points
                if num_tokens_in_place == 3:
                    # print("3 opponent tokens are in place")
                    heuristic -= points_3_in_place
                num_tokens_in_place = 0
                
        # print(heuristic)
        return heuristic
    
    def _diagonal_check(self, board, points_2_in_place, points_3_in_place):
        heuristic = 0
        count_ways_to_connect4 = 4
        num_tokens_in_place = 0
        can_connect_4 = True    # if there is an opponent token in the line, make it false
        
        #   top-left to bottom-right diagonal
        
        #   calculate points for me
        for row in range(3):
            start = 0
            end = 4
            for i in range(count_ways_to_connect4):
                row_offset = 0
                for col in range(start + i, end + i):
                    # if there is an opponent token in the line, don't check the following cells
                    # and don't get any points for the current check
                    if board.get_cell_value(row + row_offset, col) == self.id % 2 + 1:
                        can_connect_4 = False
                        break
                    if board.get_cell_value(row + row_offset, col) == self.id:
                        num_tokens_in_place += 1
                    row_offset += 1
                        
                if can_connect_4 == False:
                    num_tokens_in_place = 0
                    can_connect_4 = True
                    continue
                if num_tokens_in_place == 2:
                    heuristic += points_2_in_place  # get points
                if num_tokens_in_place == 3:
                    heuristic += points_3_in_place
                num_tokens_in_place = 0
                
        can_connect_4 = True
        num_tokens_in_place = 0
        #   calculate points for opponent
        for row in range(3):
            start = 0
            end = 4
            for i in range(count_ways_to_connect4):
                row_offset = 0
                for col in range(start + i, end + i):
                    if board.get_cell_value(row + row_offset, col) == self.id:
                        can_connect_4 = False
                        break
                    if board.get_cell_value(row + row_offset, col) == self.id % 2 + 1:
                        num_tokens_in_place += 1
                    row_offset += 1

                if can_connect_4 == False:
                    num_tokens_in_place = 0
                    can_connect_4 = True
                    continue
                if num_tokens_in_place == 2:
                    heuristic -= points_2_in_place  #   lose points
                if num_tokens_in_place == 3:
                    heuristic -= points_3_in_place
                num_tokens_in_place = 0
        
        #   bottom-left to top-right diagonal
        
        #   calculate points for me
        for row in range(3, 6):
            start = 0
            end = 4
            for i in range(count_ways_to_connect4):
                row_offset = 0
                for col in range(start + i, end + i):
                    # if there is an opponent token in the line, don't check the following cells
                    # and don't get any points for the current check
                    if board.get_cell_value(row - row_offset, col) == self.id % 2 + 1:
                        can_connect_4 = False
                        break
                    if board.get_cell_value(row - row_offset, col) == self.id:
                        num_tokens_in_place += 1
                    row_offset += 1
                
                if can_connect_4 == False:
                    num_tokens_in_place = 0
                    can_connect_4 = True
                    continue
                if num_tokens_in_place == 2:
                    heuristic += points_2_in_place  # get points
                if num_tokens_in_place == 3:
                    heuristic += points_3_in_place
                num_tokens_in_place = 0

        can_connect_4 = True
        num_tokens_in_place = 0
        #   calculate points for opponent
        for row in range(3, 6):
            start = 0
            end = 4
            for i in range(count_ways_to_connect4):
                row_offset = 0
                for col in range(start + i, end + i):
                    if board.get_cell_value(row - row_offset, col) == self.id:
                        can_connect_4 = False
                        break
                    if board.get_cell_value(row - row_offset, col) == self.id % 2 + 1:
                        num_tokens_in_place += 1
                    row_offset += 1
                
                if can_connect_4 == False:
                    num_tokens_in_place = 0
                    can_connect_4 = True
                    continue
                if num_tokens_in_place == 2:
                    heuristic -= points_2_in_place  #   lose points
                if num_tokens_in_place == 3:
                    heuristic -= points_3_in_place
                num_tokens_in_place = 0

        return heuristic

    def set_up_multidirectional_attack(self, board):
        """
        set up a multidirectional attack i.e. place three adjacent tokens in a row while the
        cell on the left and right are empty, so we can win in both directions
        same applies to diagonals
        do the same for the opponent, but lose score for satisfied condition
        """
        heuristic = 0
        empty = 0
        count_ways_to_set_up_horizontal = 3 # there are 3 ways to set up a multidirectional attack in a row
        count_ways_to_set_up_diagonal = 3
        num_cells_to_check = 5
        points_horizontal = 50
        points_diagonal = 50

        max = points_horizontal * count_ways_to_set_up_horizontal * board.height + points_diagonal * count_ways_to_set_up_diagonal * 2

        # horizontal
        for row in range(board.height):
            for i in range(count_ways_to_set_up_horizontal):
                currCells = []
                for j in range(num_cells_to_check):
                    currCells.append(board.get_cell_value(row, j + i))
            # if multidirectional attack conditions are satisfied
            if currCells[0] == empty and currCells[1] == self.id and currCells[2] == self.id and currCells[3] == self.id and currCells[4] == empty:
                heuristic += points_horizontal  # get points
            if currCells[0] == empty and currCells[1] == self.id % 2 + 1 and currCells[2] == self.id % 2 + 1 and currCells[3] == self.id % 2 + 1 and currCells[4] == empty:
                heuristic -= points_horizontal  # lose points
            currCells = []

        # top-left to bottom-right diagonal
        for row in range(2):
            for i in range(count_ways_to_set_up_diagonal):
                row_offset = 0
                currCells = []
                for j in range(num_cells_to_check):
                    currCells.append(board.get_cell_value(row + row_offset, j + i))
                    row_offset += 1
            # if multidirectional attack conditions are satisfied
            if currCells[0] == empty and currCells[1] == self.id and currCells[2] == self.id and currCells[3] == self.id and currCells[4] == empty:
                heuristic += points_diagonal  # get points
            if currCells[0] == empty and currCells[1] == self.id % 2 + 1 and currCells[2] == self.id % 2 + 1 and currCells[3] == self.id % 2 + 1 and currCells[4] == empty:
                heuristic -= points_diagonal  # lose points
            currCells = []

        # bottom-left to top-right diagonal
        for row in range(4, 6):
            for i in range(count_ways_to_set_up_diagonal):
                row_offset = 0
                currCells = []
                for j in range(num_cells_to_check):
                    currCells.append(board.get_cell_value(row - row_offset, j + i))
                    row_offset += 1
            # if multidirectional attack conditions are satisfied
            if currCells[0] == empty and currCells[1] == self.id and currCells[2] == self.id and currCells[3] == self.id and currCells[4] == empty:
                heuristic += points_diagonal  # get points
            if currCells[0] == empty and currCells[1] == self.id % 2 + 1 and currCells[2] == self.id % 2 + 1 and currCells[3] == self.id % 2 + 1 and currCells[4] == empty:
                heuristic -= points_diagonal  # lose points
            currCells = []

        return heuristic, max

    def winner(self, board):
        """
        Takes the board as input and determines if there is a winner.
        If the game has a winner, it returns the player number (Player One = 1, Player Two = 2).
        If the game is still ongoing, it returns zero.
        """
        row_winner = self._check_rows(board)
        if row_winner:
            return row_winner
        col_winner = self._check_columns(board)
        #print("col winner = ", col_winner)
        if col_winner:
            return col_winner
        diag_winner = self._check_diagonals(board)
        if diag_winner:
            return diag_winner
        return 0  # no winner yet

    def _check_rows(self, board):
        for row in board.board:
            same_count = 1
            curr = row[0]
            for i in range(1, board.width):
                if row[i] == curr:
                    same_count += 1
                    if same_count == board.num_to_connect and curr != 0:
                        return curr
                else:
                    same_count = 1
                    curr = row[i]
        return 0

    def _check_columns(self, board):
        for i in range(board.width):
            same_count = 1
            curr = board.board[0][i]
            for j in range(1, board.height):
                if board.board[j][i] == curr:
                    same_count += 1
                    if same_count == board.num_to_connect and curr != 0:
                        return curr
                else:
                    same_count = 1
                    curr = board.board[j][i]
        return 0

    def _check_diagonals(self, board):
        boards = [
            board.board,
            [row[::-1] for row in copy.deepcopy(board.board)]
        ]

        for b in boards:
            for i in range(board.width - board.num_to_connect + 1):
                for j in range(board.height - board.num_to_connect + 1):
                    if i > 0 and j > 0:  # would be a redundant diagonal
                        continue

                    # (j, i) is start of diagonal
                    same_count = 1
                    curr = b[j][i]
                    k, m = j + 1, i + 1
                    while k < board.height and m < board.width:
                            if b[k][m] == curr:
                                same_count += 1
                                if same_count is board.num_to_connect and curr != 0:
                                    return curr
                            else:
                                same_count = 1
                                curr = b[k][m]
                            k += 1
                            m += 1
        return 0
    
    def fit_range(self, old_max, old_min, new_max, new_min, old_value):
        """
        fit number range to range from -1 to 1
        """
        
        old_range = old_max - old_min
        new_range = new_max - new_min
        new_value = (((old_value - old_min) * new_range) / old_range) + new_min

        return new_value

