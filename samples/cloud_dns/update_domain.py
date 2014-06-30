#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c)2012 Rackspace US, Inc.

# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import print_function

import os
import sys

import pyrax
import pyrax.exceptions as exc


pyrax.set_setting("identity_type", "rackspace")
creds_file = os.environ.get('PYRAX_CREDS_FILE', os.path.expanduser("~/.rackspace_cloud_credentials"))
pyrax.set_credential_file(creds_file)
dns = pyrax.cloud_dns

domain_name = "abc.example.edu"
try:
    dom = dns.find(name=domain_name)
except exc.NotFound:
    print("There is no DNS information for the domain '%s'." % domain_name)
    sys.exit()

print("Original TTL for '%s': %s" % (domain_name, dom.ttl))
# Add 10 minutes
new_ttl = dom.ttl + 600
dom.update(ttl=new_ttl)
dom.reload()
print("New TTL: %s" % dom.ttl)
