#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jorge Niedbalski R. <jnr@metaklass.org>'

from maasive.loader import Loader

import logging

logger = logging.getLogger(__name__)


def on_failure(driver, instances):
    #this callback will be invoked on failure, you can
    #abort the whole installation if you want.
    pass


def main():
    loader = Loader("qemu:///system",
                    "ASs3XccLNUPU7qjsjU:WmXp28J8vVHrX52St8:Kjg468ZxVewKHMbKNpnQBvy6FcRk3KFC",
                    "http://localhost:8000/MAAS/api/1.0/")

    loader.get_instances(15, {
        'architecture': 'amd64',
        'prefix': "juju-",
        'memory': 512,
        'cpus': 2,
        'disk': 1
    }, on_failure=on_failure)


if __name__ == "__main__":
    main()
