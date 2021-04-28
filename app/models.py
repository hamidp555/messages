from marshmallow import fields, validate, ValidationError
from flask import current_app as app
from datetime import datetime

from . import ma, db


def is_palindrome(o):
    if not isinstance(o, str):
        return False
    if o and not o.isalnum():
        return False
    o = o.lower()
    chars = o[::]
    return chars == chars[::-1]

def _validate_notblank(val):
    if val.isspace():
        raise ValidationError(message=['Cannot be blank.'], field_name='content')


class Properties(db.EmbeddedDocument):
    palindrome = db.BooleanField(required=True)
    length = db.IntField(required=True)


class Message(db.Document):
    content = db.StringField(required=True)
    date_created = db.DateTimeField(required=True, default=datetime.now())
    date_modified =  db.DateTimeField(required=True, default=datetime.now())
    properties = db.EmbeddedDocumentField(Properties)

    def __repr__(self):
        return '<Message {}>'.format(self.content)

    def _save(self):
        props = Properties(
            palindrome=is_palindrome(self.content), 
            length=len(self.content)
        )
        self.properties = props
        self.save()

    @staticmethod
    def _update(id, content):
        msg = Message._find(id)
        if not msg:
            return False

        props = Properties(
            palindrome=is_palindrome(content), 
            length=len(content)
        )
        msg.update(
                content=content,
                properties=props,
                date_modified=datetime.now()
            )
        return msg
        
    @staticmethod
    def _delete(id):
        msg = Message._find(id)
        if not msg:
            return False

        msg.delete()
        return True

    @staticmethod
    def _find(id):
        return Message.objects(id=id).first()

    @staticmethod
    def _find_all(page, limit):
        return Message.objects.paginate(page, limit)

    def _to_dict(self):
        return {
            'id': str(self.id),
            'content': self.content,
            'date_created': self.date_created.isoformat(),
            'date_modified': self.date_modified.isoformat(),
            'properties': {
                'palindrome': self.properties.palindrome,
                'length': self.properties.length
            }
        }


class MessageRequestSchema(ma.Schema):
    content = fields.String(required=True, 
        validate=[
            validate.Length(min=1, max=255, error='Lenght must be between {min} and {max} charcaters.'),
            _validate_notblank
        ])


class PropertiesSchema(ma.Schema):
    palindrome = fields.Boolean()
    length = fields.Integer()


class MessageResponseSchema(ma.Schema):
    class Meta:
        model = Message
        fields = ('id', 'date_created', 'date_modified', 'content', 'properties',)

    id              = fields.Integer()
    date_created    = fields.DateTime(dump_only=True)
    date_modified   = fields.DateTime(dump_only=True)
    content         = fields.String()
    properties      = fields.Nested(PropertiesSchema, dump_only=True)

