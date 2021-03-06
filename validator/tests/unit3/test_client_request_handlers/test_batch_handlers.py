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

import sawtooth_validator.state.client_handlers as handlers
from sawtooth_validator.protobuf import client_pb2
from sawtooth_validator.protobuf.batch_pb2 import Batch
from test_client_request_handlers.base_case import ClientHandlerTestCase
from test_client_request_handlers.mocks import MockBlockStore


class TestBatchListRequests(ClientHandlerTestCase):
    def setUp(self):
        store = MockBlockStore()
        self.initialize(
            handlers.BatchListRequest(store),
            client_pb2.ClientBatchListRequest,
            client_pb2.ClientBatchListResponse,
            store=store)

    def test_batch_list_request(self):
        """Verifies requests for batch lists without parameters work properly.

        Queries the default mock block store with three blocks:
            {header_signature: 'B-2', batches: [{header_signature: 'b-2' ...}] ...}
            {header_signature: 'B-1', batches: [{header_signature: 'b-1' ...}] ...}
            {header_signature: 'B-0', batches: [{header_signature: 'b-0' ...}] ...}

        Expects to find:
            - a status of OK
            - a head_id of 'B-2' (the latest)
            - a list of batches with 3 items
            - the items are instances of Batch
            - the first item has a header_signature of 'b-2'
        """
        response = self.make_request()

        self.assertEqual(self.status.OK, response.status)
        self.assertEqual('B-2', response.head_id)
        self.assertEqual(3, len(response.batches))
        self.assert_all_instances(response.batches, Batch)
        self.assertEqual('b-2', response.batches[0].header_signature)

    def test_batch_list_bad_request(self):
        """Verifies requests for lists of batches break with bad protobufs.

        Expects to find:
            - a status of INTERNAL_ERROR
            - that batches and head_id are missing
        """
        response = self.make_bad_request(head_id='B-1')

        self.assertEqual(self.status.INTERNAL_ERROR, response.status)
        self.assertFalse(response.head_id)
        self.assertFalse(response.batches)

    def test_batch_list_bad_request(self):
        """Verifies requests for lists of batches break with no genesis.

        Expects to find:
            - a status of NOT_READY
            - that batches and head_id are missing
        """
        self.break_genesis()
        response = self.make_request()

        self.assertEqual(self.status.NOT_READY, response.status)
        self.assertFalse(response.head_id)
        self.assertFalse(response.batches)

    def test_batch_list_with_head(self):
        """Verifies requests for lists of batches work properly with a head id.

        Queries the default mock block store with '1' as the head:
            {header_signature: 'B-1', batches: [{header_signature: 'b-1' ...}] ...}
            {header_signature: 'B-0', batches: [{header_signature: 'b-0' ...}] ...}

        Expects to find:
            - a status of OK
            - a head_id of 'B-1'
            - a list of batches with 2 items
            - the items are instances of Batch
            - the first item has a header_signature of 'b-1'
        """
        response = self.make_request(head_id='B-1')

        self.assertEqual(self.status.OK, response.status)
        self.assertEqual('B-1', response.head_id)
        self.assertEqual(2, len(response.batches))
        self.assert_all_instances(response.batches, Batch)
        self.assertEqual('b-1', response.batches[0].header_signature)

    def test_batch_list_with_bad_head(self):
        """Verifies requests for lists of batches break with a bad head.

        Expects to find:
            - a status of NO_ROOT
            - that batches and head_id are missing
        """
        response = self.make_request(head_id='bad')

        self.assertEqual(self.status.NO_ROOT, response.status)
        self.assertFalse(response.head_id)
        self.assertFalse(response.batches)

    def test_batch_list_filtered_by_ids(self):
        """Verifies requests for lists of batches work filtered by batch ids.

        Queries the default mock block store with three blocks:
            {header_signature: 'B-2', batches: [{header_signature: 'b-2' ...}] ...}
            {header_signature: 'B-1', batches: [{header_signature: 'b-1' ...}] ...}
            {header_signature: 'B-0', batches: [{header_signature: 'b-0' ...}] ...}

        Expects to find:
            - a status of OK
            - a head_id of 'B-2', the latest
            - a list of batches with 2 items
            - the items are instances of Batch
            - the first item has a header_signature of 'b-0'
            - the second item has a header_signature of 'b-2'
        """
        response = self.make_request(batch_ids=['b-0', 'b-2'])

        self.assertEqual(self.status.OK, response.status)
        self.assertEqual('B-2', response.head_id)
        self.assertEqual(2, len(response.batches))
        self.assert_all_instances(response.batches, Batch)
        self.assertEqual('b-0', response.batches[0].header_signature)
        self.assertEqual('b-2', response.batches[1].header_signature)

    def test_batch_list_by_bad_ids(self):
        """Verifies batch list requests break when ids are not found.

        Queries the default mock block store with three blocks:
            {header_signature: 'B-2', batches: [{header_signature: 'b-2' ...}] ...}
            {header_signature: 'B-1', batches: [{header_signature: 'b-1' ...}] ...}
            {header_signature: 'B-0', batches: [{header_signature: 'b-0' ...}] ...}

        Expects to find:
            - a status of NO_RESOURCE
            - a head_id of 'B-2', the latest
            - that batches is missing
        """
        response = self.make_request(batch_ids=['bad', 'also-bad'])

        self.assertEqual(self.status.NO_RESOURCE, response.status)
        self.assertEqual('B-2', response.head_id)
        self.assertFalse(response.batches)

    def test_batch_list_by_good_and_bad_ids(self):
        """Verifies batch list requests work filtered by good and bad ids.

        Queries the default mock block store with three blocks:
            {header_signature: 'B-2', batches: [{header_signature: 'b-2' ...}] ...}
            {header_signature: 'B-1', batches: [{header_signature: 'b-1' ...}] ...}
            {header_signature: 'B-0', batches: [{header_signature: 'b-0' ...}] ...}

        Expects to find:
            - a status of OK
            - a head_id of 'B-2', the latest
            - a list of batches with 1 items
            - that item is an instances of Batch
            - that item has a header_signature of 'b-1'
        """
        response = self.make_request(batch_ids=['bad', 'b-1'])

        self.assertEqual(self.status.OK, response.status)
        self.assertEqual('B-2', response.head_id)
        self.assertEqual(1, len(response.batches))
        self.assert_all_instances(response.batches, Batch)
        self.assertEqual('b-1', response.batches[0].header_signature)

    def test_batch_list_by_head_and_ids(self):
        """Verifies batch list requests work with both head and batch ids.

        Queries the default mock block store with '1' as the head:
            {header_signature: 'B-1', batches: [{header_signature: 'b-1' ...}] ...}
            {header_signature: 'B-0', batches: [{header_signature: 'b-0' ...}] ...}

        Expects to find:
            - a status of OK
            - a head_id of 'B-1'
            - a list of batches with 1 item
            - that item is an instance of Batch
            - that item has a header_signature of 'b-0'
        """
        response = self.make_request(head_id='B-1', batch_ids=['b-0'])

        self.assertEqual(self.status.OK, response.status)
        self.assertEqual('B-1', response.head_id)
        self.assertEqual(1, len(response.batches))
        self.assert_all_instances(response.batches, Batch)
        self.assertEqual('b-0', response.batches[0].header_signature)

    def test_batch_list_head_ids_mismatch(self):
        """Verifies batch list requests break when ids not found with head.

        Queries the default mock block store with '0' as the head:
            {header_signature: 'B-0', batches: [{header_signature: 'b-0' ...}] ...}

        Expects to find:
            - a status of NO_RESOURCE
            - a head_id of 'B-0'
            - that batches is missing
        """
        response = self.make_request(head_id='B-0', batch_ids=['b-1', 'b-2'])

        self.assertEqual(self.status.NO_RESOURCE, response.status)
        self.assertEqual('B-0', response.head_id)
        self.assertFalse(response.batches)


