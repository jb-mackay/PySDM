from PySDM.physics import si
from PySDM.initialisation import spectral_sampling, spectra
from PySDM.physics import formulae as phys
from PySDM.physics import constants as const
from chempy import Substance
import numpy as np
from PySDM.dynamics.aqueous_chemistry.support import AQUEOUS_COMPOUNDS
from pystrict import strict


@strict
class Settings:
    def __init__(self, dt: float, n_sd: int, n_substep: int):
        self.DRY_RHO = 1800 * si.kg / (si.m ** 3)
        self.system_type = 'closed'

        self.t_max = (2400 + 196) * si.s
        self.output_interval = 10 * si.s
        self.dt = dt

        self.w = .5 * si.m/si.s
        self.g = 10 * si.m / si.s**2

        self.n_sd = n_sd
        self.n_substep = n_substep

        self.p0 = 950 * si.mbar
        self.T0 = 285.2 * si.K
        self.pv0 = .95 * phys.pvs(self.T0)

        self.kappa = .61  # TODO #442
        rho = 1  # TODO #442
        self.mass_of_dry_air = 44  # TODO #442

        self.cloud_radius_range = (
                .5 * si.micrometre,
                25 * si.micrometre
        )

        self.r_dry, self.n_in_dv = spectral_sampling.ConstantMultiplicity(
            spectrum=spectra.Lognormal(
                norm_factor=566 / si.cm**3 / rho * self.mass_of_dry_air,
                m_mode=.08 * si.um / 2,
                s_geom=2
            )
        ).sample(n_sd)

        self.ENVIRONMENT_MOLE_FRACTIONS = {
            "SO2": 0.2 * const.ppb,
            "O3": 50 * const.ppb,
            "H2O2": 0.5 * const.ppb,
            "CO2": 360 * const.ppm,
            "HNO3": 0.1 * const.ppb,
            "NH3": 0.1 * const.ppb,
        }

        DRY_SUBSTANCE = Substance.from_formula("NH4HSO4")
        BUM = phys.volume(self.r_dry) * self.DRY_RHO / (DRY_SUBSTANCE.mass * si.gram / si.mole)
        self.starting_amounts = {
            "moles_"+k: BUM if k in ("N_mIII", "S_VI") else np.zeros(self.n_sd) for k in AQUEOUS_COMPOUNDS.keys()
        }

    @property
    def nt(self):
        nt = self.t_max / self.dt
        assert nt == int(nt)
        return int(nt)

    @property
    def steps_per_output_interval(self) -> int:
        return int(self.output_interval / self.dt)
