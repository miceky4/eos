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

from abc import ABCMeta
from abc import abstractproperty
from collections import Mapping

from eos import const
from .affector import Affector


class MutableAttributeHolder:
    """
    Base attribute holder class inherited by all classes that need to keep track of modified attributes.
    This class holds a MutableAttributeMap to keep track of changes.
    """
    __metaclass__ = ABCMeta

    @abstractproperty
    def location(self):
        ...

    def __init__(self, invType):
        """ Constructor. Accepts invType"""

        # Which fit this holder is bound to
        self.fit = None

        # Which invType this holder wraps
        self.invType = invType

        # Special dictionary subclass that holds modified attributes and data related to their calculation
        self.attributes = MutableAttributeMap(self)

    def generateAffectors(self):
        """Get all affectors generated by holder"""
        affectors = set()
        for effect in self.invType.effects:
            for info in effect.infos:
                affector = Affector(self, info)
                affectors.add(affector)
        return affectors

    def _damageDependantsOnAttr(self, attrId):
        """Clear calculated attribute values relying on value of passed attribute"""
        for affector in self.generateAffectors():
            info = affector.info
            # Skip affectors which do not use attribute being damaged as source
            if info.sourceValue != attrId or info.sourceType != const.srcAttr:
                continue
            # Gp through all holders targeted by info
            for targetHolder in self.fit._getAffectees(affector):
                # And remove target attribute
                del targetHolder.attributes[info.targetAttribute]

    def _damageDependantsAll(self):
        """Clear calculated attribute values relying on anything assigned to holder"""
        for affector in self.generateAffectors():
            # Go through all holders targeted by info
            for targetHolder in self.fit._getAffectees(affector):
                # And remove target attribute
                del targetHolder.attributes[affector.info.targetAttribute]

class MutableAttributeMap(Mapping):
    """Store, process and provide access to modified attribute values"""

    def __init__(self, holder):
        self.__holder = holder
        # Actual container of calculated attributes
        # Format: attributeID: value
        self.__modifiedAttributes = {}

    def __getitem__(self, attrId):
        try:
            val = self.__modifiedAttributes[attrId]
        except KeyError:
            val = self.__modifiedAttributes[attrId] = self.__calculate(attrId)
            self.__holder._damageDependantsOnAttr(attrId)
        return val

    def __len__(self):
        return len(self.keys())

    def __contains__(self, attrId):
        result = attrId in self.__modifiedAttributes or attrId in self.__holder.invType.attributes
        return result

    def __iter__(self):
        for k in self.keys():
            yield k

    def keys(self):
        keys = set(self.__modifiedAttributes.keys()).intersection(self.__holder.invType.attributes.keys())
        return keys

    def __delitem__(self, attrId):
        if attrId in self.__modifiedAttributes:
            # Clear the value in our calculated attributes dict
            del self.__modifiedAttributes[attrId]
            # And make sure all other attributes relying on it
            # are cleared too
            self.__holder._damageDependantsOnAttr(attrId)

    def __calculate(self, attrId):
        """
        Run calculations to find the actual value of attribute with ID equal to attrID.
        All other attribute values are assumed to be final (if they're not, this method will be called on them)
        """
        holder =  self.__holder
        # Base attribute value which we'll use for modification
        result = holder.invType.attributes.get(attrId)
        # Attribute metadata
        attrMeta = holder.fit._dataHandler.getAttribute(attrId)
        # Container for non-penalized modifiers
        # Format: operator: set(values)
        normalMods = {}
        # Container for penalized modifiers
        # Format: operator: set(values)
        penalizedMods = {}
        # Now, go through all affectors affecting ourr holder
        for affector in holder.fit._getAffectors(holder):
            sourceHolder, info = affector
            # Skip affectors who do not target attribute being calculated
            if info.targetAttribute != attrId:
                continue
            operator = info.operator
            # If source value is attribute reference
            if info.sourceType == const.srcAttr:
                # Get its value
                modValue = sourceHolder.attributes[info.sourceValue]
                # And decide if it should be stacking penalized or not, based on stackable property,
                # source item category and operator
                penalize = not attrMeta.stackable and sourceHolder.invType.categoryId not in const.penaltyImmuneCats \
                and operator in {const.optrPreMul, const.optrPostMul, const.optrPostPercent, const.optrPreDiv, const.optrPostDiv}
            # For value modifications, just use stored in info value and avoid its penalization
            else:
                modValue = info.sourceValue
                penalize = False
            # Normalize addition/subtraction, so it's always
            # acts as addition
            if operator == const.optrModSub:
                modValue = -modValue
            # Normalize multiplicative modifiers, converting them into form of
            # multiplier
            elif operator in {const.optrPreDiv, const.optrPostDiv}:
                modValue = 1 / modValue
            elif operator == const.optrPostPercent:
                modValue = modValue / 100 + 1
            # Add value to appropriate dictionary
            if penalize is True:
                try:
                    modList = penalizedMods[operator]
                except KeyError:
                    modList = penalizedMods[operator] = []
            else:
                try:
                    modList = normalMods[operator]
                except KeyError:
                    modList = normalMods[operator] = []
            modList.append(modValue)
        # When data gathering was finished, process penalized modifiers
        # They are penalized on per-operator basis
        for operator, modList in penalizedMods.items():
            # Gather positive modifiers into one chain, negative
            # into another
            chainPositive = []
            chainNegative = []
            for modVal in modList:
                # Transform value into form of multiplier - 1 for ease of
                # stacking chain calculation
                modVal -= 1
                if modVal >= 0:
                    chainPositive.append(modVal)
                else:
                    chainNegative.append(modVal)
            # Strongest modifiers always go first
            chainPositive.sort(reverse=True)
            chainNegative.sort()
            # Get final penalized factor and store it into normal dictionary
            penalizedValue = self.__penalizeChain(chainPositive) * self.__penalizeChain(chainNegative)
            try:
                modList = normalMods[operator]
            except KeyError:
                modList = normalMods[operator] = []
            modList.append(penalizedValue)
        # Calculate result of normal dictionary, according to operator order
        for operator in sorted(normalMods):
            modList = normalMods[operator]
            # Pick best modifier for assignments, based on highIsGood value
            if operator in (const.optrPreAssignment, const.optrPostAssignment):
                result = max(modList) if attrMeta.highIsGood is True else min(modList)
            elif operator in (const.optrModAdd, const.optrModSub):
                for modVal in modList:
                    result += modVal
            elif operator in (const.optrPreMul, const.optrPreDiv, const.optrPostMul,
                               const.optrPostDiv, const.optrPostPercent):
                for modVal in modList:
                    result *= modVal
        return result

    def __penalizeChain(self, chain):
        """Calculate stacking penalty chain"""
        # Base final multiplier on 1
        result = 1
        for position, modifier in enumerate(chain):
            # Ignore 12th modifier and further as non-significant
            if position > 10:
                break
            # Apply stacking penalty based on modifier position
            result *= 1 + modifier * const.penaltyBase ** (position ** 2)
        return result
