#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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
#===============================================================================


from eos.const import State, Location, Context, Operator
from eos.fit.attributeCalculator.modifier.modifier import Modifier
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import Fit, IndependentItem


class TestStateSwitching(AttrCalcTestCase):
    """Test holder state switching and modifier states"""

    def setUp(self):
        AttrCalcTestCase.setUp(self)
        self.tgtAttr = tgtAttr = Attribute(1, stackable=1)
        srcAttr1 = Attribute(2)
        srcAttr2 = Attribute(3)
        srcAttr3 = Attribute(4)
        srcAttr4 = Attribute(5)
        modifierOff = Modifier()
        modifierOff.state = State.offline
        modifierOff.context = Context.local
        modifierOff.sourceAttributeId = srcAttr1.id
        modifierOff.operator = Operator.postMul
        modifierOff.targetAttributeId = tgtAttr.id
        modifierOff.location = Location.self_
        modifierOff.filterType = None
        modifierOff.filterValue = None
        modifierOn = Modifier()
        modifierOn.state = State.online
        modifierOn.context = Context.local
        modifierOn.sourceAttributeId = srcAttr2.id
        modifierOn.operator = Operator.postMul
        modifierOn.targetAttributeId = tgtAttr.id
        modifierOn.location = Location.self_
        modifierOn.filterType = None
        modifierOn.filterValue = None
        modifierAct = Modifier()
        modifierAct.state = State.active
        modifierAct.context = Context.local
        modifierAct.sourceAttributeId = srcAttr3.id
        modifierAct.operator = Operator.postMul
        modifierAct.targetAttributeId = tgtAttr.id
        modifierAct.location = Location.self_
        modifierAct.filterType = None
        modifierAct.filterValue = None
        modifierOver = Modifier()
        modifierOver.state = State.overload
        modifierOver.context = Context.local
        modifierOver.sourceAttributeId = srcAttr4.id
        modifierOver.operator = Operator.postMul
        modifierOver.targetAttributeId = tgtAttr.id
        modifierOver.location = Location.self_
        modifierOver.filterType = None
        modifierOver.filterValue = None
        # Overload category will make sure that holder can enter all states
        effect = Effect(None, EffectCategory.overload)
        effect._modifiers = (modifierOff, modifierOn, modifierAct, modifierOver)
        self.fit = Fit({tgtAttr.id: tgtAttr, srcAttr1.id: srcAttr1, srcAttr2.id: srcAttr2,
                        srcAttr3.id: srcAttr3, srcAttr4.id: srcAttr4})
        self.holder = IndependentItem(Type(None, effects=(effect,), attributes={self.tgtAttr.id: 100, srcAttr1.id: 1.1,
                                                                                srcAttr2.id: 1.3, srcAttr3.id: 1.5,
                                                                                srcAttr4.id: 1.7}))

    def testFitOffline(self):
        self.holder.state = State.offline
        self.fit.items.append(self.holder)
        self.assertAlmostEqual(self.holder.attributes[self.tgtAttr.id], 110)
        self.fit.items.remove(self.holder)
        self.assertBuffersEmpty(self.fit)

    def testFitOnline(self):
        self.holder.state = State.online
        self.fit.items.append(self.holder)
        self.assertAlmostEqual(self.holder.attributes[self.tgtAttr.id], 143)
        self.fit.items.remove(self.holder)
        self.assertBuffersEmpty(self.fit)

    def testFitActive(self):
        self.holder.state = State.active
        self.fit.items.append(self.holder)
        self.assertAlmostEqual(self.holder.attributes[self.tgtAttr.id], 214.5)
        self.fit.items.remove(self.holder)
        self.assertBuffersEmpty(self.fit)

    def testFitOverloaded(self):
        self.holder.state = State.overload
        self.fit.items.append(self.holder)
        self.assertAlmostEqual(self.holder.attributes[self.tgtAttr.id], 364.65)
        self.fit.items.remove(self.holder)
        self.assertBuffersEmpty(self.fit)

    def testSwitchUpSingle(self):
        self.holder.state = State.offline
        self.fit.items.append(self.holder)
        self.holder.state = State.online
        self.assertAlmostEqual(self.holder.attributes[self.tgtAttr.id], 143)
        self.fit.items.remove(self.holder)
        self.assertBuffersEmpty(self.fit)

    def testSwitchUpMultiple(self):
        self.holder.state = State.online
        self.fit.items.append(self.holder)
        self.holder.state = State.overload
        self.assertAlmostEqual(self.holder.attributes[self.tgtAttr.id], 364.65)
        self.fit.items.remove(self.holder)
        self.assertBuffersEmpty(self.fit)

    def testSwitchDownSingle(self):
        self.holder.state = State.overload
        self.fit.items.append(self.holder)
        self.holder.state = State.active
        self.assertAlmostEqual(self.holder.attributes[self.tgtAttr.id], 214.5)
        self.fit.items.remove(self.holder)
        self.assertBuffersEmpty(self.fit)

    def testSwitchDownMultiple(self):
        self.holder.state = State.active
        self.fit.items.append(self.holder)
        self.holder.state = State.offline
        self.assertAlmostEqual(self.holder.attributes[self.tgtAttr.id], 110)
        self.fit.items.remove(self.holder)
        self.assertBuffersEmpty(self.fit)
