from board import Direction, Rotation, Shape
from random import Random
import statistics


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
        for (x,y) in movebox.falling.cells:
            if x < x_rep:
                x_rep = x
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
        result = self.find_lowest(movebox,num_falling,num_fallen,dest)
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
    
    def mean_height(self,movebox):
        list = self.heights(movebox)
        return sum(list)/len(list)
    
    def std_height(self,movebox):
        list = self.heights(movebox)
        return statistics.stdev(list)
    
    def max_height(self,movebox):
        list = self.heights(movebox)
        return max(list)
    
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
        return sum(buried_list)
            
    def find_wells(self,movebox):
        board_binary = self.create_binary(movebox)
        well_list = [] 
        sum_n = [0,1,3,6,10,15,21,28,36,45,55]
        for m in range(movebox.height):
            well = 0
            sum_col = 0
            for n in range(movebox.width):
                if board_binary[m][n] == 0:
                    if (n-1<0 or board_binary[m][n-1] == 1) and (n+1 >= 10 or board_binary[m][n+1] == 1):
                        well += 1
                    else:
                        sum_col += sum_n[well]
                        wells = 0
            well_list.append(sum_col)
        return sum(well_list)
    
    def row_count(self,movebox):
        board_binary = self.create_binary(movebox)
        count_list = []
        for m in range(1,24):
            count = 0
            for n in range(10):
                if board_binary[m][n] == 0 and board_binary[m-1][n] == 1:
                    count += 1
            count_list.append(count)
        nonzero = 0
        for x in count_list:
            if x != 0:
                nonzero+=1
        return nonzero
    
    def hole_depth(self,movebox):
        board_binary = self.create_binary(movebox)
        count = 0
        for m in range(1,24):
            for n in range(10):
                if board_binary[m][n] == 0 and board_binary[m-1][n] == 1:
                    count += m
        return count
                 
    def find_elimination(self,movebox,num_fallen,num_falling):
        num_after = len(movebox.cells)
        lines_cancelled = (num_fallen + num_falling - num_after)/10
        eroded = lines_cancelled
        return eroded
    
    def find_lowest(self,movebox,num_falling,num_fallen,dest):
        max_height = self.max_height(movebox)
        mean_height = self.mean_height(movebox)
        stdiv_height = self.std_height(movebox)
        landing_height = self.land_height(movebox,dest)
        colTran_sum = self.col_transations(movebox)
        rowTran_sum = self.row_transitions(movebox)
        hole_sum = self.find_buried(movebox)
        buried_row = self.row_count(movebox)
        well_sum = self.find_wells(movebox)
        eroded = self.find_elimination(movebox,num_fallen,num_falling)
        holedep = self.hole_depth(movebox)
        # evaluation
        # value = (-1 * landing_height) + 1 * eroded - 1 * rowTran_sum - 1 *colTran_sum - 4 * buried_sum - 1 * well_sum
        # value = (-4.500158825082766 * landing_height) + 3.4181268101392694 * eroded - 3.2178882868487753 * rowTran_sum - 9.348695305445199 *colTran_sum - 7.899265427351652 * buried_sum - 3.3855972247263626 * well_sum
        # value = (-0.35 * landing_height) + 0.19 * eroded - 0.25 * rowTran_sum - 0.7 *colTran_sum - 0.54 * buried_sum - 0.25 * well_sum
        # value = (-0.32 * landing_height) + 0.07 * eroded - 0.28 * rowTran_sum - 0.6 *colTran_sum - 0.24 * buried_sum - 0.27 * well_sum - 0.08*holedep - 0.55*buried_row
        # value_list = [landing_height,eroded,rowTran_sum,colTran_sum,buried_sum,well_sum,holedep,buried_row]
        # weight_list = [-0.32,0.07,-0.28,-0.6,-0.24,-0.27,-0.08,-0.55]
        # value_list = [value_list[i]*weight_list[i] for i in range(len(value_list))]
        # value = sum(value_list)

        value = - hole_sum - stdiv_height - max_height
        # else:
        #     value_list = [stdiv_height,hole_sum]
        #     weight_list = [-10,-2]
        #     value_list = [value_list[i]*weight_list[i] for i in range(len(value_list))]
        #     value = sum(value_list)
        if eroded !=0:
            value = 1000
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
        height_achieved = []
        for rot in rotate_list:
            testbox = sandbox.clone()
            for i in range(rot):
                testbox.rotate(Rotation.Clockwise)
            for dest in move_dest_list:
                movebox = testbox.clone()
                height = self.test_drop(movebox,dest)
                if height == None:
                    return None
                height_achieved.append([rot,dest,height]) 
        height_list = []
        for lst in height_achieved:
            height_list.append(lst[2])  
        height_min = max(height_list)
        for lst in height_achieved:
            if lst[2] == height_min:
                return [lst[0],lst[1]]
        
    def choose_action(self, board):
        move = self.m_permutations(board)
        print(move)
        if move == None:
            return None
        #implement
        list_actions = []
        for i in range(move[0]):
            list_actions.append(Rotation.Clockwise)
        x_rep = 10
        for (x,y) in board.falling.cells:
            if x < x_rep:
                x_rep = x
        moves = move[1] - x_rep
        if moves < 0:
            moves = -moves
            for i in range(moves):
                list_actions.append(Direction.Left)
        else:
            for i in range(moves):
                list_actions.append(Direction.Right)
        list_actions.append(Direction.Drop)
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
