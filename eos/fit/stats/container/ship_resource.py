# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
#
# This file is part of Eos.
#
# Eos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Eos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Eos. If not, see <http://www.gnu.org/licenses/>.
# ===============================================================================


from eos.util.volatile_cache import InheritableVolatileMixin, volatile_property


class ShipResource(InheritableVolatileMixin):
    """
    Class designed to conveniently provide ship
    resource use and output.
    """

    def __init__(self, fit, resource_use_register, output_attr):
        InheritableVolatileMixin.__init__(self)
        self._fit = fit
        self.__register = resource_use_register
        self.__output_attr = output_attr

    @volatile_property
    def used(self):
        return self.__register.get_resource_use()

    @volatile_property
    def output(self):
        # Get ship's resource output, setting it to None
        # if fitting doesn't have ship assigned,
        # or ship doesn't have resource output attribute
        ship_item = self._fit.ship
        try:
            ship_item_attribs = ship_item.attributes
        except AttributeError:
            return None
        else:
            try:
                return ship_item_attribs[self.__output_attr]
            except KeyError:
                return None
