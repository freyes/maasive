Maasive
=======

A tool for deploy/commision large amounts of KVM guests on MaaS.


Example
========

This example will start 50 KVM guests and then register them for commisioning
on the specified MAAS server.


```python
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
                    "ASs3XccLNUPU7qM9jU:WmXp28J8vVHrX52St8:Kjg468ZxVewKHMbKNpnQBvy6FcRk3KFC",
                    "http://localhost:8000/MAAS/api/1.0/")

    loader.get_instances(50, {
        'architecture': 'amd64',
        'prefix': "jujustack",
        'memory': 512,
        'cpus': 2,
        'disk': 1
    }, on_failure=on_failure)


if __name__ == "__main__":
    main()
```


Todo
====

* CLI interface
* Better logging
* Tests

