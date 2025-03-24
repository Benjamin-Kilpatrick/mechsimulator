from sim import outcome


def single_mech(conds_dct, gas, reac_type, ydata_shape):
    """

        :param conds_dct:
        :param gas:
        :param reac_type:
        :return:
    """

    mech_end_tpx = outcome.single_mech(
        conds_dct, gas, reac_type, 'pathways', None, ydata_shape)

    return mech_end_tpx
