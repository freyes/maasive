#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jorge Niedbalski R. <jnr@metaklass.org>'

from maasive.driver import Driver
from maasive.maas import MaaS

import logging
import collections

logger = logging.getLogger(__name__)


class LoaderException(Exception):
    pass


class Loader(object):

    def __init__(self, libvirt_uri, maas_oauth, maas_url, *args, **kwargs):
        self.driver = Driver(uri=libvirt_uri, *args, **kwargs)
        self.maas = MaaS(maas_oauth, maas_url, *args, **kwargs)

    def _register_on_maas(self, instance, **details):
        for mac in instance.macs:
            self.maas.new_node(details['prefix'],
                               mac,
                               **details)

    def _run_callback(self, name, *args, **kwargs):
        callback = self.callbacks.get(name, None)
        if callback and isinstance(callback, collections.Callable):
            return callback(*args, **kwargs)

    def get_instances(self, instances, details, **callbacks):

        self.callbacks = callbacks
        loaded_instances = []

        for i in xrange(0, instances):
            logger.debug("Starting instance %d of %d" % (i, instances))
            try:
                if 'prefix' in details:
                    details['name'] = '%s%d' % (details['prefix'], i)
                else:
                    details['name'] = 'new_machine_%d' % i

                instance = self.driver.create(**details)

                logger.debug("Created new instance %d, details: %s"
                             % (i, instance))

                self._run_callback('on_new_instance', self.driver,
                                   instance)
                self._register_on_maas(instance, **details)
                loaded_instances.append(instance)

            except Exception as ex:
                logger.error("Error starting new instance %d, error: %s" %
                             (i, ex.message))
                self._run_callback('on_failure', self.driver, ex)

        self._run_callback('on_load_ready', loaded_instances)
        return loaded_instances
