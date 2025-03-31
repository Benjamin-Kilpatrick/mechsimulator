

# used ---- to split functions for my own view for now, so i know where functions are that were inside of other functions
'''Avoid:
1. Dictionaries (unless necessary)
2. '''
from pint import Quantity


class Reactors:

    @staticmethod
    def st(temperature, pressure, mix, gas, target_species, end_time, p_of_t):

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
    def set_state(gas, temp: Quantity, pressure: Quantity, mix):

        pressure = pressure.to('pascal')

        #TODO: come replace these dict methods once mix is no longer a dict
        if isinstance(mix, dict) and 'fuel' in mix:  # if mix defined using phi
            # Create string for fuel species
            fuel = ''
            fuel_count = len(mix['fuel'])
            for idx in range(fuel_count):
                spc = mix['fuel'][idx]
                if fuel_count > 1:
                    ratio = mix['fuel_ratios'][0][idx]
                    fuel += f'{spc}: {ratio}'
                    if idx + 1 < fuel_count:  # if not on last spc, add a comma
                        fuel += ', '
                else:
                    fuel += spc
            # Create string for oxidizer species
            oxid = ''
            oxid_count = len(mix['oxid'])
            for idx in range(oxid_count):
                spc = mix['oxid'][idx]
                if oxid_count > 1:
                    ratio = mix['oxid_ratios'][0][idx]
                    oxid += f'{spc}: {ratio}'
                    if idx + 1 < oxid_count:  # if not on last spc, add a comma
                        oxid += ', '
                else:
                    oxid += spc

            phi = mix['phi']
            gas.set_equivalence_ratio(phi, fuel, oxid, basis='mole')
            gas.TP = temp, pressure
        else:  # if mix is defined in terms of mole fractions
            gas.TPX = temp, pressure, mix

        return gas

    @staticmethod
    def mix_str(mix, type):
        """Converts a mixture to a string

        mix: mixture description; either in terms of equivalence ratio
        type mix: dict
        type: set to either 'fuel' or 'oxid'
        :return mix_string: Mixture description as a string
        :rtype: str
        """

        # TODO: actually convert this into a string???
        mix_string = '' # begin with empty string
        component_count = len(mix[type]) # number of components
        for i in range(component_count):
            spc = mix[type][i]
            if component_count > 1:
                ratio = 4
        return  mix_string