import ckan.model as cmodel
import ckan.plugins as plugins
from pylons import config
import ckan.logic.action.update as origin
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

__all__ = ['resource_update']

def resource_update(context, data_dict):
    '''Update a resource.
    ::seealso https://github.com/ckan/ckan/blob/master/ckan/logic/action/update.py
    '''
    model = context['model']
    user = context['user']
    id = _get_or_bust(data_dict, "id")

    resource = model.Resource.get(id)
    previous_s3_object_url =   resource.url
    context["resource"] = resource

    if not resource:
        log.error('Could not find resource ' + id)
        raise NotFound(_('Resource was not found.'))

    _check_access('resource_update', context, data_dict)
    del context["resource"]

    package_id = resource.package.id
    pkg_dict = _get_action('package_show')(dict(context, return_type='dict'),
        {'id': package_id})

    for n, p in enumerate(pkg_dict['resources']):
        if p['id'] == id:
            break
    else:
        log.error('Could not find resource ' + id)
        raise NotFound(_('Resource was not found.'))

    for plugin in plugins.PluginImplementations(plugins.IResourceController):
        plugin.before_update(context, pkg_dict['resources'][n], data_dict)

    upload = uploader.get_resource_uploader(data_dict)

    pkg_dict['resources'][n] = data_dict
    try:
        context['defer_commit'] = True
        context['use_cache'] = False
        updated_pkg_dict = _get_action('package_update')(context, pkg_dict)
        context.pop('defer_commit')
    except ValidationError, e:
        errors = e.error_dict['resources'][n]
        raise ValidationError(errors)

    #Delete previous file (?)
    log.debug("Delete previous file: "+previous_s3_object_url)
    upload.delete(previous_s3_object_url)
    remote_filepath = upload.upload(id, uploader.get_max_resource_size())
    log.debug(remote_filepath)

    if remote_filepath:
      pkg_dict['resources'][n]['url_type'] = ''
      pkg_dict['resources'][n]['url'] = remote_filepath
      _get_action('package_update')(context, pkg_dict)

    model.repo.commit()

    resource = _get_action('resource_show')(context, {'id': id})

    for plugin in plugins.PluginImplementations(plugins.IResourceController):
        plugin.after_update(context, resource)

    return resource



resource_update.__doc__ = origin.resource_update.__doc__
