from enum import Enum


class DataSource(Enum):
    """
    The data source parsed by serial.common.utils.parse_datasource
    (plot, plot) -> X_SIM_COND_SIM
    (plot, exp)  -> X_SIM_COND_MEAS
    (exp, exp)   -> X_MEAS_COND_MEAS
    (exp, plot)  -> X_MEAS_COND_SIM
    """
    X_SIM_COND_MEAS = 0
    X_SIM_COND_SIM = 1
    X_MEAS_COND_MEAS = 2
    X_MEAS_COND_SIM = 3

    INVALID = -1
