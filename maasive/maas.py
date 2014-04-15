#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jorge Niedbalski R. <jnr@metaklass.org>'

import logging
import json

logger = logging.getLogger(__name__)

from apiclient.maas_client import (
    MAASClient,
    MAASDispatcher,
    MAASOAuth,
    )

from provisioningserver.enum import POWER_TYPE


class MaaSException(object):
    pass


class MaaS(object):

    def __init__(self, credentials, url):
        [self.consumer_key, self.token, self.secret] = credentials.split(':')
        self.url = url
        self._auth = None
        self._client = None

    @property
    def auth(self):
        if self._auth is None:
            self._auth = MAASOAuth(consumer_key=self.consumer_key,
                                   resource_token=self.token,
                                   resource_secret=self.secret)
        return self._auth

    @property
    def client(self):
        if self._client is None:
            self._client = MAASClient(self.auth, MAASDispatcher(), self.url)
        return self._client

    def _get_tags(self):
        return json.loads(
            self.client.get(u'tags/', 'list').read())

    def _has_tag_or_create(self, tag_name):
        tags = self._get_tags()
        for tag in tags:
            if tag['name'] == tag_name:
                return

        return self.client.post(u'tags/',
                                'new',
                                name=tag_name,
                                kernel_opts='console=ttyS2, 115200')

    def _hydrate_node(self, mac_addr, **parameters):
        node = {
            'architecture': parameters.get('architecture', 'amd64'),
            'nodegroup': '',
            'mac_addresses': [mac_addr],
            'power_type': POWER_TYPE.VIRSH,
        }

        if 'power_address' in parameters:
            node.extend({
                'power_parameters_power_address': parameters.get(
                    'power_address')
            })

        return node

    def _update_node(self, tag, response):
        response = json.loads(response.read())
        system_id = response.get('system_id', None)

        self.client.post(u'tags/%s/' % tag,
                         'update_nodes',
                         add=system_id)

        self.client.post(u'tags/use-fastpath-installer/',
                         'update_nodes',
                         add=system_id)

    def new_node(self, tag, mac_addr, **parameters):
        self._has_tag_or_create(tag)
        try:
            response = self.client.post(u'nodes/', 'new',
                                        **self._hydrate_node(mac_addr,
                                                             **parameters))
            self._update_node(tag, response)

        except Exception as ex:
            raise MaaSException(
                'Cannot create node on maas server, exc: %s' % ex.message)
        else:
            logger.info("Registered node: %s on MaaS Server: %s" % (mac_addr,
                                                                    self.url))
