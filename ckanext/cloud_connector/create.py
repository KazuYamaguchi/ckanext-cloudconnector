import os
import ckan.model as model
from pylons import config
import ckan.logic.action.create as origin
import ckan.plugins.toolkit as tk
import ckan.plugins as plugins
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

__all__ = ['resource_create']

def resource_create(context, data_dict):
    '''
      .. sealso https://github.com/ckan/ckan/blob/master/ckan/logic/action/create.py
    '''
    model = context['model']
    user = context['user']

    package_id = _get_or_bust(data_dict, 'package_id')
    _get_or_bust(data_dict, 'url')

    pkg_dict = _get_action('package_show')(
        dict(context, return_type='dict'),
        {'id': package_id})

    _check_access('resource_create', context, data_dict)

    for plugin in plugins.PluginImplementations(plugins.IResourceController):
        plugin.before_create(context, data_dict)

    if not 'resources' in pkg_dict:
        pkg_dict['resources'] = []

    upload = uploader.get_resource_uploader(data_dict)
    pkg_dict['resources'].append(data_dict)
    try:
        context['defer_commit'] = True
        context['use_cache'] = False
        _get_action('package_update')(context, pkg_dict)
        context.pop('defer_commit')
    except ValidationError, e:
        errors = e.error_dict['resources'][-1]
        raise ValidationError(errors)

    ## Get out resource_id resource from model as it will not appear in
    ## package_show until after commit
    remote_filepath = upload.upload(context['package'].resources[-1].id,   uploader.get_max_resource_size())
    if remote_filepath:
        log.debug(remote_filepath)
        pkg_dict['resources'][-1]['url_type'] = ''
        pkg_dict['resources'][-1]['url'] = remote_filepath
    _get_action('package_update')(context, pkg_dict)
    model.repo.commit()

    ##  Run package show again to get out actual last_resource
    updated_pkg_dict = _get_action('package_show')(context, {'id': package_id})
    resource = updated_pkg_dict['resources'][-1]

    for plugin in plugins.PluginImplementations(plugins.IResourceController):
        plugin.after_create(context, resource)

    return resource
