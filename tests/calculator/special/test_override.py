        # ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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


from unittest.mock import call

from eos.const.eos import State, Domain, Scope, Operator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import Modifier
from tests.calculator.calculator_testcase import CalculatorTestCase
from tests.calculator.environment import IndependentItem


class TestOverride(CalculatorTestCase):
    """
    Check that attribute overriding functions as expected.
    """

    def setUp(self):
        super().setUp()
        self.src_attr = self.ch.attribute(attribute_id=1)
        self.tgt_attr = self.ch.attribute(attribute_id=2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.scope = Scope.local
        modifier.src_attr = self.src_attr.id
        modifier.operator = Operator.post_percent
        modifier.tgt_attr = self.tgt_attr.id
        modifier.domain = Domain.self_
        modifier.filter_type = None
        modifier.filter_value = None
        effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        effect.modifiers = (modifier,)
        self.holder = IndependentItem(self.ch.type_(type_id=1, effects=(effect,),
            attributes={self.src_attr.id: 10, self.tgt_attr.id: 50}))
        self.fit.items.add(self.holder)

    def test_override_set(self):
        # Setup
        holder = self.holder
        self.assertAlmostEqual(holder.attributes[self.tgt_attr.id], 55)
        # Action
        holder.attributes._override_set(self.src_attr.id, 77)
        # Verification
        self.assertEqual(holder.attributes[self.src_attr.id], 77)
        self.assertAlmostEqual(holder.attributes[self.tgt_attr.id], 88.5)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_reset(self):
        # Setup
        holder = self.holder
        holder.attributes._override_set(self.src_attr.id, 77)
        self.assertAlmostEqual(holder.attributes[self.tgt_attr.id], 88.5)
        # Action
        holder.attributes._override_set(self.src_attr.id, 88)
        # Verification
        self.assertEqual(holder.attributes[self.src_attr.id], 88)
        self.assertAlmostEqual(holder.attributes[self.tgt_attr.id], 94)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_delete(self):
        # Setup
        holder = self.holder
        holder.attributes._override_set(self.src_attr.id, 77)
        self.assertAlmostEqual(holder.attributes[self.tgt_attr.id], 88.5)
        # Action
        holder.attributes._override_del(self.src_attr.id)
        # Verification
        self.assertEqual(holder.attributes[self.src_attr.id], 10)
        self.assertAlmostEqual(holder.attributes[self.tgt_attr.id], 55)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_delete_persistent(self):
        # Setup
        holder = self.holder
        holder.attributes._override_set(self.src_attr.id, 77, persist=True)
        self.assertAlmostEqual(holder.attributes[self.tgt_attr.id], 88.5)
        # Action
        holder.attributes._override_del(self.src_attr.id)
        # Verification
        self.assertEqual(holder.attributes[self.src_attr.id], 10)
        self.assertAlmostEqual(holder.attributes[self.tgt_attr.id], 55)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_clear(self):
        # Setup
        holder = self.holder
        holder.attributes._override_set(self.src_attr.id, 77)
        self.assertAlmostEqual(holder.attributes[self.tgt_attr.id], 88.5)
        # Action
        holder.attributes.clear()
        # Verification
        self.assertEqual(holder.attributes[self.src_attr.id], 10)
        self.assertAlmostEqual(holder.attributes[self.tgt_attr.id], 55)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_clear_persistent(self):
        # Setup
        holder = self.holder
        holder.attributes._override_set(self.src_attr.id, 77, persist=True)
        self.assertAlmostEqual(holder.attributes[self.tgt_attr.id], 88.5)
        # Action
        holder.attributes.clear()
        # Verification
        self.assertEqual(holder.attributes[self.src_attr.id], 77)
        self.assertAlmostEqual(holder.attributes[self.tgt_attr.id], 88.5)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)