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

    def __init__(self, libvirt_uri, maas_oauth, maas_url):
        self.driver = Driver(uri=libvirt_uri)
        self.maas = MaaS(maas_oauth, maas_url)

    def _register_on_maas(self, instance, **details):
        for mac in instance.macs:
            self.maas.new_node(details['prefix'],
                               mac,
                               **details)

    def get_instances(self, instances, details, **callbacks):
        loaded_instances = []

        for i in xrange(0, instances):
            logger.debug("Starting instance %d of %d" % (i, instances))
            try:
                if 'prefix' in details:
                    details['name'] = '%s-%d' % (details['prefix'], i)
                else:
                    details['name'] = 'new_machine_%d' % i

                instance = self.driver.create(**details)
            except Exception as ex:
                logger.error("Error starting new instance %d, error: %s" %
                             (i, ex.message))
                on_failure = callbacks.get('on_failure', None)

                if on_failure and isinstance(on_failure, collections.Callable):
                    on_failure(self.driver, loaded_instances)
            else:
                logger.debug("Created new instance %d, details: %s" % (i,
                                                                       instance))
                on_new_instance = callbacks.get('on_new_instance', None)

                if on_new_instance and isinstance(on_new_instance,
                                                  colllections.Callable):
                    on_new_instance(self.driver, instance)
                try:
                    self._register_on_maas(instance, **details)
                except:
                    raise
                else:
                    loaded_instances.append(instance)

        on_load_ready = callbacks.get('on_load_ready', None)
        if on_load_ready and isinstance(on_load_ready, collections.Callable):
            return on_load_ready(loaded_instances)

        return loaded_instances
