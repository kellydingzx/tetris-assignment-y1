from board import Direction, Rotation, Shape
from random import Random
import statistics

# reference 1: El-Tetris – An Improvement on Pierre Dellacherie’s Algorithm
# https://imake.ninja/el-tetris-an-improvement-on-pierre-dellacheries-algorithm/ 
# date of access: 20/11/2019
# reference 2: Amine Boumaza. How to design good Tetris players. 2013. hal-00926213

class Player:
    def apply_moves(self, board, moves):
        # apply the elements in moves to the board.
        for move in moves:
            if isinstance(move, Direction):
                landed = board.move(move)
            elif isinstance(move, Rotation):
                landed = board.rotate(move)
            if landed:
                return True
        return False
    
    def test_drop(self,movebox,dest):
        if not movebox.falling:
            return None
        move_list = []
        num_falling = len(movebox.falling.cells)
        num_fallen = len(movebox.cells)
        #find out the representitive x-coordinate of the block
        x_rep = 10
        for tup in movebox.falling.cells:
            if tup[0] < x_rep:
                x_rep = tup[0]
        print(x_rep)
        #move the block horizontally
        moves = dest - x_rep
        if moves < 0:
            moves = -moves
            for i in range(moves):
                move_list.append(Direction.Left)
        else:
            for i in range(moves):
                move_list.append(Direction.Right)
        if not self.apply_moves(movebox, move_list):
            movebox.move(Direction.Drop)
        result = self.evaluate(movebox,num_falling,num_fallen,dest)
        return result
    
    def heights(self,movebox):
        height_list = [0,0,0,0,0,0,0,0,0,0]
        for x in range(movebox.width):
            for y in range(movebox.height):
                if(x,y) in movebox.cells:
                    real_height = movebox.height - y
                    if real_height > height_list[x]:
                        height_list[x] = real_height
        return height_list
    
    def land_height(self,movebox,dest):
        list = self.heights(movebox)
        height = list[dest] 
        return height
    
    def create_binary(self,movebox):
        # inital board
        board_binary = []
        for i in range(24):
            line = []
            for z in range(10):
                line.append(0)
            board_binary.append(line)   
        # write the board
        for x in range(movebox.width):
            for y in range(movebox.height):
                if(x,y) in movebox.cells:
                    board_binary[y][x] = 1
        return board_binary
    
    def col_transations(self,movebox):
        board_binary = self.create_binary(movebox)
        colTran_list = [] 
        for m in range(movebox.height):
            colTran = 0
            for n in range(movebox.width-1):
                if board_binary[m][n] != board_binary[m][n+1]:
                    colTran += 1
            colTran_list.append(colTran)
        return sum(colTran_list)
    
    def row_transitions(self,movebox):
        board_binary = self.create_binary(movebox)
        rowTran_list = []
        for n in range(movebox.width):
            rowTran = 0
            for m in range(movebox.height - 1):
                if board_binary[m][n] != board_binary[m+1][n]:
                    rowTran += 1
            rowTran_list.append(rowTran)
        return sum(rowTran_list)
               
    def find_buried(self,movebox):
        board_binary = self.create_binary(movebox)
        buried_list = [] 
        for n in range(movebox.width):
            holes = None
            for m in range(movebox.height):
                if holes == None and board_binary[m][n] == 1 :
                    holes = 0
                if holes != None and board_binary[m][n] == 0:
                    holes += 1
            if holes != None:
                buried_list.append(holes)
            else:
                buried_list.append(0)
        return sum(buried_list)
            
    def find_wells(self,movebox):
        board_binary = self.create_binary(movebox)
        well_list = [] 
        sum_n = [0,1,3,6,10,15,21,28,36,45,55]
        for n in range(movebox.width):
            well = 0
            sum_col = 0
            for m in range(movebox.height):
                if board_binary[m][n] == 0:
                    if (n-1<0 or board_binary[m][n-1] == 1) and (n+1 >= 10 or board_binary[m][n+1] == 1):
                        sum_col += 1
                    # else:
                        # sum_col += well
                        # sum_n[well]
                        # wells = 0
            well_list.append(sum_col)
        return sum(well_list)
          
    def find_elimination(self,movebox,num_fallen,num_falling):
        num_after = len(movebox.cells)
        lines_cancelled = (num_fallen + num_falling - num_after)/10
        return lines_cancelled
    
    
    def evaluate(self,movebox,num_falling,num_fallen,dest):
        landing_height = self.land_height(movebox,dest)
        colTran_sum = self.col_transations(movebox)
        rowTran_sum = self.row_transitions(movebox)
        hole_sum = self.find_buried(movebox)
        well_sum = self.find_wells(movebox)
        cancelled = self.find_elimination(movebox,num_fallen,num_falling)
        # evaluation
        value = (-4.500158825082766 * landing_height) + 3.4181268101392694 * cancelled - 3.2178882868487753 * rowTran_sum - 9.348695305445199 *colTran_sum - 7.899265427351652 * hole_sum - 3.3855972247263626 * well_sum
        return value
        
    def m_permutations(self,board):
        sandbox = board.clone()
        rotate_list = []
        if sandbox.falling.shape == Shape.I:
            rotate_list = [0,1]  
        elif sandbox.falling.shape == Shape.J:
            rotate_list = [0,1,2,3]
        elif sandbox.falling.shape == Shape.L:
            rotate_list = [0,1,2,3]
        elif sandbox.falling.shape == Shape.O:
            rotate_list = [0]
        elif sandbox.falling.shape == Shape.T:
            rotate_list = [0,1,2,3,4]
        elif sandbox.falling.shape == Shape.S:
            rotate_list = [0,1,2]
        elif sandbox.falling.shape == Shape.Z:
            rotate_list = [0,1,2]
        move_dest_list = [0,1,2,3,4,5,6,7,8,9]
        evaluation_achieved = []
        for rot in rotate_list:
            testbox = sandbox.clone()
            for i in range(rot):
                testbox.rotate(Rotation.Clockwise)
            for dest in move_dest_list:
                movebox = testbox.clone()
                evaluation = self.test_drop(movebox,dest)
                if evaluation == None:
                    return None
                evaluation_achieved.append([rot,dest,evaluation]) 
        evaluation_list = []
        for lst in evaluation_achieved:
            evaluation_list.append(lst[2])  
        evaluation_min = max(evaluation_list)
        for lst in evaluation_achieved:
            if lst[2] == evaluation_min:
                return [lst[0],lst[1]]
            
    def action_list(self,board):
        move = self.m_permutations(board)
        if move == None:
            return None
        final_board = board.clone()
        list_actions = []
        for i in range(move[0]):
            final_board.rotate(Rotation.Clockwise)
            list_actions.append(Rotation.Clockwise)
        x_rep = 10
        for tup in final_board.falling.cells:
            if tup[0] < x_rep:
                x_rep = tup[0]
        moves = move[1] - x_rep
        if moves < 0:
            moves = -moves
            for i in range(moves):
                list_actions.append(Direction.Left)
        else:
            for i in range(moves):
                list_actions.append(Direction.Right)
        list_actions.append(Direction.Drop)
        return list_actions
    
    def choose_action(self, board):
        list_actions = self.action_list(board)
        if list_actions == None:
            return None
        if self.apply_moves(board,list_actions):
            return list_actions
        
        
class RandomPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(seed)

    def choose_action(self, board):
        return self.random.choice([
            Direction.Left,
            Direction.Right,
            Direction.Down,
            Rotation.Anticlockwise,
            Rotation.Clockwise,
        ])


SelectedPlayer = Player
