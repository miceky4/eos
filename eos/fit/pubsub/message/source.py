# ==============================================================================
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
# ==============================================================================


from eos.const.eos import State
from eos.util.repr import make_repr_str
from .base import BaseInputMessage, BaseInstructionMessage
from .item import (
    InstrEffectsStart, InstrEffectsStop, InstrItemAdd, InstrItemRemove,
    InstrStatesActivate, InstrStatesDeactivate)


class InputSourceChanged(BaseInputMessage):

    def __init__(self, old, new, items):
        self.old = old
        self.new = new
        self.items = items

    def get_instructions(self):
        instructions = []
        # Issue instructions to remove items, if there was an old source
        if self.old is not None:
            for item in self.items:
                states = {s for s in State if s <= item.state}
                # Handle effect deactivation
                running_copy = set(item._running_effect_ids)
                if running_copy:
                    instructions.append(InstrEffectsStop(item, running_copy))
                    item._running_effect_ids.clear()
                # Handle state deactivation
                instructions.append(InstrStatesDeactivate(item, states))
                # Handle item removal
                instructions.append(InstrItemRemove(item))
        # Force refresh of all source-dependent objects
        instructions.append(InstrRefreshSource())
        # Issue instructions to add items again, if there's a new source
        if self.new is not None:
            for item in self.items:
                # Handle item addition
                instructions.append(InstrItemAdd(item))
                # Handle state activation
                states = {s for s in State if s <= item.state}
                instructions.append(InstrStatesActivate(item, states))
                # Handle effect activation
                to_start, to_stop = item._get_wanted_effect_status_changes()
                if to_start:
                    item._running_effect_ids.update(to_start)
                    instructions.append(InstrEffectsStart(item, to_start))
                if to_stop:
                    instructions.append(InstrEffectsStop(item, to_stop))
                    item._running_effect_ids.difference_update(to_stop)
        return instructions

    def __repr__(self):
        spec = ['old', 'new', 'items']
        return make_repr_str(self, spec)


class InstrRefreshSource(BaseInstructionMessage):
    ...
