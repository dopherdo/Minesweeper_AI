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
        
        self.hasCoveredAdjacents = set()
        
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
            
            #address hasCoveredAdjacents
            if numHidden == 0 and tile in self.hasCoveredAdjacents:
                self.hasCoveredAdjacents.remove(tile)
                
            if numHidden > 0 and tile not in self.hasCoveredAdjacents:
                self.hasCoveredAdjacents.add(tile)
            
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
        
        pattern_action = self.patternCheck()
        if pattern_action:
            # print(f"ONE-ONE HAS BEEN DONE")
            return pattern_action
            
        # Random algorithm
        unvisited_tiles = [
            (x, y) for x in range(self.numCols)
            for y in range(self.numRows)
            if (x, y) not in self.visited and (x, y) not in self.flaggedMines
        ]
        
        if unvisited_tiles:
            random_tile = random.choice(unvisited_tiles)
            self.theirPos = random_tile
            #print(f"Case 3: No safe moves; picking random tile: {self.theirPos}")

            self.lastAction = "uncover"
            # print(f"RANDOM CHOICE: {random_tile[0]}, {random_tile[1]}")
            return Action(AI.Action.UNCOVER, random_tile[0], random_tile[1])

        
        
    
        return Action(AI.Action.LEAVE)

    def patternCheck(self):
        '''
        Checks for patterns and performs the corresponding action
        Return: None
        '''
        oneOne =  self.oneOne()
        if oneOne:
            return oneOne
        oneTwo =  self.oneTwo()
        if oneTwo:
            return oneTwo
        
        return None
    
    def oneOne(self):
        '''
        Checks for 1-1 pattern
        WILL ADD: 1-1+ pattern
        '''
        # 1-1 Pattern: Precise Definitive Mine Location
        for (x1, y1) in self.hasCoveredAdjacents:
            # Ensure first position is a 1
            if self.getTileNumber(x1, y1) - len(self.adjacentFlags(x1, y1)) != 1:
                continue
                        
            # Get hidden neighbors for first position
            hidden1 = set(self.getHidden(x1, y1))
            
            # Wall check for hidden1
            if len(hidden1) != 2:
                continue
            
            # Only check adjacent 1's
            for (x2, y2) in [(x1-1, y1), (x1+1, y1), (x1, y1-1), (x1, y1+1)]:
                
                # Skip if this adjacent position is not in hasCoveredAdjacents
                if (x2, y2) not in self.hasCoveredAdjacents:
                    continue
                
                # Ensure adjacent position is also a 1
                if self.getTileNumber(x2, y2) - len(self.adjacentFlags(x2, y2)) != 1:
                    continue
                
                # Get hidden neighbors for second position
                hidden2 = set(self.getHidden(x2, y2))
                
                # Shared hidden tiles between the two 1 positions
                shared_hidden = hidden1.intersection(hidden2)
                
                # Check if the share is exactly two tiles
                if len(shared_hidden) == 2:
                    # This means checking ALL tiles around both 1-positions
                    all_hidden_context = set()
                    for (check_x, check_y) in [(x1, y1), (x2, y2)]:
                        # Get ALL hidden around this position
                        all_around = set(self.getHidden(check_x, check_y))
                        all_hidden_context.update(all_around)
                    
                    # If shared_hidden is the ONLY possible mine location
                    if shared_hidden == all_hidden_context.intersection(shared_hidden):
                        # Unique tiles not in the shared area
                        unique1 = hidden1 - shared_hidden
                        unique2 = hidden2 - shared_hidden
                        
                        # Safe tile is the unique tile
                        if unique1 or unique2:
                            safe_tile = unique1.pop() if unique1 else unique2.pop()
                            self.theirPos = safe_tile
                            self.lastAction = "uncover"
                            return Action(AI.Action.UNCOVER, safe_tile[0], safe_tile[1])
        return None

    
    def oneTwo(self):
        for (x1, y1) in self.hasCoveredAdjacents:
            # Ensure the first tile is a "1" (after accounting for flags)
            # print(f"Adjacent flags: {self.adjacentFlags(x1, y1)}")
            if self.getTileNumber(x1, y1) - len(self.adjacentFlags(x1, y1)) != 1:
                continue

            # Get hidden neighbors for the "1" tile
            hidden1 = set(self.getHidden(x1, y1))

            # Ensure the "1" has exactly 2 hidden neighbors
            if len(hidden1) != 2:
                continue

            # Look for neighboring "2" tiles
            for (x2, y2) in [(x1-1, y1), (x1+1, y1), (x1, y1-1), (x1, y1+1)]:
                # Skip if this neighbor is not in hasCoveredAdjacents
                if (x2, y2) not in self.hasCoveredAdjacents:
                    continue

                # Ensure the second tile is a "2" (after accounting for flags)
                # print(f"Adjacent flags 2: {self.adjacentFlags(x2, y2)}")

                # print(f"Flagged Mines: {self.flaggedMines}")
                if self.getTileNumber(x2, y2) - len(self.adjacentFlags(x2, y2)) != 2:
                    continue

                # Get hidden neighbors for the "2" tile
                hidden2 = set(self.getHidden(x2, y2))

                # Find shared and unique tiles
                shared_hidden = hidden1.intersection(hidden2)
                unique_hidden = hidden2 - shared_hidden

                # Ensure shared tiles are exactly 2 and there's 1 unique tile for the "2"
                if len(shared_hidden) == 2 and len(unique_hidden) == 1:
                    # Flag the unique tile as a mine
                    mine_tile = unique_hidden.pop()
                    self.theirPos = mine_tile
                    self.lastAction = "flag"
                    # print(f"ONE-TWO PATTERN: Flagging {mine_tile[0]}, {mine_tile[1]}")
                    self.matrix[self.numRows - mine_tile[1] - 1][mine_tile[0]] = '?'
                    self.flaggedMines.add(mine_tile)
                    return Action(AI.Action.FLAG, mine_tile[0], mine_tile[1])

                    
        return None

        
    
    def getHidden(self, x_coord, y_coord): #returns a list of unvisited adjacent tiles
        adjacentTiles = []
        for x in range(-1, 2):  # -1, 0, 1
            for y in range(-1, 2):
                if x == 0 and y == 0:
                    continue
                adj_x, adj_y = x_coord + x, y_coord + y
                if (0 <= self.numRows - adj_y - 1 < self.numRows and 0 <= adj_x < self.numCols 
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
