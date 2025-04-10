import cantera
import numpy as np
from scipy.interpolate import RegularGridInterpolator
import cantera as Cantera
from typing import List
from pint import Quantity
from data.mixtures.compound import Compound

# used ---- to split functions for my own view for now, so i know where functions are that were inside of other functions



class Reactors:

    @staticmethod
    def st(temperature, pressure, mix, gas, targ_species, end_time, pres_vs_time=None):
        """
        Will run a shock tube simulation. The non-ideal pressure rise, dP/dt, and can be incorporated via an optional P(t) profile
        
        :param temperature: 
        :param pressure: 
        :param mix: 
        :param gas: 
        :param targ_species: 
        :param end_time: 
        :param pres_vs_time: 
        :return: 
        """
        gas = Reactors.set_state(gas, temperature, pressure, mix)

        if pres_vs_time is None:
            # Create an array of ones spanning from t=0 to t=end_time
            velocity_vs_time = np.array([[0, end_time], [1, 1]])
        else:
            # Convert P(t) to V(t) assuming isentropic behavior
            gamma = gas.cp_mass / gas.cv_mass  # specific heat ratio
            velocity_vs_time = np.zeros_like(pres_vs_time)
            velocity_vs_time[0, :] = pres_vs_time[0, :]  # time values are the same
            velocity_vs_time[1, :] = (pres_vs_time[1, :] / pres_vs_time[1, 0]) ** (-1 / gamma)
    
        reaction = Cantera.IdealGasReactor(gas)
        reaction.volume = 1 # m^3 (default value, but here for clarity)
        env = Cantera.Reservoir(gas)
        wall = Cantera.Wall(env, reaction)
        wall.area = 1  # m^2 (default value, but here for clarity)
        wall.heat_transfer_coeff = 0  # no heat transfer considerations for ST
        def wall_velocity(temp_time):
            """ Gets the wall velocity at some time based on velocity_vs_time

                :param temp_time: individual time value (s)
                :type temp_time: float
                :return vel: velocity of the wall (m/s)
                :rtype: float
            """
            dvdt = np.gradient(velocity_vs_time[1, :], velocity_vs_time[0, :])
            dxdt = dvdt / wall.area  # only for clarity (since A = 1 m^2)
            vel = np.interp(temp_time, velocity_vs_time[0, :], -1 * dxdt)

            return vel
        wall.set_velocity(wall_velocity)
        network = Cantera.ReactorNet([reaction])

        # Run the simulation
        time = 0
        states = Cantera.SolutionArray(gas, extra=['t'])
        states.append(reaction.thermo.state, t=time)
        while time < np.min([end_time, velocity_vs_time[0, -1]]):
            time = network.step()
            states.append(reaction.thermo.state, t=time)

        # Get results
        times = states.t
        pressures = states.P
        temps = states.T
        targ_concs = np.zeros((len(targ_species), len(times)))
        for ndx, targ_spc in enumerate(targ_species):
            if targ_spc is not None:
                targ_concs[ndx, :] = states.X[:, gas.species_index(targ_spc)]
            else:
                targ_concs[ndx, :] = np.nan

        rop = None  # will develop later...
        end_gas = gas

        # todo-t: change to Object return
        return targ_concs, pressures, temps, times, rop, end_gas

    # ---------------

    @staticmethod
    def rcm(temp, pressure, mix: Compound, gas, targ_spcs, end_time, velocity_vs_time):
        gas = Reactors.set_state(gas, temp, pressure, mix)

        print('inside reactions, rcm temp: ', temp)
        # Normalize the volume profile by the first value
        velocity_vs_time[1, :] = velocity_vs_time[1, :] / velocity_vs_time[1, 0]

        # Set up reactor, piston, and network
        reaction = Cantera.IdealGasReactor(gas)
        reaction.volume = 1  # m^3
        env = Cantera.Reservoir(gas)
        piston = Cantera.Wall(env, reaction)
        piston.area = 1  # m^2 (this is the default, but put here for clarity)
        piston.heat_transfer_coeff = 0  # instead, considering heat trans. w/volume

        @staticmethod
        def piston_velocity(temp_time):
            dvdt = np.gradient(velocity_vs_time[1, :], velocity_vs_time[0, :])
            dxdt = dvdt / piston.area  # only for clarity (since area = 1 m^2)
            vel = np.interp(temp_time, velocity_vs_time[0, :], -1 * dxdt)
            return vel
        
        piston.set_velocity(piston_velocity)
        network = Cantera.ReactorNet([reaction])
        # network.set_max_time_step(np.max(np.diff(velocity_vs_time[0, :])))

        # Run the simulation
        time = 0
        states = Cantera.SolutionArray(gas, extra=['t'])
        states.append(reaction.thermo.state, t=time)
        while time < np.min([end_time, velocity_vs_time[0, -1]]):
            time = network.step()
            states.append(reaction.thermo.state, t=time)

        # Get results
        times = states.t
        pressures = states.P
        targ_concs = np.zeros((len(targ_spcs), len(times)))
        for idx, targ_spc in enumerate(targ_spcs):
            targ_concs[idx, :] = states.X[:, gas.species_index(targ_spc)]
        end_gas = gas
        rop = None  # temporary

        return targ_concs, pressures, times, rop, end_gas
            

    # ---------------

    @staticmethod
    def pfr(temp: Quantity, pressure: Quantity, mix, gas, targ_species, mdot, area, length,res_time=None, n_steps=2000, x_profile=None, t_profile=None, t_profile_setpoints=None):
        # Set the initial gas state
        if x_profile is not None:  # use T profile if given
            # Create the 2D array
            t_data = np.ndarray((len(x_profile[0]), len(t_profile_setpoints)))
            for ndx, array in enumerate(t_profile):
                t_data[:, ndx] = array
            # Create the interp object and interp (note: the [0] gets rid of uncertainties)
            interp = RegularGridInterpolator((x_profile[0], t_profile_setpoints), t_data)
            start_temp = interp((0, temp))
            gas = Reactors.set_state(gas, start_temp, pressure, mix)
        else:  # otherwise, just use the given, fixed T
            gas = Reactors.set_state(gas, temp, pressure, mix)

        # Create reactor and reactor network
        reac = Cantera.IdealGasConstPressureReactor(gas)
        network = Cantera.ReactorNet([reac])

        # Approximate a time step
        density, _ = gas.DP  # kg/m^3
        if res_time is not None:  # if res_time was given instead of mdot
            mdot = (density * area * length) / res_time  # kg/s
        inlet_velocity = mdot / (density * area)  # m/s
        dt = (length / inlet_velocity) / n_steps  # s

    # ---------------

    @staticmethod
    def jsr(temp: Quantity, pressure: Quantity, mix, gas, targ_spcs, res_time, vol, prev_concs=None, mdot=None, max_iter=30000):

        # Note: must set gas with mix before creating reservoirs!
        gas = Reactors.set_state(gas, temp, pressure, mix)
        inlet = Cantera.Reservoir(gas)
        exhaust = Cantera.Reservoir(gas)

        # Create reactor, using prev_concs to speed up convergence
        prev_concs_input = True # todo-t: use compound?
        if prev_concs is None:
            prev_concs_input = False
            prev_concs = mix
        gas = Reactors.set_state(gas, temp, pressure, prev_concs)
        reac = Cantera.IdealGasReactor(gas, energy='off', volume=vol)

        # Set up devices
        pressure_valve_coeff = 0.01  # "conductance" of the pressure valve
        Cantera.Valve(upstream=reac, downstream=exhaust, K=pressure_valve_coeff)
        if res_time is not None:  # MFC condition depends on inputs
            Cantera.MassFlowController(upstream=inlet, downstream=reac,
                                  mdot=reac.mass / res_time)
        elif mdot is not None:
            Cantera.MassFlowController(upstream=inlet, downstream=reac, mdot=mdot)

        # Create reactor network (only the JSR in this case) and advance it to SS
        reac_net = Cantera.ReactorNet([reac])
        failure = False
        try:
            reac_net.advance_to_steady_state(max_steps=max_iter)
            all_concs = reac.thermo.X  # store output concentrations
        except Cantera._cantera.CanteraError as ct_error:
            failure = True
            print(f"JSR solver failed at {temp} K for mechanism {gas.name}. The "
                  f"error was:\n{ct_error}")
            # If no initial guess, set results to None for next iteration
            if prev_concs_input is False:
                all_concs = None
            # If an initial guess was input, return it for use in the next iteration
            else:
                all_concs = prev_concs

        # Get results for target species
        targ_concs = np.zeros(len(targ_spcs))
        for targ_ndx, targ_spc in enumerate(targ_spcs):
            if failure:
                targ_concs[targ_ndx] = None
            else:
                if targ_spc in gas.species_names:
                    targ_concs[targ_ndx] = all_concs[gas.species_index(targ_spc)]
                else:  # if the targ_spc isn't in the mechanism
                    targ_concs[targ_ndx] = None
        end_gas = gas
        rop = None

        return targ_concs, all_concs, rop, end_gas

    # ---------------

    @staticmethod
    def const_t_p(temp: Quantity, pressure:Quantity, mix, gas, targ_spcs, end_time):
        gas = Reactors.set_state(gas, temp, pressure, mix)

        # Setting energy to 'off' holds T constant
        reac = Cantera.IdealGasConstPressureReactor(gas, energy='off') # todo-t: the reaction? or reactor? same for rest of file, i.e. other functions
        network = Cantera.ReactorNet([reac])

        # Run the simulation
        time = 0
        states = Cantera.SolutionArray(gas, extra=['t'])
        states.append(reac.thermo.state, t=time)
        while time < end_time:
            time = network.step() # todo-t: does this decrement?
            states.append(reac.thermo.state, t=time)

        # Get results
        times = states.t
        pressures = states.P
        temps = states.T
        targ_concs = np.zeros((len(targ_spcs), len(times)))

        for targ_ndx, targ_spc in enumerate(targ_spcs):
            if targ_spc is not None:
                targ_concs[targ_ndx, :] = states.X[:, gas.species_index(targ_spc)]
            else:
                targ_concs[targ_ndx, :] = np.nan

        rop = None  # will develop later... ???
        end_gas = gas

        return targ_concs, pressures, temps, times, rop, end_gas

    # ---------------

    @staticmethod
    def free_flame(temp, pressure, mix, gas, targ_spcs, prev_soln=None):

        # initialize the data from Cantera
        gas = Reactors.set_state(gas, temp, pressure, mix)
        loglevel = 0 # TODO-t:what is the purpose of supressing output here?
        flame: cantera.FreeFlame = Cantera.FreeFlame(gas) # cantera returns a result here from this input
        flame.transport_model = 'Mix'
        if prev_soln is not None:
            flame.set_profile('T', prev_soln[0, :], prev_soln[1, :])
        # Run a simulation
        try:
            flame.solve(loglevel=loglevel, auto=True)
        except Cantera._cantera.CanteraError as ct_error:
            print(f"Free flame solver failed at {temp} K, {pressure} atm, mix: "
                  f"{mix}. The error was:\n{ct_error}")
            
        # Concentration target retrival
        num_points = np.shape(flame.X)[1]  # length of second dim is num_points
        targ_concs = np.ndarray((len(targ_spcs), num_points))

        for targ_ndx, targ_spc in enumerate(targ_spcs):
            if targ_spc in gas.species_names:
                targ_concs[targ_ndx] = flame.solution(targ_spc)
            else:  # if the targ_spc isn't in the mechanism
                targ_concs[targ_ndx] = np.nan # todo-t: ???

        # Get other results
        pos = flame.grid
        vels = flame.velocity
        temps = flame.T
        rop = None  # not sure what to do here
        end_gas = None  # will develop later

        return targ_concs, pos, vels, temps, rop, end_gas

    # ---------------
    @staticmethod
    def set_state(gas, temp: Quantity, pressure: Quantity, mix: Compound):
        #todo-t: do last after prev mix fixes
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
            for i in range(fuel_count):
                spc = mix['fuel'][i]
                if fuel_count > 1:
                    ratio = mix['fuel_ratios'][0][i]
                    fuel += f'{spc}: {ratio}'
                    if i + 1 < fuel_count:  # if not on last spc, add a comma
                        fuel += ', '
                else:
                    fuel += spc
            # Create string for oxidizer species
            oxid = ''
            oxid_count = len(mix['oxid'])
            for i in range(oxid_count):
                spc = mix['oxid'][i]
                if oxid_count > 1:
                    ratio = mix['oxid_ratios'][0][i]
                    oxid += f'{spc}: {ratio}'
                    if i + 1 < oxid_count:  # if not on last spc, add a comma
                        oxid += ', '
                else:
                    oxid += spc

            phi = mix['phi']
            gas.set_equivalence_ratio(phi, fuel, oxid, basis='mole')
            gas.TP = temp, pressure
        else:  # if mix is defined in terms of mole fractions
            gas.TPX = temp, pressure, mix

        return gas
