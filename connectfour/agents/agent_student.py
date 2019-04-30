from connectfour.agents.computer_player import RandomAgent
import random

class StudentAgent(RandomAgent):
    def __init__(self, name):
        super().__init__(name)
        self.MaxDepth = 1


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
        heuristic = 0

        #   put tokens in the center column as much as possible
        heuristic += self.control_center(board)
        return heuristic
    
    def control_center(self, board):
        """
        count the number of my tokens and opponent's tokens
        the closer my tokens to the middle, the higher score it gets
        get score for my tokens
        lose score for opponent's tokens
        """
        heuristic = 0
        center_column = 3
        score_center_col = 5
        score_2_4_col = 3
        score_1_5_col = 2
        
        old_max, old_min, new_max, new_min = 0, 0, 0, 0

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
        
        """
        fit the value between -1 and 1
        """
        old_max = score_center_col * board.height + score_2_4_col * board.height * 2.0 + score_1_5_col * board.height * 2.0
        old_min = 0 - old_max
        new_max = 1.0
        new_min = -1.0
        
        value = self.fit_range(old_max, old_min, new_max, new_min, heuristic)

        return value

    def fit_range(self, old_max, old_min, new_max, new_min, old_value):
        """
        fit number range to range from -1 to 1
        """
        
        old_range = old_max - old_min
        new_range = new_max - new_min
        new_value = (((old_value - old_min) * new_range) / old_range) + new_min

        return new_value

