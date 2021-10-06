import logging
import ckan.plugins.toolkit as toolkit
from ckanext.harvest.harvesters.ckanharvester import CKANHarvester
from ckan.lib.helpers import json
from ckan import model
from ckanext.harvest.model import HarvestObject
from ckanext.harvest.model import HarvestObjectExtra as HOExtra

import six

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
            raise ValueError('No config set')
        {
            "dataset_type": "geoscience",
            "license_id": "cc-by-4",
            "security_classification": "PUBLIC",
            "version": "1.0",
            "update_frequency": "non-regular",
            "data_driven_application": "NO",
            "de_identified_data": "NO",
            "default_groups": ["Geoscience"],
            "deletion_reason": "Dataset deleted at harvest source",
            "author_email": "gsqopendata@resources.qld.gov.au",
        }

        try:
            config_obj = json.loads(config)
            # TODO Validation of values required for harvest

            if 'default_groups' in config_obj:
                if not isinstance(config_obj['default_groups'], list):
                    raise ValueError('default_groups must be a *list* of group'
                                     ' names/ids')
                if config_obj['default_groups'] and \
                        not isinstance(config_obj['default_groups'][0],
                                       six.string_types):
                    raise ValueError('default_groups must be a list of group '
                                     'names/ids (i.e. strings)')

                # Check if default groups exist
                context = {'model': model, 'user': toolkit.c.user}
                config_obj['default_group_dicts'] = []
                for group_name_or_id in config_obj['default_groups']:
                    try:
                        group = toolkit.get_action('group_show')(
                            context, {'id': group_name_or_id})
                        # save the dict to the config object, as we'll need it
                        # in the import_stage of every dataset
                        config_obj['default_group_dicts'].append(group)
                    except toolkit.NotFound as e:
                        raise ValueError('Default group not found')
                
                config = json.dumps(config_obj)

            if 'dataset_type' not in config_obj:
                raise ValueError('dataset_type must be set')

            if 'license_id' not in config_obj:
                raise ValueError('license_id must be set')

            if 'security_classification' not in config_obj:
                raise ValueError('security_classification must be set')

            if 'version' not in config_obj:
                raise ValueError('version must be set')

            if 'update_frequency' not in config_obj:
                raise ValueError('update_frequency must be set')

            if 'data_driven_application' not in config_obj:
                raise ValueError('data_driven_application must be set')

            if 'de_identified_data' not in config_obj:
                raise ValueError('de_identified_data must be set')

            if 'deletion_reason' not in config_obj:
                raise ValueError('deletion_reason must be set')

            if 'author_email' not in config_obj:
                raise ValueError('author_email must be set')

        except ValueError as e:
            raise e

        return config

    def modify_package_dict(self, package_dict, harvest_object):

        self._set_config(harvest_object.job.source.config)

        # TODO get default values from harvest config
        package_dict['type'] = self.config.get('dataset_type')
        package_dict['update_frequency'] = self.config.get('update_frequency')
        if not package_dict.get('author_email'):
            package_dict['author_email'] = self.config.get('author_email')

        if not package_dict.get('version'):
            package_dict['version'] = self.config.get('version')
        package_dict['data_driven_application'] = self.config.get('data_driven_application')
        package_dict['security_classification'] = self.config.get('security_classification')
        package_dict['de_identified_data'] = self.config.get('de_identified_data')
        package_dict['license_id'] = self.config.get('license_id')
        package_dict['url'] = '{0}/dataset/{1}'.format(harvest_object.source.url.rstrip('/'), package_dict.get('name'))
        # TODO Should the URL be injected into the template instead? Some notes are empty which are required so this fixes that
        package_dict['notes'] = 'URL:{0}\r\n\r\n{1}'.format(package_dict.get('url'), package_dict.get('notes', ''))
        package_dict['groups'] = self.config.get('default_group_dicts')

        # extras = package_dict.get('extras', [])
        # if extras:
        #     package_dict['extra:access_rights'] = extras.get('extra:access_rights')
        #     package_dict['extra:theme'] = extras.get('extra:theme')
        #     package_dict['survey_type'] = extras.get('survey_type')
        #     package_dict['survey_method'] = extras.get('survey_method')
        #     package_dict['survey_resolution'] = extras.get('survey_resolution')
        #     package_dict['earth_science_data_category'] = extras.get('earth_science_data_category')
        #     package_dict['status'] = extras.get('status')
        #     package_dict['borehole_sub_purpose'] = extras.get('borehole_sub_purpose')
        #     package_dict['borehole_class'] = extras.get('borehole_class')
        #     package_dict['borehole_purpose'] = extras.get('borehole_purpose')

        package_dict.pop('extras', []) 
        package_dict.pop('resources', [])

        return package_dict

    def gather_stage(self, harvest_job):
        
        self._set_config(harvest_job.source.config)

        guids_in_source = super(GeoScienceCKANHarvester, self).gather_stage(harvest_job)

        # Get the previous guids for this source
        query = model.Session.query(HarvestObject.guid, HarvestObject.package_id).\
                                        filter(HarvestObject.current==True).\
                                        filter(HarvestObject.harvest_source_id==harvest_job.source.id)

        guid_to_package_id = {guid: package_id for guid, package_id in query}

        guids_in_db = set(guid_to_package_id.keys())

        # Check datasets that need to be deleted
        guids_to_delete = set(guids_in_db) - set(guids_in_source)
        for guid in guids_to_delete:
            # Delete package
            package_id = guid_to_package_id[guid]
            context = {'model': model, 'session': model.Session,
                       'user': self._get_user_name()}
            try:
                data_dict = {"id": package_id, "deletion_reason": self.config.get('deletion_reason')}
                toolkit.get_action('package_delete')(context, data_dict)
                log.info('Deleted package {0} with guid {1}'.format(package_id, guid))

                obj = HarvestObject(guid=guid, job=harvest_job,
                                    package_id=guid_to_package_id[guid],
                                    extras=[HOExtra(key='status', value='delete')])

                model.Session.query(HarvestObject).\
                    filter_by(guid=guid).\
                    update({'current': False}, False)
                obj.save()
            except Exception as e:
                # TODO: What should we do here?
                log.error('Deleting package {0} with guid {1} failed'.format(package_id, guid))

        return guids_in_source
