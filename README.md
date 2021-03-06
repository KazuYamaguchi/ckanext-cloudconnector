# CKAN CloudConnector

A fork / merge of https://github.com/DataShades/ckanext-cloudconnector and  https://github.com/okfn/ckanext-s3filestore

## Requirements

This extension was developed and tested under CKAN-2.5

For now extension supports only Amazon S3 Cloud storage. In order to use this extension you should have AWS account because AWS Key and AWS Secret Key are required for connection to Cloud.

## Installation

To install CKAN CloudConnector:

1. Activate your CKAN virtual environment, for example:

     `$ . /usr/lib/ckan/default/bin/activate`

2. Install the ckanext-cloudconnector Python package into your virtual environment:

     ```
     $ cd /some/dir/ckanext-cloudconnector
     $ python setup.py install
     ```
3. Add ``cloud_connector`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     `$ sudo service apache2 reload `

## Config Settings
This extension defines additional settings in config file

     ckanext.cloud_storage.enable=true|false                      //is connector enabled or not?
     ckanext.cloud_storage.s3.aws_key=AWS_S3_KEY                  //customer key of your AWS instance
     ckanext.cloud_storage.s3.secret_key=AWS_S3_SECRET            //secret key of your AWS instance
     ckanext.cloud_storage.s3.bucket=YOUR_BUCKET_NAME             //Name of bucket on S3
     ckanext.cloud_storage.s3.endpoint=https://s3.amazonaws.com/  // Bucket endpoint
     ckanext.cloud_storage.path=ckan                              // local path on bucket



## Development Installation

To install CKAN CloudConnector for development, activate your CKAN virtualenv and
do:

     $ cd /some/dir/ckanext-cloudconnector
     $ python setup.py develop

All dependencies will be installed automatically

## Copying and License

This material is copyright &copy; 2015 Link Web Services Pty Ltd

It is open and licensed under the GNU Affero General Public License (AGPL) v3.0 whose full text may be found at:

[http://www.fsf.org/licensing/licenses/agpl-3.0.html](http://www.fsf.org/licensing/licenses/agpl-3.0.html)


## Notes

The original Web administration from https://github.com/DataShades/ckanext-cloudconnector was removed from this fork. Probably it is a bad idea to publish aws key and secret_key as runtime editable options
> Only configuration options which are not critical, sensitive or could cause the CKAN instance to break should be made runtime-editable.
([Making configuration options runtime-editable](http://docs.ckan.org/en/latest/extensions/remote-config-update.html) )

Config options are available via rest api
[ckan.logic.action.get.config_option_show](http://docs.ckan.org/en/latest/api/index.html#ckan.logic.action.get.config_option_show)  
> Show the current value of a particular configuration option.

This fork disables the runtime editable option.

### Other Relevant Information:
* [Editing Bucket Permissions](http://docs.aws.amazon.com/AmazonS3/latest/UG/EditingBucketPermissions.html)
