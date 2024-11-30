from AI import AI
from Action import Action
from collections import deque
import random

class MyAI(AI):
    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
        self.theirPos = (startX, startY)  # THEIRS
        self.totalMines = totalMines
        self.numRows = rowDimension
        self.numCols = colDimension

        self.visited = set()  #their pos      
        self.flaggedMines = set() #flagged mines
        self.safeQueue = deque() #0 mines adjacent

        self.matrix = self.initializeBoard()  
        self.lastAction = "uncover" #because of first move

        self.moveCount = 0

    def getAction(self, number: int):
        #print(f"Move Count: {self.moveCount}")
        self.moveCount += 1

        if self.lastAction == "uncover":  
            self.matrix[self.numRows - self.theirPos[1] - 1][self.theirPos[0]] = number
            self.visited.add(self.theirPos)
        
        #for row in self.matrix: #prints my matrix (debugging purposes) 
        #    print(row)

        validAdj = self.getHidden(self.theirPos[0], self.theirPos[1])

        # Helps us out in the future
        if number == 0: #safeQueue
            for tile in validAdj:
                if tile not in self.safeQueue: #Added based on their Pos
                    self.safeQueue.append(tile)

        #print(f"Visited tiles: {self.visited}")   
        #print(f"Safe Queue: {self.safeQueue}")
        #print(f"Flagged: {self.flaggedMines}")
        
        for tile in self.visited: #updates gameboard accurately (from TAS)
            numHidden = len(self.getHidden(tile[0], tile[1]))
            numFlags = len(self.adjacentFlags(tile[0],tile[1]))
            currentTileNum = self.getTileNumber(tile[0], tile[1])
            if (numHidden + numFlags) == currentTileNum: #should be at that tile
                for unsafe in self.getHidden(tile[0],tile[1]):
                    self.matrix[self.numRows - unsafe[1] - 1][unsafe[0]] = '?'
                    self.flaggedMines.add(unsafe)
                    #print(f"Case 0: Bomb at {unsafe} since {numHidden} + {numFlags} is {currentTileNum} at {tile}")
                    self.theirPos = unsafe
                    return Action(AI.Action.FLAG, unsafe[0], unsafe[1]) #should keep flagging until safe
            elif numFlags == currentTileNum:
                for safeTile in self.getHidden(tile[0],tile[1]):
                     if safeTile not in self.safeQueue:
                          self.safeQueue.append(safeTile)

        
        # 3 OPTIONS TO PICK NEXT TILE (theirPos)
        if validAdj and number == 0:
            nextTile = random.choice(validAdj)
            self.theirPos = nextTile

            if nextTile in self.safeQueue:
                self.safeQueue.remove(nextTile)
            #print(f"Case 1: Picking nonbomb adjacent: {self.theirPos}")

            self.lastAction = "uncover"
            return Action(AI.Action.UNCOVER, nextTile[0], nextTile[1])

        elif self.safeQueue:
            # Use next safe tile from the queue if no adjacent unvisited tiles
            nextTile = self.safeQueue.popleft()
            self.theirPos = nextTile
            #print(f"Case 2: Uncovering from safe queue: {self.theirPos}")
            
            # Remove the nextTile from safeQueue if it is there
            if nextTile in self.safeQueue:
                self.safeQueue.remove(nextTile)

            self.lastAction = "uncover"
            return Action(AI.Action.UNCOVER, nextTile[0], nextTile[1])
        
        unvisited_tiles = [
        (x, y) for x in range(self.numCols)
        for y in range(self.numRows)
        if (x, y) not in self.visited and (x, y) not in self.flaggedMines]

        if unvisited_tiles:
            random_tile = random.choice(unvisited_tiles)
            self.theirPos = random_tile
            #print(f"Case 3: No safe moves; picking random tile: {self.theirPos}")

            self.lastAction = "uncover"
            return Action(AI.Action.UNCOVER, random_tile[0], random_tile[1])

        #print("No valid moves remaining. Leaving game.")
        return Action(AI.Action.LEAVE)

    def getHidden(self, x_coord, y_coord): #returns a list of unvisited adjacent tiles
        adjacentTiles = []
        for x in range(-1, 2):  # -1, 0, 1
            for y in range(-1, 2):
                if x == 0 and y == 0:
                    continue
                adj_x, adj_y = x_coord + x, y_coord + y
                if (0 <= adj_x < self.numRows and 0 <= adj_y < self.numCols 
                    and self.matrix[self.numRows - adj_y - 1][adj_x] == -2 and (adj_x, adj_y) not in self.visited and (adj_x, adj_y) not in self.flaggedMines): #for my matrix must use diff system
                    adjacentTiles.append((adj_x, adj_y))
        return adjacentTiles
    
    def adjacentFlags(self, x_coord, y_coord): #returns a list of adjacent flags
        adjacentFlags = []
        for x in range(-1, 2):  # -1, 0, 1
            for y in range(-1, 2):
                if x == 0 and y == 0:
                    continue
                adj_x, adj_y = x_coord + x, y_coord + y
                if (0 <= self.numRows - adj_y - 1 < self.numRows and 0 <= adj_x < self.numCols 
                    and self.matrix[self.numRows - adj_y - 1][adj_x] != -2 and (adj_x, adj_y) in self.flaggedMines):
                    adjacentFlags.append((adj_x, adj_y))
        return adjacentFlags

    def getTileNumber(self, x, y):
        # Ensure the tile is within the bounds of the board
        if 0 <= x < self.numCols and 0 <= y < self.numRows:
            # Return the number at that tile
            return self.matrix[self.numRows - y - 1][x]
        else:
            # Return None or another indicator if the tile is out of bounds
            return None

    def initializeBoard(self):
        # Initialize the board with -2 (covered tiles)
        return [[-2 for _ in range(self.numCols)] for _ in range(self.numRows)]
