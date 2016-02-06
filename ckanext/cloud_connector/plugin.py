import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from pylons import config

import ckanext.cloud_connector.create as create
import ckanext.cloud_connector.update as update

import ckanext.cloud_connector.uploader

import ckan.model as model
import logging
log = logging.getLogger(__name__)

class S3Plugin(plugins.SingletonPlugin):
  plugins.implements(plugins.IActions)
  plugins.implements(plugins.IUploader)


  def get_actions(self):
    log.debug('Setting up actions')
    return {
      'resource_create': create.resource_create,
      'resource_update': update.resource_update,
      #'resource_delete': action.resource_delete,
    }

  # IUploader
  # see https://github.com/okfn/ckanext-s3filestore
  def get_resource_uploader(self, data_dict):
      '''Return an uploader object used to upload resource files.'''
      return ckanext.cloud_connector.uploader.S3ResourceUploader(data_dict)

  def get_uploader(self, upload_to, old_filename=None):
    '''Return an uploader object used to upload general files.'''
    return ckanext.cloud_connector.uploader.S3Uploader(upload_to, old_filename)
