from evo.organism import Organism, LocalWorldState, Action

import random


class World:

    def __init__(self, config: dict) -> None:
        self.config = config
        self.world_width = config.get('world_width')
        self.world_height = config.get('world_height')
        assert self.world_width is not None and self.world_height is not None, \
            'World size not specified'

        self.include_diagonal_cells_in_local_state = \
            config.get('include_diagonal_cells')

        if self.include_diagonal_cells_in_local_state is None:
            raise Exception('include_diagonal_cells not specified in config')

        # Data structures for storing organisms
        self.organisms = []
        self.grid = [[None for _ in range(self.world_width)] for _ in range(self.world_height)]

    @property
    def current_population(self) -> int:
        return len(self.organisms)

    def is_cell_occupied(self, x: int, y: int) -> bool:
        return self.grid[y][x] is not None

    def find_random_empty_cell(self) -> tuple:
        empty_cells = []
        for y in range(self.world_height):
            for x in range(self.world_width):
                if not self.is_cell_occupied(x, y):
                    empty_cells.append((x, y))

        if len(empty_cells) == 0:
            return None

        return random.choice(empty_cells)

    def get_organism_position(self, organism: Organism) -> tuple:
        return organism.local_world_state.x, organism.local_world_state.y

    def set_organism_position(self,
                              organism: Organism,
                              x: int, y: int) -> None:
        self.grid[y][x] = organism

        if organism.local_world_state is not None:
            old_x = organism.local_world_state.x
            old_y = organism.local_world_state.y
            self.grid[old_y][old_x] = None

            organism.local_world_state.x = x
            organism.local_world_state.y = y
        else:
            if self.include_diagonal_cells_in_local_state:
                n_local_cells = 8
            else:
                n_local_cells = 4

            organism.local_world_state = LocalWorldState(
                x=x, y=y,
                local_cells=[None] * n_local_cells,
                world_metadata=self.config
            )

    def add_organism(self, organism: Organism) -> None:
        self.organisms.append(organism)
        x, y = self.find_random_empty_cell()
        self.set_organism_position(organism, x, y)

    def update_local_world_state(self, organism: Organism) -> None:
        """
        Updates the local world state of an organism.
        """
        if self.include_diagonal_cells_in_local_state:
            self._add_locals_including_diagonals(organism)
        else:
            self._add_locals_excluding_diagonals(organism)

    def _add_locals_excluding_diagonals(self, organism: Organism):
        x, y = self.get_organism_position(organism)
        local_cells = organism.local_world_state.local_cells
        local_cells[0] = self.grid[y - 1][x] if y > 0 else None
        local_cells[1] = self.grid[y + 1][x] if y < self.world_height - 1 else None
        local_cells[2] = self.grid[y][x - 1] if x > 0 else None
        local_cells[3] = self.grid[y][x + 1] if x < self.world_width - 1 else None
        return local_cells

    def _add_locals_including_diagonals(self, organism: Organism):
        x, y = self.get_organism_position(organism)
        local_cells = organism.local_world_state.local_cells
        i = 0
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue

                i += 1
                xx = x + dx
                yy = y + dy

                if xx < 0 or xx >= self.world_width or yy < 0 or yy >= self.world_height:
                    local_cells[i] = self.grid[yy][xx]
                else:
                    local_cells[i] = None

    def get_new_pos(self, x: int, y: int, dx: int, dy: int):
        new_x = x + dx
        new_y = y + dy

        if new_x < 0:
            new_x = 0
        elif new_x >= self.world_width:
            new_x = self.world_width - 1

        if new_y < 0:
            new_y = 0
        elif new_y >= self.world_height:
            new_y = self.world_height - 1

        return new_x, new_y

    def update_organism(self, organism: Organism) -> None:
        action = organism.get_action()
        dx, dy = Action.to_tuple(action)
        curr_x, curr_y = self.get_organism_position(organism)
        new_x, new_y = self.get_new_pos(curr_x, curr_y, dx, dy)
        if self.is_cell_occupied(new_x, new_y):
            return
        self.set_organism_position(organism, new_x, new_y)

    def reset(self) -> None:
        for y in range(self.world_height):
            for x in range(self.world_width):
                self.grid[y][x] = None

        random.shuffle(self.organisms)
        for organism in self.organisms:
            x, y = self.find_random_empty_cell()
            self.set_organism_position(organism, x, y)

    def update(self) -> None:
        random.shuffle(self.organisms)
        for organism in self.organisms:
            self.update_local_world_state(organism)
            self.update_organism(organism)

    def kill_organism(self, organism: Organism) -> None:
        self.organisms.remove(organism)
        x, y = self.get_organism_position(organism)
        self.grid[y][x] = None
