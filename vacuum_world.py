# libraries
import random
import json


# actions
CLEAN = 'clean'
UP    = 'up'
DOWN  = 'down'
LEFT  = 'left'
RIGHT = 'right'


# environment
class World:

    def __init__(self, rows:int, columns:int) -> None:
        # attributes
        self.layout = list()
        # counters
        self.rooms_dirty = 0
        # initialize environment
        for _ in range(rows):
            temp = list()
            for _ in range(columns):
                dirty = random.randint(0, 1)
                temp.append(dirty)
                self.rooms_dirty += 1 if dirty else 0
            self.layout.append(temp)


# vacuum cleaner
class Agent:

    def __init__(self, x_position:int, y_position:int, rows:int, columns:int, rooms_dirty:int, layout:list) -> None:
        # attributes
        self.x_position    = x_position
        self.y_position    = y_position
        self.world_rows    = rows
        self.world_columns = columns
        self.world_layout  = [list(item) for item in layout]
        self.visited       = set()
        # counters
        self.score         = 0
        self.rooms_visited = 0
        self.rooms_cleaned = 0
        self.rooms_dirty   = rooms_dirty
        # initial room
        self.visited.add((self.x_position, self.y_position))

    def possible_steps(self) -> list:
        # potential movements
        allowed = list()
        # verification
        if self.world_layout[self.y_position][self.x_position]:
            allowed.append(CLEAN)
        if self.y_position-1 >= 0:
            allowed.append(UP)
        if self.y_position+1 < self.world_rows:
            allowed.append(DOWN)
        if self.x_position-1 >= 0:
            allowed.append(LEFT)
        if self.x_position+1 < self.world_columns:
            allowed.append(RIGHT)
        # return potential movements
        return allowed

    def perform_action(self, action:str) -> None:
        # act
        if action == CLEAN:
            self.world_layout[self.y_position][self.x_position] = 0
            self.score         += 10
            self.rooms_cleaned += 1
        elif action == UP:
            self.y_position    -= 1
            self.score         -= 1
            self.rooms_visited += 1
        elif action == DOWN:
            self.y_position    += 1
            self.score         -= 1
            self.rooms_visited += 1
        elif action == LEFT:
            self.x_position    -= 1
            self.score         -= 1
            self.rooms_visited += 1
        elif action == RIGHT:
            self.x_position    += 1
            self.score         -= 1
            self.rooms_visited += 1
        # save room
        self.visited.add((self.x_position, self.y_position))


# simple vacuum cleaner
class SimpleAgent(Agent):

    def clean_world(self, index:int) -> dict:
        # record information
        summary   = dict()
        iteration = 0
        # initial information
        summary['Attempt']          = index
        summary['Initial position'] = [self.x_position, self.y_position]
        summary['Initial layout']   = [list(item) for item in self.world_layout]
        summary['Process']          = dict()
        # clean environment
        while self.rooms_cleaned != self.rooms_dirty:
            # backup position
            x_temp = self.x_position
            y_temp = self.y_position
            # action
            allowed_steps = self.possible_steps()
            next_step = CLEAN if CLEAN in allowed_steps else random.choice(allowed_steps)
            self.perform_action(next_step)
            # record action
            if next_step == CLEAN:
                record_action = 'clean at ('+str(self.x_position)+', '+str(self.y_position)+')'
            else:
                record_action = '('+str(x_temp)+', '+str(y_temp)+') to ('+str(self.x_position)+', '+str(self.y_position)+')'
            iteration += 1
            summary['Process'][iteration] = record_action
        # final information
        summary['Final position'] = [self.x_position, self.y_position]
        summary['Final layout']   = [list(item) for item in self.world_layout]
        summary['Rooms total']    = self.world_rows * self.world_columns
        summary['Rooms visited']  = self.rooms_visited
        summary['Rooms cleaned']  = self.rooms_cleaned
        summary['Rooms dirty']    = self.rooms_dirty
        summary['Score local']    = self.score
        # return information
        return summary


