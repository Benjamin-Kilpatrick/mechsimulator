from typing import Dict

import pint


class UnitParser:
    """
    Static helper class to parse units
    """
    _ureg = pint.UnitRegistry()
    UNIT_LOOKUP: Dict[str, Dict[str, pint.Quantity]] = {
        'temperature': {
            'K': _ureg.Quantity(1, 'kelvin'),
            'C': _ureg.Quantity(1, 'celsius'),
            'F': _ureg.Quantity(1, 'fahrenheit'),
            'R': _ureg.Quantity(1, 'rankine'),
        },
        'pressure': {
            'atm': _ureg.Quantity(1, 'standard_atmosphere'),
            'bar': _ureg.Quantity(1, 'bar'),
            'Pa': _ureg.Quantity(1, 'pascal'),
            'kPa': _ureg.Quantity(1e3, 'pascal'),
            'MPa': _ureg.Quantity(1e6, 'pascal'),
            'torr': _ureg.Quantity(1, 'torr')
        },
        'time': {
            's': _ureg.Quantity(1, 'second'),
            'ms': _ureg.Quantity(1, 'ms'),
            'micros': _ureg.Quantity(1e-6, 'microsecond'),
        },
        'concentration': {
            'ppm': _ureg.Quantity(1,'ppm'),
            '%': _ureg.Quantity(1,'%'),
            'molec/cm3': _ureg.Quantity(1, 'mole/cm^3')
        },
        'length': {
            'm': _ureg.Quantity(1, 'meter'),
            'cm': _ureg.Quantity(1, 'centimeter'),
            'mm': _ureg.Quantity(1, 'millimeter')
        },
        'area': {
            'm2': _ureg.Quantity(1, 'm^2'),
            'cm2': _ureg.Quantity(1, 'cm^2'),
            'mm2': _ureg.Quantity(1, 'mm^2')
        },
        'volume': {
            'm3': _ureg.Quantity(1, 'm^3'),
            'cm3': _ureg.Quantity(1, 'cm^3'),
            'mm3': _ureg.Quantity(1, 'mm^3'),
        },
        'absorption_coefficient': {
            # TODO: figure out these units
        },
        'absorption': {
            '%': _ureg.Quantity(1, '%'),
            'fraction': _ureg.Quantity(1, '')
        },
        'dP/dt': {
            '%/ms': _ureg.Quantity(1, '%/ms')
        },
        'mdot': {
            'kg/s': _ureg.Quantity(1, 'kg/s'),
            'g/s': _ureg.Quantity(1, 'g/s')
        },
        'velocity': {
            'm/s': _ureg.Quantity(1, 'm/s'),
            'cm/s': _ureg.Quantity(1, 'cm/s')
        },
        'phi': {
            '': _ureg.Quantity(1, '')
        },
        'other': {
            'X': _ureg.Quantity(1, '')
        }
    }

    @classmethod
    def parse(cls, category: str, value: float, units: str) -> pint.Quantity:
        """
        Convert a value in a specific category given the units
        :param category: category to check for conversion
        :param value: the value, scalar or array
        :param units: the units to convert to
        :return: a pint quantity, scalar or array
        """
        if value is None:
            return None
        if category not in cls.UNIT_LOOKUP:
            raise Exception(f'Category {category} not implemented')
        if units not in cls.UNIT_LOOKUP[category]:
            raise Exception(f'Failed to parse {category}:{units}')
        return value * cls.UNIT_LOOKUP[category][units]

    @classmethod
    def parse_all(cls, value: float, units: str) -> pint.Quantity:
        """
        Convert a value with no category given the units
        :param value: the value, scalar or array
        :param units: the units to convert to
        :return: a pint quantity, scalar or array
        """
        if value is None:
            return None
        category: str
        for category in cls.UNIT_LOOKUP.keys():
            if units in cls.UNIT_LOOKUP[category]:
                return value * cls.UNIT_LOOKUP[category][units]
        raise Exception(f'Failed to parse {units}')
