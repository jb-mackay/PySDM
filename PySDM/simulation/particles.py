"""
Created at 09.11.2019

@author: Piotr Bartman
@author: Sylwester Arabas
"""

import numpy as np
from PySDM.simulation.physics import formulae as phys
from PySDM.simulation.state.state import State
from PySDM.simulation.state.state_factory import StateFactory
from PySDM.simulation.stats import Stats
from PySDM.simulation.initialisation.r_wet_init import r_wet_init
from PySDM.simulation.mesh import Mesh


class Particles:

    def __init__(self, n_sd, dt, backend, stats=Stats()):
        self.__n_sd = n_sd
        self.__dt = dt
        self.backend = backend
        self.mesh = None
        self.environment = None
        self.state: (State, None) = None
        self.dynamics: list = []
        self.__dv = None
        self.n_steps = 0
        self.stats = stats

    @property
    def n_sd(self) -> int:
        return self.__n_sd

    @property
    def dt(self) -> float:
        return self.__dt

    def set_mesh(self, grid, size):
        assert_none(self.mesh)
        self.mesh = Mesh(grid, size)

    def set_mesh_0d(self, dv=None):
        assert_none(self.mesh)
        self.mesh = Mesh.mesh_0d(dv)

    def set_environment(self, environment_class, params: dict):
        assert_not_none(self.mesh)
        assert_none(self.environment)
        self.environment = environment_class(self, **params)

    def add_dynamic(self, dynamic_class, params: dict):
        self.dynamics.append(dynamic_class(self, **params))

    def create_state_0d(self, n, extensive, intensive):
        assert_not_none(self.mesh)
        assert_none(self.state)
        self.state = StateFactory.state_0d(n, extensive, intensive, self)

    def create_state_2d(self, extensive, intensive, spatial_discretisation, spectral_discretisation,
                        spectrum_per_mass_of_dry_air, r_range, kappa):
        assert_not_none(self.mesh, self.environment)
        assert_none(self.state)

        with np.errstate(all='raise'):
            positions = spatial_discretisation(self.mesh.grid, self.n_sd)

            r_dry, n_per_kg = spectral_discretisation(
                self.n_sd, spectrum_per_mass_of_dry_air, r_range
            )
            # TODO: cell_id, _, _ = StateFactory.positions(n_per_kg, positions)

            cell_origin = positions.astype(dtype=int)
            cell_id = np.dot(self.mesh.strides, cell_origin.T).ravel()
            # </TEMP>

            # TODO: not here
            n_per_m3 = n_per_kg * self.environment["rhod"][cell_id]
            domain_volume = np.prod(np.array(self.mesh.size))
            n = (n_per_m3 * domain_volume).astype(np.int64)
            r_wet = r_wet_init(r_dry, self.environment, cell_id, kappa)

        extensive['volume'] = phys.volume(radius=r_wet)
        extensive['dry volume'] = phys.volume(radius=r_dry)

        self.state = StateFactory.state_2d(n, intensive, extensive, positions, self)

    def run(self, steps):
        with self.stats:
            for _ in range(steps):
                for dynamic in self.dynamics:
                    dynamic()
                self.environment.post_step()
        self.n_steps += steps


# TODO: move somewhere
def assert_none(*params):
    for param in params:
        if param is not None:
            raise AssertionError(str(param.__class__.__name__) + " is already initialized.")


def assert_not_none(*params):
    for param in params:
        if param is None:
            raise AssertionError(str(param.__class__.__name__) + " is not initialized.")
