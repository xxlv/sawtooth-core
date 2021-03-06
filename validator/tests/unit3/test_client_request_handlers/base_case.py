# Copyright 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

import unittest


class ClientHandlerTestCase(unittest.TestCase):
    """Parent for Client Request Handler tests that simplifies making requests.
    Run initialize as part of setUp, and then call make_request in each test.
    """
    def initialize(self, handler, request_proto, response_proto,
                    store=None, roots=None):
        self._identity = '1234567'
        self._handler = handler
        self._request_proto = request_proto
        self._store = store
        self.status = response_proto
        self.roots = roots

    def make_request(self, **kwargs):
        return self._handle(self._serialize(**kwargs))

    def _serialize(self, **kwargs):
        request = self._request_proto(**kwargs)
        return request.SerializeToString()

    def _handle(self, request):
        result = self._handler.handle(self._identity, request)
        return result.message_out

    def make_bad_request(self, **kwargs):
        """Truncates the protobuf request, which will break it as long as
        the protobuf is not empty.
        """
        return self._handle(self._serialize(**kwargs)[0:-1])

    def break_genesis(self):
        """Breaks the chain head causing certain "latest" requests to fail.
        Simulates what block store would look like if genesis had not been run.
        """
        del self._store.store['chain_head_id']

    def assert_all_instances(self, items, cls):
        """Checks that all items in a collection are instances of a class
        """
        for item in items:
            self.assertIsInstance(item, cls)
