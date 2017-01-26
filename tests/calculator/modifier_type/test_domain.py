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


from eos.const.eos import ModifierType, ModifierDomain, ModifierOperator, State
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import Modifier
from tests.calculator.calculator_testcase import CalculatorTestCase
from tests.calculator.environment import IndependentItem, ShipItem, OwnModItem


class TestModTypeDomain(CalculatorTestCase):

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute(attribute_id=1)
        src_attr = self.ch.attribute(attribute_id=2)
        modifier = Modifier()
        modifier.type = ModifierType.domain
        modifier.domain = ModifierDomain.ship
        modifier.state = State.offline
        modifier.src_attr = src_attr.id
        modifier.operator = ModifierOperator.post_percent
        modifier.tgt_attr = self.tgt_attr.id
        effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        effect.modifiers = (modifier,)
        self.influence_source = IndependentItem(self.ch.type(
            type_id=1, effects=(effect,), attributes={src_attr.id: 20}))
        self.fit.items.add(self.influence_source)

    def test_match(self):
        influence_target = ShipItem(self.ch.type(type_id=2, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(influence_target)
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 120)
        self.fit.items.remove(self.influence_source)
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_other_domain(self):
        influence_target = OwnModItem(self.ch.type(type_id=2, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(influence_target)
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        self.fit.items.remove(influence_target)
        self.fit.items.remove(self.influence_source)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)
