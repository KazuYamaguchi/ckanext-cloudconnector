import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from pylons import config

import ckanext.cloud_connector.action as action
import ckan.model as model
import logging
log = logging.getLogger(__name__)

from ckanext.cloud_connector.s3.uploader import s3_option_items

class S3Plugin(plugins.SingletonPlugin):
  plugins.implements(plugins.IActions)
  plugins.implements(plugins.IRoutes, inherit=True)

  #See Notes on README.md
  #plugins.implements(plugins.IConfigurer)

  def get_actions(self):
    log.debug('Setting up actions')
    return {
      'resource_create': action.resource_create,
      'resource_update': action.resource_update,
    }

  '''
  def update_config(self, config):
    toolkit.add_template_directory(config, 'templates')
    toolkit.add_resource('fanstatic', 'cloud_connector')
  '''
  '''
  # http://docs.ckan.org/en/latest/extensions/remote-config-update.html
  def update_config_schema(self, schema):

    ignore_missing = toolkit.get_validator('ignore_missing')
    is_positive_integer = toolkit.get_validator('is_positive_integer')

    schema.update(s3_option_items)
    return schema
  '''

  def before_map(self, map):
    map.connect(
      'cloud_connector_config', '/ckan-admin/cloud_connector_config',
      controller='ckanext.cloud_connector.s3.controller:S3Controller',
      action='config', ckan_icon='cloud')
    map.connect(
      'cloud_connector_config_reset', '/ckan-admin/cloud_connector_config_reset',
      controller='ckanext.cloud_connector.s3.controller:S3Controller',
      action='reset_config')
    return map
