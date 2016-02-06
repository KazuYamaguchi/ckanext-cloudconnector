import ckan.model as cmodel
from pylons import config
import ckan.logic.action.delete as origin
import ckan.plugins.toolkit as tk
import ckan.lib.uploader as uploader

from ckan.logic import (
  NotFound,
  ValidationError,
  get_or_bust as _get_or_bust,
  check_access as _check_access,
  get_action as _get_action,
)

import logging
log = logging.getLogger(__name__)

__all__ = ['resource_delete']

def resource_delete(context, data_dict):
  ''' Delete a resource.
    .. seealso https://github.com/ckan/ckan/blob/master/ckan/logic/action/delete.py
  '''
  model = context['model']
  user = context['user']
  id = _get_or_bust(data_dict, "id")
  log.debug(id)
  resource = model.Resource.get(id)
  previous_s3_object_url =   resource.url
  ################################################################################################################
  if tk.asbool(config.get('ckanext.cloud_storage.enable')) and previous_s3_object_url.startswith("https://s3.amazonaws.com/") :
    log.debug('Deleting Remote Resource')
    log.debug(previous_s3_object_url)
    context["resource"] = resource

    if not resource:
      log.error('Could not find resource ' + id)
      raise NotFound(_('Resource was not found.'))

    _check_access('resource_delete', context, data_dict)
    package_id = resource.package.id
    pkg_dict = _get_action('package_show')(context, {'id': package_id})

    for n, p in enumerate(pkg_dict['resources']):
      if p['id'] == id:
          break
    else:
      log.error('Could not find resource ' + id)
      raise NotFound(_('Resource was not found.'))

    upload = uploader.get_resource_uploader(data_dict)
    upload.delete(previous_s3_object_url)
  else:
    log.debug('Plugin Not Enabled or External Link')
  ################################################################################################################
  return origin.resource_delete(context, data_dict)
  ################################################################################################################





resource_delete.__doc__ = origin.resource_delete.__doc__
