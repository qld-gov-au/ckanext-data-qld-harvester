import logging
from ckanext.harvest.harvesters.ckanharvester import CKANHarvester
from ckan.lib.helpers import json

log = logging.getLogger(__name__)


class GeoScienceCKANHarvester(CKANHarvester):
    '''
    A Harvester for CKAN portal Geoscience
    '''
    config = None

    api_version = 2
    action_api_version = 3

    def info(self):
        return {
            'name': 'geoscience_ckan_harvester',
            'title': 'GSQ Open Data Portal',
            'description': 'Harvests the remote CKAN instance of GSQ Open Data Portal datasets into Data QLD Open Data portal schema',
            'form_config_interface': 'Text'
        }

    def validate_config(self, config):
        if not config:
            return config

        try:
            config_obj = json.loads(config)
            # TODO Validation of values required for harvest
        except ValueError, e:
            raise e

        return config

    def modify_package_dict(self, package_dict, harvest_object):

        # TODO get default values from harvest config
        package_dict['type'] = 'dataset'
        package_dict['update_frequency'] = 'non-regular'
        package_dict['author_email'] = package_dict['author_email'] if package_dict['author_email'] else 'test@test.com'  # TODO What should the default value be
        package_dict['version'] = package_dict['version'] if package_dict['version'] else '1.0'  # TODO What should the default value be
        package_dict['data_driven_application'] = 'NO'
        package_dict['security_classification'] = 'PUBLIC'
        package_dict['de_identified_data'] = 'NO'
        package_dict['url'] = u'https://geoscience.data.qld.gov.au/dataset/{0}'.format(package_dict.get('name'))
        # TODO Should the URL be injected into the template instead? Some notes are empty which are required so this fixes that
        package_dict['notes'] = 'URL:{0}\r\n\r\n{1}'.format(package_dict.get('url'), package_dict.get('notes', ''))

        package_dict.pop('resources', [])

        return package_dict
