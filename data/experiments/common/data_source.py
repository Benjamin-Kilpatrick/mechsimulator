from enum import Enum


class DataSource(Enum):
    X_SIM_COND_MEAS = 0
    X_SIM_COND_SIM = 1
    X_MEAS_COND_MEAS = 2
    X_MEAS_COND_SIM = 3

    INVALID = -1
