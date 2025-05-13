from typing import Dict

import cantera
import numpy as np
from scipy.interpolate import RegularGridInterpolator
import cantera as Cantera
from pint import Quantity

from data.experiments.mixture import Mixture
from data.experiments.mixture_type import MixtureType
from sim.SimulatorUtils import SimulatorUtils



class Reactors:

    @staticmethod
    def st(temp: Quantity, pressure: Quantity, mix, gas, targ_species, end_time, press_of_time=None):
        """
        Will run a shock tube simulation. The non-ideal pressure rise, dP/dt, and can be incorporated via an optional P(t) profile
        
        :param temp: the experiments condition temperature
        :param pressure: the experiments condition temperature
        :param mix: dict of mixture type and mixture list, initial species concentrations at reactor inlet initial
            species concentrations at reactor inlet
        :param gas: The Cantera mechanism object
        :param targ_species: a list of target species
        :param end_time: float, end time for the simulation, will end at the first of either this time or the max time in press_of_time
        :param press_of_time: numpy array of specified pressure vs time, set to None if no non-ideal effects are simulated.
        :return:
            1. targ_concs - the target concentrations
            2. pressures - Solution pressures
            3. temps - Solution temperatures
            4. times - Solution times
        """
        gas = Reactors.set_gas_state(gas, temp, pressure, mix)

        if press_of_time is None:
            # Create an array of ones spanning from t=0 to t=end_time
            velocity_of_time = np.array([[0, end_time], [1, 1]])
        else:
            # Convert P(t) to V(t) assuming isentropic behavior
            gamma = gas.cp_mass / gas.cv_mass  # specific heat ratio
            velocity_of_time = np.zeros_like(press_of_time)
            velocity_of_time[0, :] = press_of_time[0, :]  # time values are the same
            velocity_of_time[1, :] = (press_of_time[1, :] / press_of_time[1, 0]) ** (-1 / gamma)
    
        reaction = Cantera.IdealGasReactor(gas)
        reaction.volume = 1 # m^3 (default value, but here for clarity)
        env = Cantera.Reservoir(gas)
        wall = Cantera.Wall(env, reaction)
        wall.area = 1  # m^2 (default value, but here for clarity)
        wall.heat_transfer_coeff = 0  # no heat transfer considerations for ST

        def wall_velocity(temp_time):
            """ Gets the wall velocity at some time based on velocity_of_time

                :param temp_time: individual time value (s)
                :type temp_time: float
                :return vel: velocity of the wall (m/s)
            """
            dvdt = np.gradient(velocity_of_time[1, :], velocity_of_time[0, :])
            dxdt = dvdt / wall.area  # only for clarity (since A = 1 m^2)
            vel = np.interp(temp_time, velocity_of_time[0, :], -1 * dxdt)
            return vel

        wall.set_velocity(wall_velocity)
        network = Cantera.ReactorNet([reaction])

        # Run the simulation
        time = 0
        states = Cantera.SolutionArray(gas, extra=['t'])
        states.append(reaction.thermo.state, t=time)
        while time < np.min([end_time.magnitude, velocity_of_time[0, -1]]):
            time = network.step()
            states.append(reaction.thermo.state, t=time)

        # Get results
        times = states.t
        pressures = states.P
        temps = states.T
        targ_concs = np.zeros((len(targ_species), len(times)))
        for ndx, targ_spc in enumerate(targ_species):
            if targ_spc is not None:
                targ_concs[ndx, :] = states.X[:, gas.species_index(targ_spc.name)]
            else:
                targ_concs[ndx, :] = np.nan

        return targ_concs, pressures, temps, times

    # ---------------

    @staticmethod
    def rcm(temp: Quantity, pressure: Quantity, mix, gas, targ_species, end_time, velocity_of_time):
        """
        Runs a rapid compression machine simulation, with compression and heat
        loss incorporated via an input V(t) profile

        :param temp: reactor inlet temperature, pre-configured to kelvin via pint
        :param pressure: reactor constant pressure, pre-configured to atm via pint
        :param mix: dict of mixture type and mixture list, initial species concentrations at reactor inlet initial
            species concentrations at reactor inlet
        :param gas: Cantera object describing a kinetic gas (mechanism)
        :param targ_species: desired species concentrations
        :param end_time: the ending time for the simulation (seconds)
        :param velocity_of_time: specified volume (any units) vs time (s) profile
            to account for both piston compression and heat loss
        :return:
            1. targ_concs - the target concentrations
            2. pressures - Solution pressures
            3. times - Solution times
        """
        gas = Reactors.set_gas_state(gas, temp, pressure, mix)

        print('inside reactions, rcm temp: ', temp)
        # Normalize the volume profile by the first value
        velocity_of_time[1, :] = velocity_of_time[1, :] / velocity_of_time[1, 0]

        # Set up reactor, piston, and network
        reaction = Cantera.IdealGasReactor(gas)
        reaction.volume = 1  # m^3
        env = Cantera.Reservoir(gas)
        piston = Cantera.Wall(env, reaction)
        piston.area = 1  # m^2 (this is the default, but put here for clarity)
        piston.heat_transfer_coeff = 0  # instead, considering heat trans. w/volume

        @staticmethod
        def piston_velocity(temp_time):
            """ Gets the piston velocity at some time based on v_of_t

            :param time: individual time value (s)
            :return vel: velocity of the piston (m/s)
            """
            dvdt = np.gradient(velocity_of_time[1, :], velocity_of_time[0, :])
            dxdt = dvdt / piston.area  # only for clarity (since area = 1 m^2)
            vel = np.interp(temp_time, velocity_of_time[0, :], -1 * dxdt)
            return vel
        piston.set_velocity(piston_velocity)
        network = Cantera.ReactorNet([reaction])

        # Run the simulation
        time = 0
        states = Cantera.SolutionArray(gas, extra=['t'])
        states.append(reaction.thermo.state, t=time)
        while time < np.min([end_time, velocity_of_time[0, -1]]):
            time = network.step()
            states.append(reaction.thermo.state, t=time)

        # Get results
        times = states.t
        pressures = states.P
        temps = states.T
        targ_concs = np.zeros((len(targ_species), len(times)))
        for ndx, targ_spc in enumerate(targ_species):
            targ_concs[ndx, :] = states.X[:, gas.species_index(targ_spc)]

        return targ_concs, pressures, times
            

    # ---------------
    @staticmethod
    def pfr(temp: Quantity, pressure: Quantity, mix, gas, targ_species, mdot, area, length, res_time=None, n_steps=2000, x_profile=None, t_profile=None, t_profile_setpoints=None):
        """
        
        :param temp: reactor inlet temperature, pre-configured to kelvin via pint
        :param pressure: reactor constant pressure, pre-configured to atm via pint
        :param mix: dict of mixture type and mixture list, initial species concentrations at reactor inlet initial
            species concentrations at reactor inlet
        :param gas: Cantera object describing a kinetic gas (mechanism)
        :param targ_species: desired species concentrations
        :param mdot: reactor mass flow rate (kg/s)
        :param area: reactor cross-sectional area (m^2)
        :param length: reactor length (m)
        :param res_time: reactor residence time (s), only given if mdot is None
        :param n_steps:  approx. number of steps to take; used to guess timestep (note: will almost NEVER be the actual 
            number of timesteps taken)
        :param x_profile: array of the x_data
        :param t_profile: array of the temperatures
        :param t_profile_setpoints: array of points, not too sure what this is
        :return:
            1. targ_concs - the target concentrations
            2. pressures - Solution pressures
            3. temps - Solution temperatures
            4. times - Solution times
        """
        # Set the initial gas state
        if x_profile is not None:  # use T profile if given
            # Create the 2D array
            t_data = np.ndarray((len(x_profile), len(t_profile_setpoints)))
            for ndx, array in enumerate(t_profile):
                t_data[:, ndx] = array
            # Create the interp object and interp (note: the [0] gets rid of uncertainties)
            interp = RegularGridInterpolator((x_profile, t_profile_setpoints), t_data)
            start_temp = interp((0, temp))
            gas = Reactors.set_gas_state(gas, start_temp, pressure, mix)
        else:  # otherwise, just use the given, fixed T
            gas = Reactors.set_gas_state(gas, temp, pressure, mix)

        # Create reactor and reactor network
        reac = Cantera.IdealGasConstPressureReactor(gas)
        network = Cantera.ReactorNet([reac])
        
        # Approximate a time step
        density, _ = gas.DP  # kg/m^3
        if res_time is not None:  # if res_time was given instead of mdot
            mdot = (density * area * length) / res_time  # kg/s
        inlet_velocity = mdot / (density * area)  # m/s
        dt = (length / inlet_velocity) / n_steps  # s

        # Initialize time, position, velocity, and thermo states
        times = (np.arange(n_steps * 2) + 1) * dt  # longer than needed to be safe
        positions = np.zeros_like(times)
        velocities = np.zeros_like(times)
        states = cantera.SolutionArray(reac.thermo)

        # Loop over each timestep
        end_ndx = len(times) - 1  # defining as backup; should be overwritten
        for ndx, time in enumerate(times):
            network.advance(time)  # perform time integration
            velocities[ndx] = mdot / area / reac.thermo.density
            positions[ndx] = positions[ndx - 1] + velocities[ndx] * dt  # transform
            states.append(reac.thermo.state)

            # If the reactor length has been exceeded, exit the for loop
            if positions[ndx] >= length:
                end_ndx = ndx
                break

            # If a T profile was given, update the temperature
            if t_profile is not None:
                new_temp = interp((positions[ndx], temp))  # use *given* T to get profile
                thermo = reac.thermo
                thermo.TPX = new_temp, thermo.TPX[1], thermo.TPX[2]
                reac.insert(thermo)
                network.reinitialize()

        # Removed unused entries in time and position
        times = times[:(end_ndx + 1)]
        positions = positions[:(end_ndx + 1)]

        # Get results for target species
        targ_concs = np.full((len(targ_species), end_ndx + 1), np.nan)
        for ndx, targ_spc in enumerate(targ_species):
            if targ_spc is not None:
                targ_concs[ndx, :] = states.X[:, gas.species_index(targ_spc)]

        end_gas = gas

        return targ_concs, times, positions, end_gas
    # ---------------

    @staticmethod
    def jsr(temp: Quantity, pressure: Quantity, mix, gas, targ_species, res_time, vol, mdot=None, previous_concentrations=None):
        """
        Runs a jet-stirred reactor simulation
        :param temp: reactor inlet temperature, pre-configured to kelvin via pint
        :param pressure: reactor constant pressure
        :param mix: dict of mixture type and mixture list, initial species concentrations at reactor inlet initial
            species concentrations at reactor inlet
        :param gas: Cantera object describing a kinetic gas (mechanism)
        :param targ_species: desired species concentrations
        :param res_time: reactor residence time (s)
        :param vol: volume of the reactor (m^3)
        :param mdot: reactor mass flow rate (kg/s)
        :param previous_concentrations: species concentrations from previous solution at a similar condition
        :return:
            1. targ_concs - the target concentrations
            2. all_concs - all species concentrations from the previous solution
            3. end_gas - the gas originally passed in
        """
        max_iter = 30000

        # Note: must set gas with mix before creating reservoirs!
        gas = Reactors.set_gas_state(gas, temp, pressure, mix)
        inlet = Cantera.Reservoir(gas)
        exhaust = Cantera.Reservoir(gas)

        # Create reactor, using previous_concentrations to speed up convergence
        previous_concentrations_input = True
        if previous_concentrations is None:
            previous_concentrations_input = False
            previous_concentrations = mix
        gas = Reactors.set_gas_state(gas, temp, pressure, previous_concentrations)
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
            if previous_concentrations_input is False:
                all_concs = None
            # If an initial guess was input, return it for use in the next iteration
            else:
                all_concs = previous_concentrations

        # Get results for target species
        targ_concs = np.zeros(len(targ_species))
        for targ_ndx, targ_spc in enumerate(targ_species):
            if failure:
                targ_concs[targ_ndx] = None
            else:
                if targ_spc in gas.species_names:
                    targ_concs[targ_ndx] = all_concs[gas.species_index(targ_spc)]
                else:  # if the targ_spc isn't in the mechanism
                    targ_concs[targ_ndx] = None
        end_gas = gas

        return targ_concs, all_concs, end_gas

    # ---------------

    @staticmethod
    def const_t_p(temp: Quantity, pressure: Quantity, mix: Dict[MixtureType, Mixture], gas, targ_species, end_time):
        """
        Runs a constant-temperature, constant-pressure 0-D simulation

        :param temp: reactor inlet temperature, pre-configured to kelvin via pint
        :param pressure: reactor constant pressure, pre-configured to atm via pint
        :param mix: dict of mixture type and mixture list, initial species concentrations at reactor inlet initial species concentrations at reactor inlet
        :param gas: Cantera object describing a kinetic gas (mechanism)
        :param targ_species: desired species concentrations
        :param end_time: the ending time for the simulation (seconds)
        :return:
            1. targ_concs - the target concentrations
            2. pressures - Solution pressures
            3. temps - Solution temperatures
            4. times - Solution times
            5. end_gas - the gas originally passed in
        """
        gas = Reactors.set_gas_state(gas, temp, pressure, mix)

        # Setting energy to 'off' holds T constant
        reac = Cantera.IdealGasConstPressureReactor(gas, energy='off')
        network = Cantera.ReactorNet([reac])

        # Run the simulation
        time = 0
        states = Cantera.SolutionArray(gas, extra=['t'])
        states.append(reac.thermo.state, t=time)
        while time < end_time:
            time = network.step()
            states.append(reac.thermo.state, t=time)

        # Get results
        times = states.t
        pressures = states.P
        temps = states.T
        targ_concs = np.zeros((len(targ_species), len(times)))

        for targ_ndx, targ_spc in enumerate(targ_species):
            if targ_spc is not None:
                targ_concs[targ_ndx, :] = states.X[:, gas.species_index(targ_spc)]
            else:
                targ_concs[targ_ndx, :] = np.nan

        end_gas = gas

        return targ_concs, pressures, temps, times, end_gas

    # ---------------

    @staticmethod
    def free_flame(temp: Quantity, pressure: Quantity, mix: Dict[MixtureType, Mixture], gas, targ_species, phi, previous_solution=None):
        """
        Runs an adiabatic, 1-D, freely propagating flame simulation

        :param temp: reactor inlet temperature, pre-configured to kelvin via pint
        :param pressure: reactor constant pressure, pre-configured to atm via pint
        :param mix: dict of mixture type and mixture list, initial species concentrations at reactor inlet initial species concentrations at reactor inlet
        :param gas: Cantera object describing a kinetic gas (mechanism)
        :param targ_species: desired species concentrations
        :param previous_solution: temperature profile vs. position; first column is position, second is temperature
        :param phi: ratio of the actual fuel-to-oxidizer ratio to the stoichiometric fuel-to-oxidizer ratio.

        :return:
            1. targ_concs - the target concentrations
            2. pos - array of grid positions (m)
            3. vels - gas velocities at each position (m/s)
            4. temps - gas temperatures at each position (K)
        """

        # initialize the data from Cantera
        gas = Reactors.set_fuel_state(gas, temp, pressure, mix, phi)
        loglevel = 0
        flame: cantera.FreeFlame = Cantera.FreeFlame(gas) # cantera returns a result here from this input
        flame.transport_model = 'Mix'
        if previous_solution is not None:
            flame.set_profile('T', previous_solution[0, :], previous_solution[1, :])
        # Run a simulation
        try:
            flame.solve(loglevel=loglevel, auto=True)
        except Cantera._cantera.CanteraError as ct_error:
            print(f"Free flame solver failed at {temp} K, {pressure} atm, mix: "
                  f"{mix}. The error was:\n{ct_error}")
            
        # Concentration target retrival
        num_points = np.shape(flame.X)[1]  # length of second dim is num_points
        targ_concs = np.ndarray((len(targ_species), num_points))

        for targ_ndx, targ_spc in enumerate(targ_species):
            if targ_spc in gas.species_names:
                targ_concs[targ_ndx] = flame.solution(targ_spc)
            else:  # if the targ_spc isn't in the mechanism
                targ_concs[targ_ndx] = np.nan

        # Get other results
        pos = flame.grid
        vels = flame.velocity
        temps = flame.T

        return targ_concs, pos, vels, temps

    @staticmethod
    def set_gas_state(gas, temp: Quantity, pressure: Quantity, mix: Dict[MixtureType, Mixture]):
        """
        Sets a gas mixture to a desired thermodynamic state

        :param gas: Cantera object describing a kinetic gas (mechanism)
        :param temp: reactor inlet temperature, pre-configured to kelvin via pint
        :param pressure: reactor constant pressure, pre-configured to atm via pint
        :param mix: dict of mixture type and mixture list, initial species concentrations at reactor inlet initial species concentrations at reactor inlet
        :return gas: Cantera Solution object
        """
        new_mix = SimulatorUtils.convert_gas_mixture(mix[MixtureType.GAS_MIXTURE])
        gas.TPX = temp.magnitude, pressure.magnitude, new_mix
        return gas

    @staticmethod
    def set_fuel_state(gas: cantera.Solution, temp: Quantity, pressure: Quantity, mix: Dict[MixtureType, Mixture], phi):
        """
        Sets fuel and oxidizer mixtures to a desired thermodynamic state

        :param gas: Cantera object describing a kinetic gas (mechanism)
        :param temp: reactor inlet temperature, pre-configured to kelvin via pint
        :param pressure: reactor constant pressure, pre-configured to atm via pint
        :param mix: dict of mixture type and mixture list, initial species concentrations at reactor inlet initial species concentrations at reactor inlet
        :param phi: ratio of the actual fuel-to-oxidizer ratio to the stoichiometric fuel-to-oxidizer ratio.
        :return Cantera Solution object
        """

        fuel, oxid = SimulatorUtils.convert_fuel_mixture(mix[MixtureType.FUEL_MIXTURE], mix[MixtureType.OXIDIZER_MIXTURE])
        gas.set_equivalence_ratio(phi, fuel, oxid, basis='mole')
        gas.TP = temp, pressure
        return gas
