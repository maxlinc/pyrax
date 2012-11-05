#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from pyrax.cf_wrapper.client import FolderUploader
from pyrax.cf_wrapper.container import Container
from pyrax.cf_wrapper.storage_object import StorageObject
from pyrax.cloud_databases import CloudDatabaseClient
from pyrax.cloud_databases import CloudDatabaseInstance
from pyrax.cloud_blockstorage import CloudBlockStorageClient
from pyrax.cloud_blockstorage import CloudBlockStorageVolume
from pyrax.cloud_blockstorage import CloudBlockStorageSnapshot

import pyrax.exceptions as exc
from pyrax.rax_identity import Identity
import pyrax.utils as utils


class FakeResponse(dict):
    headers = {}
    body = ""
    status = 200
    reason = "Oops"

    def getheaders(self):
        return self.headers

    def read(self):
        return "Line1\nLine2"

    def get(self, arg):
        pass


class FakeClient(object):
    user_agent = "Fake"
    USER_AGENT = "Fake"


class FakeContainer(Container):
    def _fetch_cdn_data(self):
        pass


class FakeStorageObject(StorageObject):
    def __init__(self, client, container, name=None, total_bytes=None, content_type=None,
            last_modified=None, etag=None, attdict=None):
        """
        The object can either be initialized with individual params, or by
        passing the dict that is returned by swiftclient.
        """
        self.client = client
        self.container = container
        self.name = name
        self.total_bytes = total_bytes
        self.content_type = content_type
        self.last_modified = last_modified
        self.etag = etag
        if attdict:
            self._read_attdict(attdict)


class FakeNode(object):
    pass


class FakeVirtualIP(object):
    pass


class FakeLoadBalancerResource(object):
    pass


class FakeLoadBalancers(object):
    resource_class = FakeLoadBalancerResource


class FakeServer(object):
    id = utils.random_name()


class FakeService(object):
    user_agent = "FakeService"
    USER_AGENT = "FakeService"

    def __init__(self, *args, **kwargs):
        self.client = FakeClient()
        self.Node = FakeNode
        self.VirtualIP = FakeVirtualIP
        self.loadbalancers = FakeLoadBalancers()

    def authenticate(self):
        pass

    def get_protocols(self):
        return ["HTTP"]

    def get_algorithms(self):
        return ["RANDOM"]

    def get_usage(self):
        pass


class FakeFolderUploader(FolderUploader):
    def __init__(self, *args, **kwargs):
        super(FakeFolderUploader, self).__init__(*args, **kwargs)
        # Useful for when we mock out the run() method.
        self.actual_run = self.run
        self.run = self.fake_run

    def fake_run(self):
        pass


class FakeEntryPoint(object):
    def __init__(self, name):
        self.name = name

    def load(self):
        def dummy(*args, **kwargs):
            return self.name
        return dummy

fakeEntryPoints = [FakeEntryPoint("a"), FakeEntryPoint("b"), FakeEntryPoint("c")]


class FakeManager(object):
    api = FakeClient()
    def list(self):
        pass
    def get(self, item):
        pass
    def delete(self, item):
        pass
    def create(self, *args, **kwargs):
        pass
    def find(self, *args, **kwargs):
        pass
    def action(self, item, action_type, body={}):
        pass


class FakeException(BaseException):
    pass


class FakeServiceCatalog(object):
    def __init__(self, *args, **kwargs):
        pass
    def get_token(self):
        return "fake_token"
    def url_for(self, attr=None, filter_value=None,
            service_type=None, endpoint_type="publicURL",
            service_name=None, volume_service_name=None):
        if filter_value == "ALL":
            raise exc.AmbiguousEndpoints
        elif filter_value == "KEY":
            raise KeyError
        elif filter_value == "EP":
            raise exc.EndpointNotFound
        return "http://example.com"


class FakeKeyring(object):
    password_set = False
    def get_password(self, *args, **kwargs):
        return "FAKE_TOKEN|FAKE_URL"
    def set_password(self, *args, **kwargs):
        self.password_set = True


class FakeEntity(object):
    def __init__(self, *args, **kwargs):
        pass
    def get(self, *args, **kwargs):
        pass


class FakeDatabaseInstance(CloudDatabaseInstance):
    def __init__(self, *args, **kwargs):
        self.id = utils.random_name()
        self.volume = FakeEntity()
        self.manager = FakeManager()
        self.manager.api = FakeDatabaseClient()
        self._database_manager = FakeManager()
        self._user_manager = FakeManager()


class FakeDatabaseClient(CloudDatabaseClient):
    def __init__(self, *args, **kwargs):
        self._flavor_manager = FakeManager()
        super(FakeDatabaseClient, self).__init__("fakeuser",
                "fakepassword", *args, **kwargs)


class FakeBlockStorageVolume(CloudBlockStorageVolume):
    def __init__(self, *args, **kwargs):
        self.id = utils.random_name()
        self.manager = FakeManager()
        self._snapshot_manager = FakeManager()


class FakeBlockStorageSnapshot(CloudBlockStorageSnapshot):
    def __init__(self, *args, **kwargs):
        self.id = utils.random_name()


class FakeBlockStorageClient(CloudBlockStorageClient):
    def __init__(self, *args, **kwargs):
        self._types_manager = FakeManager()
        self._snaps_manager = FakeManager()
        super(FakeBlockStorageClient, self).__init__("fakeuser",
                "fakepassword", *args, **kwargs)


