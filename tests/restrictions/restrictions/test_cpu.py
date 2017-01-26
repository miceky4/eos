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


from eos.const.eos import Restriction, State
from eos.const.eve import Attribute
from eos.fit.item import ModuleHigh, Implant
from tests.restrictions.restriction_testcase import RestrictionTestCase


class TestCpu(RestrictionTestCase):
    """Check functionality of cpu restriction"""

    def test_fail_excess_single(self):
        # When ship provides cpu output, but single consumer
        # demands for more, error should be raised
        eve_type = self.ch.type(type_id=1, attributes={Attribute.cpu: 0})
        holder = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder.attributes = {Attribute.cpu: 50}
        self.add_holder(holder)
        self.fit.stats.cpu.used = 50
        self.fit.stats.cpu.output = 40
        restriction_error = self.get_restriction_error(holder, Restriction.cpu)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 40)
        self.assertEqual(restriction_error.total_use, 50)
        self.assertEqual(restriction_error.holder_use, 50)
        self.remove_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_excess_single_other_class_domain(self):
        # Make sure holders of all classes are affected
        eve_type = self.ch.type(type_id=1, attributes={Attribute.cpu: 0})
        holder = self.make_item_mock(Implant, eve_type, state=State.online)
        holder.attributes = {Attribute.cpu: 50}
        self.add_holder(holder)
        self.fit.stats.cpu.used = 50
        self.fit.stats.cpu.output = 40
        restriction_error = self.get_restriction_error(holder, Restriction.cpu)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 40)
        self.assertEqual(restriction_error.total_use, 50)
        self.assertEqual(restriction_error.holder_use, 50)
        self.remove_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_excess_single_undefined_output(self):
        # When stats module does not specify output, make sure
        # it's assumed to be 0
        eve_type = self.ch.type(type_id=1, attributes={Attribute.cpu: 0})
        holder = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder.attributes = {Attribute.cpu: 5}
        self.add_holder(holder)
        self.fit.stats.cpu.used = 5
        self.fit.stats.cpu.output = None
        restriction_error = self.get_restriction_error(holder, Restriction.cpu)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 0)
        self.assertEqual(restriction_error.total_use, 5)
        self.assertEqual(restriction_error.holder_use, 5)
        self.remove_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_excess_multiple(self):
        # When multiple consumers require less than cpu output
        # alone, but in sum want more than total output, it should
        # be erroneous situation
        eve_type = self.ch.type(type_id=1, attributes={Attribute.cpu: 0})
        holder1 = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder1.attributes = {Attribute.cpu: 25}
        self.add_holder(holder1)
        holder2 = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder2.attributes = {Attribute.cpu: 20}
        self.add_holder(holder2)
        self.fit.stats.cpu.used = 45
        self.fit.stats.cpu.output = 40
        restriction_error1 = self.get_restriction_error(holder1, Restriction.cpu)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 40)
        self.assertEqual(restriction_error1.total_use, 45)
        self.assertEqual(restriction_error1.holder_use, 25)
        restriction_error2 = self.get_restriction_error(holder2, Restriction.cpu)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.output, 40)
        self.assertEqual(restriction_error2.total_use, 45)
        self.assertEqual(restriction_error2.holder_use, 20)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_excess_modified(self):
        # Make sure modified cpu values are taken
        eve_type = self.ch.type(type_id=1, attributes={Attribute.cpu: 40})
        holder = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder.attributes = {Attribute.cpu: 100}
        self.add_holder(holder)
        self.fit.stats.cpu.used = 100
        self.fit.stats.cpu.output = 50
        restriction_error = self.get_restriction_error(holder, Restriction.cpu)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 50)
        self.assertEqual(restriction_error.total_use, 100)
        self.assertEqual(restriction_error.holder_use, 100)
        self.remove_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_mix_usage_negative(self):
        # If some holder has negative usage and cpu error is
        # still raised, check it's not raised for holder with
        # negative usage
        eve_type = self.ch.type(type_id=1, attributes={Attribute.cpu: 0})
        holder1 = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder1.attributes = {Attribute.cpu: 100}
        self.add_holder(holder1)
        holder2 = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder2.attributes = {Attribute.cpu: -10}
        self.add_holder(holder2)
        self.fit.stats.cpu.used = 90
        self.fit.stats.cpu.output = 50
        restriction_error1 = self.get_restriction_error(holder1, Restriction.cpu)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 50)
        self.assertEqual(restriction_error1.total_use, 90)
        self.assertEqual(restriction_error1.holder_use, 100)
        restriction_error2 = self.get_restriction_error(holder2, Restriction.cpu)
        self.assertIsNone(restriction_error2)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_mix_usage_zero(self):
        # If some holder has zero usage and cpu error is
        # still raised, check it's not raised for holder with
        # zero usage
        eve_type = self.ch.type(type_id=1, attributes={Attribute.cpu: 0})
        holder1 = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder1.attributes = {Attribute.cpu: 100}
        self.add_holder(holder1)
        holder2 = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder2.attributes = {Attribute.cpu: 0}
        self.add_holder(holder2)
        self.fit.stats.cpu.used = 100
        self.fit.stats.cpu.output = 50
        restriction_error1 = self.get_restriction_error(holder1, Restriction.cpu)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 50)
        self.assertEqual(restriction_error1.total_use, 100)
        self.assertEqual(restriction_error1.holder_use, 100)
        restriction_error2 = self.get_restriction_error(holder2, Restriction.cpu)
        self.assertIsNone(restriction_error2)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass(self):
        # When total consumption is less than output,
        # no errors should be raised
        eve_type = self.ch.type(type_id=1, attributes={Attribute.cpu: 0})
        holder1 = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder1.attributes = {Attribute.cpu: 25}
        self.add_holder(holder1)
        holder2 = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder2.attributes = {Attribute.cpu: 20}
        self.add_holder(holder2)
        self.fit.stats.cpu.used = 45
        self.fit.stats.cpu.output = 50
        restriction_error1 = self.get_restriction_error(holder1, Restriction.cpu)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(holder2, Restriction.cpu)
        self.assertIsNone(restriction_error2)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_no_attr_eve_type(self):
        # When added holder's EVE type doesn't have attribute, holder
        # shouldn't be tracked by register, and thus, no errors
        # should be raised
        eve_type = self.ch.type(type_id=1)
        holder = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder.attributes = {Attribute.cpu: 100}
        self.add_holder(holder)
        self.fit.stats.cpu.used = 100
        self.fit.stats.cpu.output = 50
        restriction_error = self.get_restriction_error(holder, Restriction.cpu)
        self.assertIsNone(restriction_error)
        self.remove_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_state(self):
        # When holder isn't online, it shouldn't consume anything
        eve_type = self.ch.type(type_id=1, attributes={Attribute.cpu: 0})
        holder = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        holder.attributes = {Attribute.cpu: 50}
        self.add_holder(holder)
        self.fit.stats.cpu.used = 50
        self.fit.stats.cpu.output = 40
        restriction_error = self.get_restriction_error(holder, Restriction.cpu)
        self.assertIsNone(restriction_error)
        self.remove_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
