import random as rn

from evo.world import World
from evo.world_gen.world_generator import WorldGenerator
from evo.util.registry import register_world_gen


RockArray = list[list[bool]]


def get_state(dimensions, array: RockArray, x, y, r1_cutoff, r2_cutoff, wall_radius) -> bool:
    '''
    Get state for a cave pixel.
    :param array: cave pixels;
    :param x: x coordinate of current pixel;
    :param y: y coordinate of current pixel;
    :param r1_cutoff: r1 parameter;
    :param r2_cutoff: r2 parameter;
    :param wall_radius: a certain radius that if is less ;
    than pixel's distance from centre will force the pixel to be rock.
    :return: Pixel's state.
    '''
    # print((x - dimensions / 2) ** 2 + (y - dimensions / 2) ** 2, wall_radius ** 2)
    if wall_radius != -1 and (x - dimensions / 2) ** 2 + (y - dimensions / 2) ** 2 > wall_radius ** 2:
        return True
    return (count_neighbours(array, 1, x, y) >= r1_cutoff != -1) or \
        (count_neighbours(array, 2, x, y) <= r2_cutoff != -1) or (array[y][x] and r1_cutoff == -1 and r1_cutoff == -1)


def count_neighbours(array: RockArray, distance: float, x: int, y: int) -> int:
    '''
    Count rocks around in a certain radius.
    :param array: cave pixels;
    :param distance: radius in which to search for rocks
    :param x: x coordinate of current pixel;
    :param y: y coordinate of current pixel;
    :return: amount of rocks in proximity
    '''
    round_dist = round(distance)
    return sum(
        array[_y][_x]
        for _y in range(max(y - round_dist, 0), min(y + round_dist + 1, len(array)))
        for _x in range(max(x - round_dist, 0), min(x + round_dist + 1, len(array[_y])))
    )


def generate_caves(dimensions: int, fillprob: float = .4, r1_cutoff=5, r2_cutoff=2, include_wall=True) -> RockArray:

    rock_map: RockArray = [
        [rn.random() < fillprob for _ in range(dimensions)]
        for _ in range(dimensions)
    ]

    for x in range(dimensions):
        for y in range(dimensions):
            rock_map[y][x] = get_state(dimensions, rock_map, x, y, r1_cutoff, r2_cutoff, -1)

    for x in range(dimensions):
        for y in range(dimensions):
            rock_map[y][x] = get_state(dimensions, rock_map, x, y, r1_cutoff, -1, -1)

    if include_wall:
        for x in range(dimensions):
            for y in range(dimensions):
                rock_map[y][x] = get_state(dimensions, rock_map, x, y, -1, -1, dimensions / 2 - 2)

        # Make the edges walls
        rock_map[0] = [True for _ in range(dimensions)]
        rock_map[-1] = [True for _ in range(dimensions)]
        for i in range(dimensions):
            rock_map[i][0] = True
            rock_map[i][-1] = True

    return rock_map


class Barrier:
    pass


@register_world_gen('forgiven_caves')
class ForgivenCavesWorldGen(WorldGenerator):
    """
    Generates a world with procedurally generated "cave"-like barriers.
    Cave generation code written by the user Forgiven on discord.
    """

    def __init__(self, global_config: dict, generator_name: str) -> None:
        super().__init__(global_config, generator_name)
        self.world_width = self.global_config.get('world_width')
        self.world_height = self.global_config.get('world_height')
        self.fillprob = self.config.get('fillprob', .4)
        self.r1_cutoff = self.config.get('r1_cutoff', 5)
        self.r2_cutoff = self.config.get('r2_cutoff', 2)
        self.include_wall = self.config.get('include_wall', True)

    def generate(self, world: World):
        rock_map = generate_caves(self.world_width,
                                  self.fillprob,
                                  self.r1_cutoff,
                                  self.r2_cutoff,
                                  self.include_wall)
        for x in range(self.world_width):
            for y in range(self.world_height):
                if rock_map[y][x]:
                    world.set_cell(x, y, Barrier())
