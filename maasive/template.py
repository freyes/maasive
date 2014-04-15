#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jorge Niedbalski R. <jorge.niedbalski@canonical.com>'


from jinja2 import Environment, PackageLoader

env = Environment()
env.loader = PackageLoader('maasive', 'templates')


def load(name, params):
    """
    Load a template from the maasive.templates package
    :param name: template name
    :type name: string
    """
    return env.get_template(name).render(**params)
