#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jorge Niedbalski R. <jnr@metaklass.org>'

import libvirt
import logging
import uuid
import subprocess

logger = logging.getLogger(__name__)

from lxml import etree
from maasive.template import load as load_template


class DriverException(Exception):
    pass


class Instance(object):
    def __init__(self, domain):
        self.domain = domain

    @property
    def macs(self):
        xml = etree.fromstring(self.domain.XMLDesc(0))
        for mac in xml.xpath(
                "/domain/devices/interface[@type='network']/mac[@address]"):
            yield mac.get('address')


class Driver(object):
    """
    Class for manage the creation, list, update and removal of virtual machines
    """

    DEFAULT_DISK_SIZE_GIB = 2

    def __init__(self, uri="qemu:///system", *args, **kwargs):
        self.conn = libvirt.open(uri)

    def __fini__(self):
        self.close()

    @property
    def memory(self):
        return self.conn.getFreeMemory()

    @property
    def vcpus(self):
        return self.conn.getVCPUs()

    @property
    def count(self):
        return len(self)

    def __len__(self):
        return self.conn.numOfDefinedDomains() + self.conn.numOfDomains()

    def __delitem__(self, item):
        self[item].delete()

    def __iter__(self):
        domains = self.conn.listDomainsID()
        for domain in domains:
            yield self[domain]

    def __getitem__(self, item):
        try:
            if isinstance(item, int):
                domain = self.conn.lookupByID(item)
            else:
                domain = self.conn.lookupByName(item)
        except libvirt.libvirtError, e:
            if e.get_error_code() == libvirt.VIR_ERR_NO_DOMAIN:
                raise Exception("Instance not found")
            else:
                raise
        return Instance(domain)

    def close(self):
        self.conn.close()

    def _generate_uuid(self):
        return uuid.uuid1()

    def _generate_disk(self, name, size):
        logger.info('Generating a (%d GiB) disk image for virtual machine %s' %
                    (size, name))
        subprocess.call(
            "dd if=/dev/zero of=/var/lib/libvirt/images/%s.img bs=1M count=%d"
            % (name, size * 1024.00), shell=True,
            stderr=subprocess.PIPE)

    def create(self, *args, **kwargs):
        kwargs['uuid'] = self._generate_uuid()

        template = kwargs.get('template', 'default')
        template = load_template(template + '.xml', kwargs)

        name = kwargs.get('name')
        disk = kwargs.get('disk', self.DEFAULT_DISK_SIZE_GIB)

        #generate a disk image
        self._generate_disk(name, disk)
        try:
            #Todo: implement a good disk handler, for
            #now all will be image based.
            self.conn.createXML(template, 0)
        except Exception as ex:
            raise DriverException(
                'Cannot create a new virtual machine, %s' % ex.message)

        return self[name]
