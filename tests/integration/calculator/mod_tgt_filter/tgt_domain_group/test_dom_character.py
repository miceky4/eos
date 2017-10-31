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


from eos import *
from eos.const.eos import ModifierDomain, ModifierOperator, ModifierTargetFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestTgtDomainGroupDomainChar(CalculatorTestCase):

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attr()
        src_attr = self.ch.attr()
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.domain_group,
            tgt_domain=ModifierDomain.character,
            tgt_filter_extra_arg=35,
            tgt_attr_id=self.tgt_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr_id=src_attr.id)
        effect = self.ch.effect(
            category_id=EffectCategoryId.passive, modifiers=[modifier])
        self.influence_src = Rig(self.ch.type(
            attributes={src_attr.id: 20}, effects=[effect]).id)

    def test_parent_domain_character(self):
        influence_tgt = Implant(self.ch.type(
            group_id=35, attributes={self.tgt_attr.id: 100}).id)
        self.fit.implants.add(influence_tgt)
        # Action
        self.fit.rigs.add(self.influence_src)
        # Verification
        self.assertAlmostEqual(influence_tgt.attributes[self.tgt_attr.id], 120)
        # Action
        self.fit.rigs.remove(self.influence_src)
        # Verification
        self.assertAlmostEqual(influence_tgt.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_parent_domain_other(self):
        influence_tgt = Drone(self.ch.type(
            group_id=35, attributes={self.tgt_attr.id: 100}).id)
        self.fit.drones.add(influence_tgt)
        # Action
        self.fit.rigs.add(self.influence_src)
        # Verification
        self.assertAlmostEqual(influence_tgt.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_group_other(self):
        influence_tgt = Implant(self.ch.type(
            group_id=3, attributes={self.tgt_attr.id: 100}).id)
        self.fit.implants.add(influence_tgt)
        # Action
        self.fit.rigs.add(self.influence_src)
        # Verification
        self.assertAlmostEqual(influence_tgt.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
