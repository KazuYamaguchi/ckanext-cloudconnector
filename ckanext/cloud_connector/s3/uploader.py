import pylons
import logging
from md5 import md5
from ckan.lib.uploader import ResourceUpload

from boto.s3.connection import S3Connection
from boto.s3.key import Key
import ckan.model as model
config = pylons.config
log = logging.getLogger(__name__)

from ckan.lib.uploader import (
  get_storage_path,
  get_max_image_size,
  get_max_resource_size,
)
from ckan.lib.base import abort



class S3Upload(ResourceUpload):

  def __init__(self, resource):
    uploaded_file = resource.get('upload')
    if uploaded_file != None:
      self.content_type = uploaded_file.type
    else:
      self.content_type = None
    super(S3Upload, self).__init__(resource)

    self.failover = config.get('ckanext.cloud_storage.failover')

    AWS_KEY = config.get('ckanext.cloud_storage.s3.aws_key')
    AWS_SECRET = config.get('ckanext.cloud_storage.s3.secret_key')
    _s3_conn = S3Connection(AWS_KEY, AWS_SECRET) if AWS_KEY and AWS_SECRET else None
    self.s3_conn = _s3_conn
    if not _s3_conn:
      return
    #self.bucket_name = config.get('ckan.site_id', 'ckan_site_id') + bucket_postfix
    self.bucket_name = config.get('ckanext.cloud_storage.s3.bucket')
    bucket = _s3_conn.lookup(self.bucket_name)
    if not bucket:
      try:
        log.debug('Creating Bucket')
        bucket = _s3_conn.create_bucket(self.bucket_name)
      except Exception, e:
        log.warn(e)
        if self.failover == '1':
          self.s3_conn = None
          return
        elif self.failover == '2':
          raise e
    else:
        log.debug('Bucket Found')

    self.bucket = bucket


  def upload(self, id, max_size=10):
    if not self.s3_conn or not self.bucket:
      if self.failover == '1':
        return super(S3Upload, self).upload(id,max_size)
      elif self.failover == '2':
        abort('404', 'Problem with cloud')
    try:
      bucket_key = Key(self.bucket)
      if self.filename:
        storage_path = config.get('ckanext.cloud_storage.path', '')
        directory = 'resource'
        filepath = '/'.join((storage_path, directory, id, self.filename))
        bucket_key.key = filepath
        if self.content_type:
          bucket_key.content_type = self.content_type
        self.upload_file.seek(0)
        bucket_key.set_contents_from_file(self.upload_file)
        bucket_key.make_public()
        bucket_key.close()
      return self.bucket_name + '/' + filepath
    except Exception, e:
      log.warn(e)


  def delete(self, s3_previous_object_url):
      if not self.s3_conn or not self.bucket:
        if self.failover == '1':
          return super(S3Upload, self).upload(id,max_size)
        elif self.failover == '2':
          abort('404', 'Problem with cloud')
      try:
        bucket_key = Key(self.bucket)
        directory = 'resource'
        file_key = s3_previous_object_url[s3_previous_object_url.find(directory):]
        log.debug( s3_previous_object_url)
        log.debug( file_key )
        if file_key:
            log.debug("Deleting object" )
            self.bucket.delete_key(file_key)
            log.debug("Object Deleted" )
      except Exception, e:
        log.warn(e)



  def _clean_whole_bucket(self):
    if self.s3_conn or self.bucket:
      for key in self.bucket.list():
        key.delete()
