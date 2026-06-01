"""Zone derivation library for special-locations skill.

Computes BS 7671:2018+A2:2022 Part 7 zone polygons + height bounds from
anchor fixtures. Reference implementation; runtime project hosts the executor.

Verified against shared/standards/electrical/BS7671/part7-special-locations.json
(verification_status: verified-against-source).
"""

__version__ = "1.0.0"
__all__ = ["common", "bath", "pool", "sauna", "medical", "elv"]

from . import bath, common, elv, medical, pool, sauna
