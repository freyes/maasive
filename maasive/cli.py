#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jorge Niedbalski R. <jnr@metaklass.org>'

import argparse
import logging

from maasive.loader import Loader

LOG = logging.getLogger('maasive.cli')
MAAS_OAUTH = ("ASs3XccLNUPU7qjsjU:WmXp28J8vVHrX52S"
              "t8:Kjg468ZxVewKHMbKNpnQBvy6FcRk3KFC")


def setup_options(argv=None):
    parser = argparse.ArgumentParser(description='Publisher of messages.')
    parser.add_argument('-n', '--num-instances', dest='num_instances',
                        metavar='N', default=2, type=int,
                        help="number of instances")
    parser.add_argument('-m', '--memory', dest='memory',
                        metavar='N', default=512, type=int,
                        help="memory (in MB) assigned to each instance")
    parser.add_argument('-p', '--prefix', dest='prefix',
                        metavar='PREFIX', default='juju-',
                        help="prefix used for the name of the instances")
    parser.add_argument('-c', '--vcpus', default=1, type=int, metavar='N',
                        help="number of vcpus assigned to each instance")
    parser.add_argument('--connect', default="qemu:///system", dest="uri",
                        metavar="URI", help="Connect to the specified URI")
    parser.add_argument('--disk', default=1, type=int, dest="disk_size",
                        metavar='N',
                        help="Disk size (in GB) for each instance")

    return parser.parse_args(argv)


def on_failure(driver, instances):
    # this callback will be invoked on failure, you can
    # abort the whole installation if you want.
    pass


def main(argv=None):
    opts = setup_options(argv)
    loader = Loader(opts.uri, MAAS_OAUTH,
                    "http://localhost:8000/MAAS/api/1.0/")

    loader.get_instances(opts.num_instances,
                         {'architecture': 'amd64',
                          'prefix': opts.prefix,
                          'memory': opts.memory,
                          'cpus': opts.vcpus,
                          'disk': opts.disk_size},
                         on_failure=on_failure)


if __name__ == "__main__":
    main()
