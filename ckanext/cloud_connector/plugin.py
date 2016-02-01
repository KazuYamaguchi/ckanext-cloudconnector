import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from pylons import config

import ckanext.cloud_connector.action as action
import ckan.model as model
import logging
log = logging.getLogger(__name__)

class S3Plugin(plugins.SingletonPlugin):
  plugins.implements(plugins.IActions)


  def get_actions(self):
    log.debug('Setting up actions')
    return {
      'resource_create': action.resource_create,
      'resource_update': action.resource_update,
      'resource_delete': action.resource_delete,
    }


  
