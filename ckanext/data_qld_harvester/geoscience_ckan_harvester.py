import logging
import ckan.plugins.toolkit as toolkit
from ckanext.harvest.harvesters.ckanharvester import CKANHarvester
from ckan.lib.helpers import json
from ckan import model
from ckanext.harvest.model import HarvestObject
from ckanext.harvest.model import HarvestObjectExtra as HOExtra

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

    def gather_stage(self, harvest_job):
        guids_in_source = super(GeoScienceCKANHarvester, self).gather_stage(harvest_job)

        # Get the previous guids for this source
        query = model.Session.query(HarvestObject.guid, HarvestObject.package_id).\
                                    filter(HarvestObject.current==True).\
                                    filter(HarvestObject.harvest_source_id==harvest_job.source.id)
        guid_to_package_id = {}

        for guid, package_id in query:
            guid_to_package_id[guid] = package_id

        guids_in_db = set(guid_to_package_id.keys())

        # Check datasets that need to be deleted
        guids_to_delete = set(guids_in_db) - set(guids_in_source)
        for guid in guids_to_delete:
            # Delete package
            package_id = guid_to_package_id[guid]
            context = {'model': model, 'session': model.Session,
                    'user': self._get_user_name()}
            try:
                toolkit.get_action('package_delete')(context, {'id': package_id})
                log.info('Deleted package {0} with guid {1}'.format(package_id, guid))

                obj = HarvestObject(guid=guid, job=harvest_job,
                                    package_id=guid_to_package_id[guid],
                                    extras=[HOExtra(key='status', value='delete')])

                model.Session.query(HarvestObject).\
                    filter_by(guid=guid).\
                    update({'current': False}, False)
                obj.save()
            except Exception as e
                # TODO: What should we do here?
                log.error('Deleting package {0} with guid {1} failed'.format(package_id, guid))

        return guids_in_source
