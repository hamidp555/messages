import json
from http import HTTPStatus
from unittest import TestCase

from app import db, create_app


class APITestCase(TestCase):

    def setUp(self):
        self.api_base_url = '/api/v1'
        self.app = create_app('TEST')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()        
        self.endpoint = self.api_base_url + '/messages'
        self.APPLICATION_JSON = 'application/json'

    def tearDown(self):
        self.app_context.pop()
    
    # create
    def test_create_message_fail_no_payload(self):
        """
        Attempt to create a message without payload
        """
        code, response = self._post(self.endpoint)
        self.assertEqual(code, HTTPStatus.BAD_REQUEST)
        self.assertTrue(
            response.get('error'), 
            'Request body cannot be empty.')
    
    def test_create_message_fail_empty_payload(self):
        """
        Attempt to create a message with empty payload
        """
        code, response = self._post(self.endpoint, {})
        self.assertEqual(code, HTTPStatus.BAD_REQUEST)
        self.assertTrue(
            response.get('errors').get('content'), 
            'Missing data for required field.')

    def test_create_message_fail_no_content(self):
        """
        Attempt to create a message null content
        """
        data = {'content': None}
        code, response = self._post(self.endpoint, data)
        self.assertEqual(code, HTTPStatus.BAD_REQUEST)
        self.assertTrue(
            response.get('errors').get('content'), 
            'Field may not be null.')

    def test_create_message_fail_empty_content(self):
        """
        Attemt to create a message with empty content
        """
        data = {'content': ''}
        code, response = self._post(self.endpoint, data)
        self.assertEqual(code, HTTPStatus.BAD_REQUEST)
        self.assertTrue(
            response.get('errors').get('content'), 
            'Lenght must be between 1 and 255 charcaters.')

    def test_create_message_fail_blank_content(self):
        """
        Attempt to create a message with blank content
        """
        data = {'content': '  '}
        code, response = self._post(self.endpoint, data)
        self.assertEqual(code, HTTPStatus.BAD_REQUEST)
        self.assertTrue(
            response.get('errors').get('content'), 
            'Cannot be blank.')

    def test_create_message_success(self):
        """
        Create a message 
        """
        data = {'content': 'test message'}
        code, response = self._post(self.endpoint, data)
        self.assertEqual(code, HTTPStatus.CREATED)

        msg = response.get('message')
        self.assertEqual(msg.get('content'), 'test message')
        self.assertEqual(msg.get('palindrome'), False)
        self.assertEqual(msg.get('id'), 1)

    # get
    def test_get_message_fail(self):
        """
        Attemt to get a message with an invalid id
        """
        code, response = self._get(self.endpoint, 12)
        self.assertEqual(code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.get('error'), 'Message Not found')

    def test_get_message_success(self):
        """
        Create a message and get it using its id
        """
        # create a message
        data = {'content': 'test message'}
        code, response = self._post(self.endpoint, data)
        self.assertEqual(code, HTTPStatus.CREATED)
        msg = response.get('message')
        id =  msg.get('id')
        palindrome = msg.get('palindrome')

        # get the message
        code, response = self._get(self.endpoint, msg.get('id'))
        self.assertEqual(code, HTTPStatus.OK)
        msg = response.get('message')
        self.assertEqual(msg.get('id'), id)
        self.assertEqual(msg.get('palindrome'), palindrome)
        self.assertEqual(msg.get('content'), data.get('content'))

    def test_get_messages_success(self):
        """
         Create 20 messages and get them all using '/messages [GET]' endpoint
         Test the pagination to make sure there are two pages, with each containing 10 messages
        """
        for i in range(20):
            data = {'content': 'test message {}'.format(i)}
            code, response = self._post(self.endpoint, data)
            self.assertEqual(code, HTTPStatus.CREATED)
        
        code, response = self._get(self.endpoint + '?page=1')
        self.assertEqual(code, HTTPStatus.OK)
        self.assertTrue(len(response.get('messages')) == 10)

        code, response = self._get(self.endpoint + '?page=2')
        self.assertEqual(code, HTTPStatus.OK)
        self.assertTrue(len(response.get('messages')) == 10)

        code, response = self._get(self.endpoint + '?page=3')
        self.assertEqual(code, HTTPStatus.OK)
        self.assertTrue(len(response.get('messages')) == 0)

    # delete
    def test_delete_message_fail(self):
        """
        Attempt to delete a message with an invalid id
        """
        code, response = self._delete(self.endpoint, 12)
        self.assertEqual(code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.get('error'), 'Message Not found')

    def test_delete_message_success(self):
        """
        Create a message and delete it using its id
        """
        # create a message
        data = {'content': 'test message'}
        code, response = self._post(self.endpoint, data)
        self.assertEqual(code, HTTPStatus.CREATED)
        msg = response.get('message')
        id = msg.get('id')

        # delete the message
        code, response = self._delete(self.endpoint, id)
        self.assertEqual(code, HTTPStatus.NO_CONTENT)

        # make sure the message is deleted
        code, response = self._get(self.endpoint, id)
        self.assertEqual(code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.get('error'), 'Message Not found')

    # update
    def test_update_message_fail(self):
        """
        Attempt to update a message with an invallid id
        """
        data = {'content': 'test message'}
        code, response = self._put(self.endpoint, 12, data)
        self.assertEqual(code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.get('error'), 'Message Not found')

    def test_update_message(self):
        """
        Ceate a message and update it using its id
        """
        # create a message
        data = {'content': 'test message'}
        code, response = self._post(self.endpoint, data)
        self.assertEqual(code, HTTPStatus.CREATED)
        msg = response.get('message')
        id =  msg.get('id')

        # update the message
        data = {'content': 'test message updated'}
        code, response = self._put(self.endpoint, msg.get('id'), data)
        self.assertEqual(code, HTTPStatus.OK)
        msg = response.get('message')
        self.assertEqual(msg.get('id'), id)
        self.assertEqual(msg.get('content'), data.get('content'))

    # utility methods
    def _post(self, endpoint=None, data=None):
        payload = None
        if data is not None:
            payload = json.dumps(data)
        
        response = self.client.post(
            endpoint, 
            data=payload, 
            content_type='application/json'
            )
        status_code = response.status_code

        body = {}
        if response.data:
            body = json.loads(response.data)

        return status_code, body

    def _put(self, endpoint=None, id=None, data = {}):
        if not id:
            return None

        payload = json.dumps(data)
        response = self.client.put(
            '{}/{}'.format(endpoint, id), 
            data=payload, 
            content_type='application/json'
            )
        status_code = response.status_code

        body = {}
        if response.data:
            body = json.loads(response.data)

        return status_code, body

    def _get(self, endpoint=None, id=None):
        url = '{}/{}'.format(endpoint, id) if id else endpoint
        response = self.client.get(url)
        status_code = response.status_code

        body = {}
        if response.data:
            body = json.loads(response.data)

        return status_code, body

    def _delete(self, endpoint=None, id=None):
        if not id:
            return None

        response = self.client.delete('{}/{}'.format(endpoint, id))
        status_code = response.status_code

        body = {}
        if response.data:
            body = json.loads(response.data)

        return status_code, body