class TestBatchGetRequests(ClientHandlerTestCase):
    def setUp(self):
        store = MockBlockStore()
        self.initialize(
            handlers.BatchGetRequest(store),
            client_pb2.ClientBatchGetRequest,
            client_pb2.ClientBatchGetResponse)

    def test_batch_get_request(self):
        """Verifies requests for a specific batch by id work properly.

        Queries the default three block mock store for a batch id of 'b-1'.
        Expects to find:
            - a status of OK
            - a batch property which is an instances of Batch
            - the batch has a header_signature of 'b-1'
        """
        response = self.make_request(batch_id='b-1')

        self.assertEqual(self.status.OK, response.status)
        self.assertIsInstance(response.batch, Batch)
        self.assertEqual('b-1', response.batch.header_signature)

    def test_batch_get_bad_request(self):
        """Verifies requests for a specific batch break with a bad protobuf.

        Expects to find:
            - a status of INTERNAL_ERROR
            - that the Batch returned, when serialized, is actually empty
        """
        response = self.make_bad_request(batch_id='b-1')

        self.assertEqual(self.status.INTERNAL_ERROR, response.status)
        self.assertFalse(response.batch.SerializeToString())

    def test_batch_get_with_bad_id(self):
        """Verifies requests for a specific batch break with a bad id.

        Expects to find:
            - a status of NO_RESOURCE
            - that the Batch returned, when serialized, is actually empty
        """
        response = self.make_request(batch_id='bad')

        self.assertEqual(self.status.NO_RESOURCE, response.status)
        self.assertFalse(response.batch.SerializeToString())

    def test_batch_get_with_block_id(self):
        """Verifies requests for a batch break properly with a block id.

        Expects to find:
            - a status of INVALID_ID
            - that the Batch returned, when serialized, is actually empty
        """
        response = self.make_request(batch_id='B-1')

        self.assertEqual(self.status.INVALID_ID, response.status)
        self.assertFalse(response.batch.SerializeToString())