# state vacuum cleaner
class StateAgent(Agent):

    def clean_world(self, index:int) -> dict:
        # record information
        summary   = dict()
        iteration = 0
        # initial information
        summary['Attempt']          = index
        summary['Initial position'] = [self.x_position, self.y_position]
        summary['Initial layout']   = [list(item) for item in self.world_layout]
        summary['Process']          = dict()
        # clean environment
        while self.rooms_cleaned != self.rooms_dirty:
            # backup position
            x_temp = self.x_position
            y_temp = self.y_position
            # action
            allowed_steps = self.possible_steps()
            next_step = CLEAN if CLEAN in allowed_steps else random.choice(self.best_steps(allowed_steps))
            self.perform_action(next_step)
            # record action
            if next_step == CLEAN:
                record_action = 'clean at ('+str(self.x_position)+', '+str(self.y_position)+')'
            else:
                record_action = '('+str(x_temp)+', '+str(y_temp)+') to ('+str(self.x_position)+', '+str(self.y_position)+')'
            iteration += 1
            summary['Process'][iteration] = record_action
        # final information
        summary['Final position'] = [self.x_position, self.y_position]
        summary['Final layout']   = [list(item) for item in self.world_layout]
        summary['Rooms total']    = self.world_rows * self.world_columns
        summary['Rooms visited']  = self.rooms_visited
        summary['Rooms cleaned']  = self.rooms_cleaned
        summary['Rooms dirty']    = self.rooms_dirty
        summary['Score local']    = self.score
        # return information
        return summary

    def best_steps(self, allowed_steps:list) -> list:
        # potential movements
        allowed_unvisited = list()
        allowed_dirty     = list()
        # verification
        if UP in allowed_steps and (self.x_position, self.y_position-1) not in self.visited:
            allowed_unvisited.append(UP)
            if self.world_layout[self.y_position-1][self.x_position]:
                allowed_dirty.append(UP)
        if DOWN in allowed_steps and (self.x_position, self.y_position+1) not in self.visited:
            allowed_unvisited.append(DOWN)
            if self.world_layout[self.y_position+1][self.x_position]:
                allowed_dirty.append(DOWN)
        if LEFT in allowed_steps and (self.x_position-1, self.y_position) not in self.visited:
            allowed_unvisited.append(LEFT)
            if self.world_layout[self.y_position][self.x_position-1]:
                allowed_dirty.append(LEFT)
        if RIGHT in allowed_steps and (self.x_position+1, self.y_position) not in self.visited:
            allowed_unvisited.append(RIGHT)
            if self.world_layout[self.y_position][self.x_position+1]:
                allowed_dirty.append(RIGHT)
        # return potential movements
        if len(allowed_dirty) > 0:
            return allowed_dirty
        elif len(allowed_unvisited) > 0:
            return allowed_unvisited
        else:
            return allowed_steps


# main
def main() -> None:

    # read information
    try:
        with open('constants.json', 'r') as file:
            data = json.load(file)
    except Exception as error:
        print(error)
        return

    # save information
    ATTEMPTS  = data['attempts']
    ROWS      = data['world_rows']
    COLUMNS   = data['world_columns']
    X_INITIAL = data['x_initial']
    Y_INITIAL = data['y_initial']

    # create environment
    world       = World(ROWS, COLUMNS)
    rooms_dirty = world.rooms_dirty
    layout      = [list(item) for item in world.layout]

    # test agents
    score_global = 0
    data_sample  = list()
    for attempt in range(ATTEMPTS):
        vacuum  = SimpleAgent(X_INITIAL, Y_INITIAL, ROWS, COLUMNS, rooms_dirty, layout)
        vacuum  = StateAgent(X_INITIAL, Y_INITIAL, ROWS, COLUMNS, rooms_dirty, layout)
        summary = vacuum.clean_world(attempt+1)
        score_global += summary['Score local']
        data_sample.append(summary)
    data_sample.append({'Score global': score_global/ATTEMPTS})

    # save information
    try:
        with open('summary.json', 'w') as file:
            json.dump(data_sample, file, indent=4)
    except Exception as error:
        print(error)
        return


# run main
if __name__ == '__main__':
    main()