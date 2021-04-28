import json
from http import HTTPStatus
from flask import jsonify, request, url_for
from flask import current_app as app

from . import api, spec
from ..exceptions import WebserviceException
from ..models import Message, MessageRequestSchema, MessageResponseSchema


spec.components.schema("MessageRequestSchema", schema=MessageRequestSchema)
spec.components.schema("MessageResponseSchema", schema=MessageResponseSchema)

@api.route('/swagger.json', methods=['GET'])
def swagger_spec():
    return jsonify(spec.to_dict())

@api.route('/messages', methods=['POST'])
def create_message():
    """
    ---
    post:
      description: Creates a Message
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MessageRequestSchema'      
      responses:
        200:
          description: Returns the created message
          content:
            application/json:
              example: {
                message: {
                  id: 0,
                  content: string,
                  palindrome: false
                }
              }
              schema:
                $ref: '#/components/schemas/MessageResponseSchema'
      tags:
        - messages
    """
    if not request.data:
        raise WebserviceException(
            message='Request body cannot be empty.', 
            code=HTTPStatus.BAD_REQUEST
        )

    data = request.get_json()
    schema = MessageRequestSchema()
    err = schema.validate(data)
    if err:
        return jsonify(errors=err), HTTPStatus.BAD_REQUEST
    
    msg = Message(content=data['content'])
    msg._save()
    result = msg._to_dict()
    app.logger.debug('Message created: {}'.format(result))

    return jsonify(message=result), HTTPStatus.CREATED


@api.route('/messages/<string:id>', methods=['GET'])
def get_message(id):
    """
    ---
    get:
      description: Requests a Message
      parameters:
      - name: id
        in: path
        required: true
        description: The id of the message to request
      responses:
        200:
          description: Returns the message
          content:
            application/json:
              example: {
                message: {
                  id: 0,
                  content: string,
                  palindrome: false
                }
              }
              schema:
                type: object
                properties:
                  message:
                    $ref: '#/components/schemas/MessageResponseSchema'
      tags:
        - messages
    """
    msg = Message._find(id)
    if not msg:
        return jsonify(error='Message Not found'), HTTPStatus.BAD_REQUEST
  
    result = msg._to_dict()
    app.logger.debug('Message with id={} retrieved.'.format(id))

    return jsonify(message=result), HTTPStatus.OK


@api.route('/messages', methods=['GET'])
def get_messages():
    """
    ---
    get:
      description: Requests a Message
      parameters:
      - name: page
        in: query
        required: false
        description: Supports pagination (10 messages per page)
      responses:
        200:
          description: Returns messages
          content:
            application/json:
              example: {
                next_url: url,
                prev_ur: url,
                messages:[
                  {
                    id: 0,
                    content: string,
                    palindrome: false
                  }
                ]
              }
              schema:
                type: object
                properties:
                  next_url:
                    type: string
                  prev_url:
                    typr: string
                  messages:
                    type: array
                    items:
                      $ref: '#/components/schemas/MessageResponseSchema'
      tags:
        - messages
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', app.config['MESSAGES_PER_PAGE'], type=int)
    msgs = Message._find_all(page, limit)

    next_url = url_for('api.get_messages', page=msgs.next_num) \
        if msgs.has_next else None
    prev_url = url_for('api.get_messages', page=msgs.prev_num) \
        if msgs.has_prev else None
    
    if next_url:
        resp.update({'next_url': next_url})
    if prev_url:
        resp.update({'prev_url': prev_url})

    resp = {'messages': [msg._to_dict() for msg in msgs.items]}

    return jsonify(resp), HTTPStatus.OK


@api.route('/messages/<string:id>', methods=['PUT'])
def update_message(id):
    """
    ---
    put:
      description: Updates a Message
      parameters:
      - name: id
        in: path
        required: true
      requestBody:
        required: true
        content:
          application/json:
            schema: 
              $ref: '#/components/schemas/MessageRequestSchema'      
      responses:
        200:
          description: Returns the updated message
          content:
            application/json:
              example: {
                message: {
                  id: 0,
                  content: string,
                  palindrome: false
                }
              }
              schema: 
                $ref: '#/components/schemas/MessageResponseSchema'
      tags:
        - messages
    """
    if not request.data:
        raise WebserviceException(
            message='Request body cannot be empty.', 
            code=HTTPStatus.BAD_REQUEST
        )

    data = request.get_json()
    schema = MessageRequestSchema()
    err = schema.validate(data)
    if err:
        return jsonify(errors=err), HTTPStatus.BAD_REQUEST

    msg = Message._update(id, data['content'])
    if not msg:
        return jsonify(error='Message Not found'), HTTPStatus.BAD_REQUEST

    result = msg._to_dict()
    app.logger.debug('Message with id={} updated.'.format(id))

    return jsonify(message=result), HTTPStatus.OK


@api.route('/messages/<string:id>', methods=['DELETE'])
def delete_message(id):
    """
    ---
    delete:
      description: Deletes a Message
      parameters:
      - name: id
        in: path
        required: true
      responses:
        200:
          description: Returns empty 
      tags:
        - messages
    """
    msg = Message._delete(id)
    if not msg:
        return jsonify(error='Message Not found'), HTTPStatus.BAD_REQUEST
    
    app.logger.debug('Message with id={} deleted.'.format(id))

    return jsonify(''), HTTPStatus.NO_CONTENT
