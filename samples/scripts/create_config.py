import pystache
import os

template = open('.rackspace_cloud_credentials.sample', 'r').read()
config = pystache.render(template, dict(os.environ))
open('.rackspace_cloud_credentials', 'w').write(config)
