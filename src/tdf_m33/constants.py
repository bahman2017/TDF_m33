"""Physical and numerical constants for TDF-M33."""

# Gravitational constant: kpc (km/s)^2 / M_sun (astronomical units)
G_KPC: float = 4.30091e-6

# Surface density: M_sun pc^-2 to M_sun kpc^-2
MSUN_PC2_TO_MSUN_KPC2: float = 1.0e6

# Corbelli et al. 2014 Sect. 2.2 — helium multiplier on HI + H2
CORBELLI2014_HELIUM_FACTOR: float = 1.33

# Corbelli et al. 2014 Sect. 2.2 — molecular gas surface density (M_sun pc^-2)
CORBELLI2014_SIGMA_H2_NORM: float = 10.0
CORBELLI2014_SIGMA_H2_SCALE_KPC: float = 2.2

# Sect. 6 vertical structure (kpc)
CORBELLI2014_GAS_HALF_THICKNESS_KPC: float = 0.5
CORBELLI2014_STELLAR_HZ_CENTER_KPC: float = 0.1
CORBELLI2014_STELLAR_HZ_OUTER_KPC: float = 1.0
CORBELLI2014_STELLAR_HZ_REF_RADIUS_KPC: float = 23.0

# Package-level sentinel for unconfigured TDF coupling (see configs/m33_default.yaml)
K_TAU_PLACEHOLDER: float | None = None
