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


from eos import *
from eos.const.eos import ModifierTargetFilter, ModifierDomain, ModifierOperator, EosEveTypes
from eos.const.eve import Attribute, EffectCategory
from eos.data.cache_object.modifier import DogmaModifier
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestTgtOwnerSkillrqSkillrqSelf(CalculatorTestCase):

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute()
        src_attr = self.ch.attribute()
        modifier = DogmaModifier(
            tgt_filter=ModifierTargetFilter.owner_skillrq,
            tgt_domain=ModifierDomain.character,
            tgt_filter_extra_arg=EosEveTypes.current_self,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr=src_attr.id
        )
        effect = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier])
        self.source_eve_type = self.ch.type(effects=[effect], attributes={src_attr.id: 20})
        self.influence_source = Implant(self.source_eve_type.id)

    def test_match(self):
        influence_target = Drone(self.ch.type(attributes={
            self.tgt_attr.id: 100, Attribute.required_skill_1: self.source_eve_type.id,
            Attribute.required_skill_1_level: 1
        }).id)
        self.fit.drones.add(influence_target)
        # Action
        self.fit.implants.add(self.influence_source)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 120)
        # Action
        self.fit.implants.remove(self.influence_source)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_skill_other(self):
        influence_target = Drone(self.ch.type(attributes={
            self.tgt_attr.id: 100, Attribute.required_skill_1: 87, Attribute.required_skill_1_level: 1
        }).id)
        self.fit.drones.add(influence_target)
        # Action
        self.fit.implants.add(self.influence_source)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)