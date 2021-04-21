from marshmallow import fields, validate, ValidationError
from flask import current_app as app
from . import ma, db


def is_palindrome(o):
    if not isinstance(o, str):
        return False
    if not o.isalnum():
        return False
    o = o.lower()
    chars = o[::]
    return chars == chars[::-1]

def _validate_notblank(val):
    if val.isspace():
        raise ValidationError(message=['Cannot be blank.'], field_name='content')


class Message(db.Model):
    __tablename__ = 'message'

    id            = db.Column(db.Integer, primary_key=True)
    content       = db.Column(db.String(255), nullable=False)   
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime,  
        default=db.func.current_timestamp(), 
        onupdate=db.func.current_timestamp()
    )

    def __repr__(self):
        return "Message(id='{self.id}',content='{self.content}')".format(self=self)

    def add_or_update(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, id):
         return cls.query.filter(Message.id == id).first()

    @classmethod
    def find_all(cls, page):
        return cls.query.paginate(page, app.config['MESSAGES_PER_PAGE'], False)


class MessageRequestSchema(ma.Schema):
    content = fields.String(required=True, 
        validate=[
            validate.Length(min=1, max=255, error='Lenght must be between {min} and {max} charcaters.'),
            _validate_notblank
        ])


class MessageResponseSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Message
        fields = ('id', 'date_created', 'date_modified', 'content', 'palindrome',)

    id              = fields.Integer(required=False)
    date_created    = fields.DateTime(required=False, dump_only=True)
    date_modified   = fields.DateTime(required=False, dump_only=True)
    content         = fields.String(required=True, 
                        validate=[
                            validate.Length(min=1, max=255, error='Lenght must be between {min} and {max} charcaters.'),
                            _validate_notblank
                        ])
    palindrome      = fields.Method('_palindrome', dump_only=True,  metadata={'doc_default': False})

    @staticmethod
    def _palindrome(obj):
        return is_palindrome(obj.content)
