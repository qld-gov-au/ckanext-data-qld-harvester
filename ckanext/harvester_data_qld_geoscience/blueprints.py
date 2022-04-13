# encoding: utf-8

from flask import Blueprint

from ckan.views.dataset import read

blueprint = Blueprint(
    u'geoscience',
    __name__,
    url_prefix=u'/dataset/',
    url_defaults={u'package_type': u'dataset'}
)

blueprint.add_url_rule(u'/<id>', view_func=read)


def get_blueprints():
    return [blueprint]
