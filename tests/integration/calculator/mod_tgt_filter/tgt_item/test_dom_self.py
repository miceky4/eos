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
from eos.const.eve import EffectCategory
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestTgtItemDomainSelf(CalculatorTestCase):

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attr()
        self.src_attr = self.ch.attr()
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr=self.src_attr.id)
        self.effect = self.ch.effect(
            category=EffectCategory.passive, modifiers=[modifier])

    def test_independent(self):
        item = Ship(self.ch.type(
            attributes={self.tgt_attr.id: 100, self.src_attr.id: 20},
            effects=[self.effect]).id)
        # Action
        self.fit.ship = item
        # Verification
        self.assertAlmostEqual(item.attributes[self.tgt_attr.id], 120)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_parent_domain_character(self):
        item = Implant(self.ch.type(
            attributes={self.tgt_attr.id: 100, self.src_attr.id: 20},
            effects=[self.effect]).id)
        # Action
        self.fit.implants.add(item)
        # Verification
        self.assertAlmostEqual(item.attributes[self.tgt_attr.id], 120)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_parent_domain_ship(self):
        item = Rig(self.ch.type(
            attributes={self.tgt_attr.id: 100, self.src_attr.id: 20},
            effects=[self.effect]).id)
        # Action
        self.fit.rigs.add(item)
        # Verification
        self.assertAlmostEqual(item.attributes[self.tgt_attr.id], 120)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_other(self):
        # Here we check that self-reference modifies only carrier of effect, and
        # nothing else is affected. We position item as character and check
        # another item which has character modifier domain to ensure that items
        # 'belonging' to self are not affected too
        influence_src = Character(self.ch.type(
            attributes={self.tgt_attr.id: 100, self.src_attr.id: 20},
            effects=[self.effect]).id)
        item = Implant(self.ch.type(attributes={self.tgt_attr.id: 100}).id)
        self.fit.implants.add(item)
        # Action
        self.fit.character = influence_src
        # Verification
        self.assertAlmostEqual(item.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
