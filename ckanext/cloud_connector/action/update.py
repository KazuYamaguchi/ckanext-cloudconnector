import ckan.model as cmodel
from pylons import config
import ckan.logic.action.update as origin
import ckanext.cloud_connector.s3.uploader as uploader
import ckan.plugins.toolkit as tk


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
    To update a resource you must be authorized to update the dataset that the
    resource belongs to.
    For further parameters see
    :py:func:`~ckan.logic.action.create.resource_create`.
    :param id: the id of the resource to update
    :type id: string
    :returns: the updated resource
    :rtype: string

    .. seealso https://github.com/ckan/ckan/blob/master/ckan/logic/action/update.py
  '''
  log.debug('Updating Resource')
  if not tk.asbool(config.get('ckan.cloud_storage_enable')) or data_dict.get('upload') == '':
    log.debug('Plugin Not Enabled or External Link')
    return origin.resource_update(context, data_dict)

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
  pkg_dict = _get_action('package_show')(context, {'id': package_id})

  for n, p in enumerate(pkg_dict['resources']):
    if p['id'] == id:
        break
  else:
    log.error('Could not find resource ' + id)
    raise NotFound(_('Resource was not found.'))


  upload = uploader.S3Upload(data_dict)

  pkg_dict['resources'][n] = data_dict

  try:
    context['defer_commit'] = True
    context['use_cache'] = False
    pkg_dict = _get_action('package_update')(context, pkg_dict)
    context.pop('defer_commit')
  except ValidationError, e:
    errors = e.error_dict['resources'][n]
    raise ValidationError(errors)

  #Delete previous file (?)
  #log.debug(previous_s3_object_url)
  upload.delete(previous_s3_object_url)

  s3_link = upload.upload(id, uploader.get_max_resource_size())
  if s3_link:
    pkg_dict['resources'][n]['url_type'] = ''
    pkg_dict['resources'][n]['url'] = 'https://s3.amazonaws.com/' + s3_link
    _get_action('package_update')(context, pkg_dict)

  model.repo.commit()
  return _get_action('resource_show')(context, {'id': id})


resource_update.__doc__ = origin.resource_update.__doc__
