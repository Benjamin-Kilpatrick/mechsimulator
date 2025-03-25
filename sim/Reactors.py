

# used ---- to split functions for my own view for now, so i know where functions are that were inside of other functions
'''Avoid:
1. Dictionaries (unless necessary)
2. '''
class Reactors:

    @staticmethod
    def st(temp, pressure, mix, gas, targ_spcs, end_time, p_of_t=None):

        raise NotImplementedError

    @staticmethod
    def _wall_velocity(time):
        raise NotImplementedError

    # ---------------

    @staticmethod
    def rcm():
        raise NotImplementedError

    @staticmethod
    def _piston_velocity(time):
        raise NotImplementedError

    # ---------------

    @staticmethod
    def pfr():
        raise NotImplementedError

    # ---------------

    @staticmethod
    def jsr():
        raise NotImplementedError

    # ---------------

    @staticmethod
    def const_t_p():
        raise NotImplementedError

    # ---------------

    @staticmethod
    def free_flame(temp, pressure, mix, gas, targ_spcs, prev_soln=None):
        gas = Reactors.set_state(gas, temp, pressure, mix)

    # ---------------

    @staticmethod
    def burner():
        #TODO: BRO WHAT IS THIS?!?
        pass

    #---------------
    @staticmethod
    def set_state(gas, temp, pressure, mix):
        raise NotImplementedError

    @staticmethod
    def mix_str(mix, type):
        mix_string = '' # begin with empty string
        component