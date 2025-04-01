import cantera
import numpy as np
from scipy.interpolate import RegularGridInterpolator
import cantera as ct

# used ---- to split functions for my own view for now, so i know where functions are that were inside of other functions
'''Avoid:
1. Dictionaries (unless necessary)
2. '''
from typing import List

from pint import Quantity

from data.mixtures.compound import Compound


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

        # initialize the data from Cantera
        gas = Reactors.set_state(gas, temp, pressure, mix)
        loglevel = 0 # TODO-t:what is the purpose of supressing output here?
        flame: cantera.FreeFlame = ct.FreeFlame(gas) # cantera returns a result here from this input
        flame.transport_model = 'Mix'
        if prev_soln is not None:
            flame.set_profile('T', prev_soln[0, :], prev_soln[1, :])
        # Run a simulation
        try:
            flame.solve(loglevel=loglevel, auto=True)
        except ct._cantera.CanteraError as ct_error:
            print(f"Free flame solver failed at {temp} K, {pressure} atm, mix: "
                  f"{mix}. The error was:\n{ct_error}")
            
        # Concentration target retrival
        num_points = np.shape(flame.X)[1]  # length of second dim is num_points
        targ_concs = np.ndarray((len(targ_spcs), num_points))

        for targ_idx, targ_spc in enumerate(targ_spcs):
            if targ_spc in gas.species_names:
                targ_concs[targ_idx] = flame.solution(targ_spc)
            else:  # if the targ_spc isn't in the mechanism
                targ_concs[targ_idx] = np.nan # todo-t: ???

        # Get other results
        pos = flame.grid
        vels = flame.velocity
        temps = flame.T
        rop = None  # not sure what to do here
        end_gas = None  # will develop later

        return targ_concs, pos, vels, temps, rop, end_gas

    # ---------------

    @staticmethod
    def burner():
        #TODO-t: BRO WHAT IS THIS?!?
        pass

    #---------------
    @staticmethod
    def set_state(gas, temp: Quantity, pressure: Quantity, mix):

        pressure = pressure.to('pascal')
        """ come replace these dict methods once mix is no longer a dict
        if isinstance(mix, List) and ('fuel' in mix):
            fuel = ''
            fuel_count = len(mix['fuel'])"""
        # issue, this new type of mix that has fuel and other stuff is so different we can't use it here.
        # TODO-t: come back when you know what mix is
        if isinstance(mix, dict) and 'fuel' in mix:  # If there is a mixture defined using phi
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