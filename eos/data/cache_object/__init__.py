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


"""
Classes in this module are objects stored in cache. Eos' objects like holders
are built on top of their instances, and often they're reused, thus make sure
to not store any fit-specific data on them.
"""


__all__ = [
    'Attribute',
    'Effect',
    'Type',
    'ItemModifier',
    'LocationModifier',
    'LocationGroupModifier',
    'LocationRequiredSkillModifier',
    'OwnerRequiredSkillModifier'
]


from .attribute import Attribute
from .effect import Effect
from .modifier import (
    ItemModifier, LocationModifier, LocationGroupModifier,
    LocationRequiredSkillModifier, OwnerRequiredSkillModifier
)
from .type import Type
