from density_max_based_v1 import DensMaxShockFinderV1
from constant_velocity_v1 import ConstVelShockFinderV1
from not_impl_shock import ShockFindingNotImpl

_shock_finders = {
    'density_max_v1': DensMaxShockFinderV1,
    'constant_vel_v1': ConstVelShockFinderV1,
    'not_implemented': ShockFindingNotImpl,
}
