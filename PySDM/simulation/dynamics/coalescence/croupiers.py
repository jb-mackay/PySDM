"""
Created at 18.12.2019

@author: Piotr Bartman
@author: Sylwester Arabas
"""


def global_FisherYates(particles, cell_start):
    particles.state.unsort()
    particles.state.sort_by_cell_id(cell_start)


def local_FisherYates(particles, cell_start):
    particles.state.sort_by_cell_id(cell_start)
    particles.state.unsort(cell_start)


def global_Shima(particles, cell_start):
    raise NotImplementedError()