class FakeIdentity(Identity):
    """Class that returns canned authentication responses."""
    def __init__(self, *args, **kwargs):
        super(FakeIdentity, self).__init__(*args, **kwargs)
        self._good_username = "fakeuser"
        self._good_api_key = "fakeapikey"
    def authenticate(self):
        if ((self.username == self._good_username) and
                (self.api_key == self._good_api_key)):
            self._parse_response(self.fake_response())
            self.authenticated = True
        else:
            self.authenticated = False
            raise exc.AuthenticationFailed("No match for '%s'/'%s' username/api_key"
                    % (self.username, self.api_key))
    def get_token(self, force=False):
        return self.token
    def fake_response(self):
        return fake_identity_response


class FakeIdentityResponse(FakeResponse):
    def read(self):
        return json.dumps(fake_identity_response)


fake_identity_response = {u'access':
        {u'serviceCatalog': [
            {u'endpoints': [{u'publicURL': u'https://ord.loadbalancers.api.rackspacecloud.com/v1.0/000000',
                              u'region': u'ORD',
                              u'tenantId': u'000000'},
                             {u'publicURL': u'https://dfw.loadbalancers.api.rackspacecloud.com/v1.0/000000',
                              u'region': u'DFW',
                              u'tenantId': u'000000'}],
              u'name': u'cloudLoadBalancers',
              u'type': u'rax:load-balancer'},
             {u'endpoints': [{u'internalURL': u'https://snet-storage101.dfw1.clouddrive.com/v1/MossoCloudFS_ffffffff-ffff-ffff-ffff-ffffffffffff',
                              u'publicURL': u'https://storage101.dfw1.clouddrive.com/v1/MossoCloudFS_ffffffff-ffff-ffff-ffff-ffffffffffff',
                              u'region': u'DFW',
                              u'tenantId': u'MossoCloudFS_ffffffff-ffff-ffff-ffff-ffffffffffff'},
                             {u'internalURL': u'https://snet-storage101.ord1.clouddrive.com/v1/MossoCloudFS_ffffffff-ffff-ffff-ffff-ffffffffffff',
                              u'publicURL': u'https://storage101.ord1.clouddrive.com/v1/MossoCloudFS_ffffffff-ffff-ffff-ffff-ffffffffffff',
                              u'region': u'ORD',
                              u'tenantId': u'MossoCloudFS_ffffffff-ffff-ffff-ffff-ffffffffffff'}],
              u'name': u'cloudFiles',
              u'type': u'object-store'},
             {u'endpoints': [{u'publicURL': u'https://dfw.servers.api.rackspacecloud.com/v2/000000',
                              u'region': u'DFW',
                              u'tenantId': u'000000',
                              u'versionId': u'2',
                              u'versionInfo': u'https://dfw.servers.api.rackspacecloud.com/v2',
                              u'versionList': u'https://dfw.servers.api.rackspacecloud.com/'},
                             {u'publicURL': u'https://ord.servers.api.rackspacecloud.com/v2/000000',
                              u'region': u'ORD',
                              u'tenantId': u'000000',
                              u'versionId': u'2',
                              u'versionInfo': u'https://ord.servers.api.rackspacecloud.com/v2',
                              u'versionList': u'https://ord.servers.api.rackspacecloud.com/'}],
              u'name': u'cloudServersOpenStack',
              u'type': u'compute'},
             {u'endpoints': [{u'publicURL': u'https://dns.api.rackspacecloud.com/v1.0/000000',
                              u'tenantId': u'000000'}],
              u'name': u'cloudDNS',
              u'type': u'rax:dns'},
             {u'endpoints': [{u'publicURL': u'https://dfw.databases.api.rackspacecloud.com/v1.0/000000',
                              u'region': u'DFW',
                              u'tenantId': u'000000'},
                             {u'publicURL': u'https://ord.databases.api.rackspacecloud.com/v1.0/000000',
                              u'region': u'ORD',
                              u'tenantId': u'000000'}],
              u'name': u'cloudDatabases',
              u'type': u'rax:database'},
             {u'endpoints': [{u'publicURL': u'https://servers.api.rackspacecloud.com/v1.0/000000',
                              u'tenantId': u'000000',
                              u'versionId': u'1.0',
                              u'versionInfo': u'https://servers.api.rackspacecloud.com/v1.0',
                              u'versionList': u'https://servers.api.rackspacecloud.com/'}],
              u'name': u'cloudServers',
              u'type': u'compute'},
             {u'endpoints': [{u'publicURL': u'https://cdn1.clouddrive.com/v1/MossoCloudFS_ffffffff-ffff-ffff-ffff-ffffffffffff',
                              u'region': u'DFW',
                              u'tenantId': u'MossoCloudFS_ffffffff-ffff-ffff-ffff-ffffffffffff'},
                             {u'publicURL': u'https://cdn2.clouddrive.com/v1/MossoCloudFS_ffffffff-ffff-ffff-ffff-ffffffffffff',
                              u'region': u'ORD',
                              u'tenantId': u'MossoCloudFS_ffffffff-ffff-ffff-ffff-ffffffffffff'}],
              u'name': u'cloudFilesCDN',
              u'type': u'rax:object-cdn'},
             {u'endpoints': [{u'publicURL': u'https://monitoring.api.rackspacecloud.com/v1.0/000000',
                              u'tenantId': u'000000'}],
              u'name': u'cloudMonitoring',
              u'type': u'rax:monitor'}],
u'token': {u'expires': u'2222-02-22T22:22:22.000-02:00',
    u'id': u'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
    u'tenant': {u'id': u'000000', u'name': u'000000'}},
u'user': {u'RAX-AUTH:defaultRegion': u'',
   u'id': u'123456',
   u'name': u'someuser',
   u'roles': [{u'description': u'User Admin Role.',
               u'id': u'3',
               u'name': u'identity:user-admin'}]}}}
