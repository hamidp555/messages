from http import HTTPStatus
from unittest import TestCase
from datetime import datetime

from app import db, create_app
from app.models import Message, MessageResponseSchema


class MessageModelTestCase(TestCase):

    def setUp(self):
        self.app = create_app('TEST')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()        
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_message(self):
        m = Message()
        m.content = 'test'
        m.add_or_update()
        self.assertTrue(
            (datetime.utcnow() - m.date_created).total_seconds() < 3)
        self.assertTrue(
            (datetime.utcnow() - m.date_modified).total_seconds() < 3)
        self.assertEqual(m.content, 'test')
        self.assertEqual(m.id, 1)

    def test_get_message(self):
        m = Message()
        m.content = 'test'
        m.add_or_update()
        m = Message.find_by_id(m.id)
        self.assertEqual(m.content, 'test')
        self.assertEqual(m.id, 1)

    def test_update_message(self):
        m = Message()
        m.content = 'test'
        m.add_or_update()
       
        m = Message.find_by_id(m.id)
        m.content = 'test updated'
        m.add_or_update()
        
        m = Message.find_by_id(m.id)
        print(m.date_created)
        print(m.date_modified)
        self.assertEqual(m.content, 'test updated')
        self.assertEqual(m.id, 1)

    def test_delete_message(self):
        m = Message()
        m.content = 'test'
        m.add_or_update()

        m = Message.find_by_id(m.id)
        m.delete()
        
        m = Message.find_by_id(m.id)
        self.assertIsNone(m)

    def test_to_json(self):
        m = Message()
        m.content = 'test'
        m.add_or_update()

        schema = MessageResponseSchema()
        m_json = schema.dump(m)
        expected_keys = ['id', 'content', 'palindrome', 'date_created', 'date_modified']
        self.assertEqual(sorted(m_json.keys()), sorted(expected_keys))





