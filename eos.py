#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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


import os.path

from eos.data.cacheCustomizer import CacheCustomizer
from eos.data.cacheHandler import JsonCacheHandler
from eos.data.cacheGenerator import CacheGenerator
from eos.fit import Fit
from eos.util.logger import Logger


eosVersion = 'git'


class Eos:

    def __init__(self, dataHandler, name='eos', storagePath=None):
        if storagePath is None:
            storagePath = os.path.join('~', '.eos')
        storagePath = os.path.expanduser(storagePath)

        self._logger = Logger(name, os.path.join(storagePath, 'logs'))
        self._logger.info('------------------------------------------------------------------------')
        self._logger.info('session started')

        self._cacheHandler = JsonCacheHandler(os.path.join(storagePath, 'cache'), name, self._logger)

        # Compare fingerprints from data and cache
        cacheFp = self._cacheHandler.getFingerprint()
        dataVersion = dataHandler.getVersion()
        currentFp = '{}_{}_{}'.format(name, dataVersion, eosVersion)

        # If data version is corrupt or fingerprints mismatch,
        # update cache
        if dataVersion is None or cacheFp != currentFp:
            if dataVersion is None:
                msg = 'data version is None, updating cache'
            else:
                msg = 'fingerprint mismatch: cache "{}", data "{}", updating cache'.format(cacheFp, currentFp)
            self._logger.info(msg)
            # Generate cache, apply customizations and write it
            cacheData = CacheGenerator(self._logger).run(dataHandler)
            CacheCustomizer().runBuiltIn(cacheData)
            self._cacheHandler.updateCache(cacheData, currentFp)

    def makeFit(self):
        fit = Fit(self)
        return fit
