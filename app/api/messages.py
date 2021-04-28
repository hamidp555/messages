import json
from http import HTTPStatus
from flask import jsonify, request, url_for
from flask import current_app as app

from . import api, spec
from ..exceptions import WebserviceException
from ..models import Message, MessageResponseSchema, MessageRequestSchema
from ..main.auth import requires_auth


spec.components.schema("MessageRequestSchema", schema=MessageRequestSchema)
spec.components.schema("MessageResponseSchema", schema=MessageResponseSchema)

@api.route('/swagger.json', methods=['GET'])
@requires_auth
def swagger_spec():
    return jsonify(spec.to_dict())

@api.route('/messages', methods=['POST'])
@requires_auth
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
    
    msg = Message()
    msg.content = data['content']
    msg.add_or_update()

    schema = MessageResponseSchema()
    result = schema.dump(msg)
    app.logger.debug('Message created: {}'.format(result))

    return jsonify(message=result), HTTPStatus.CREATED


@api.route('/messages/<int:id>', methods=['GET'])
@requires_auth
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
    msg = Message.find_by_id(id)
    if not msg:
        return jsonify(error='Message Not found'), HTTPStatus.BAD_REQUEST
  
    schema = MessageResponseSchema()
    app.logger.debug('Message with id={} retrieved.'.format(msg.id))

    return jsonify(message=schema.dump(msg)), HTTPStatus.OK


@api.route('/messages', methods=['GET'])
@requires_auth
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
    msgs = Message.find_all(page)
    schema = MessageResponseSchema()

    next_url = url_for('api.get_messages', page=msgs.next_num) \
        if msgs.has_next else None
    prev_url = url_for('api.get_messages', page=msgs.prev_num) \
        if msgs.has_prev else None
    
    resp = {'messages': [schema.dump(msg) for msg in msgs.items]}
    if next_url:
        resp.update({'next_url': next_url})
    if prev_url:
        resp.update({'prev_url': prev_url})

    return jsonify(resp), HTTPStatus.OK


@api.route('/messages/<int:id>', methods=['PUT'])
@requires_auth
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
    msg = Message.find_by_id(id)
    if not msg:
        return jsonify(error='Message Not found'), HTTPStatus.BAD_REQUEST

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
    
    msg.content = data['content']
    msg.add_or_update()
    schema = MessageResponseSchema()
    app.logger.debug('Message with id={} updated.'.format(msg.id))

    return jsonify(message=schema.dump(msg)), HTTPStatus.OK


@api.route('/messages/<int:id>', methods=['DELETE'])
@requires_auth
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
    msg = Message.find_by_id(id)
    if not msg:
        return jsonify(error='Message Not found'), HTTPStatus.BAD_REQUEST
    
    msg.delete()
    app.logger.debug('Message with id={} deleted.'.format(msg.id))

    return jsonify(''), HTTPStatus.NO_CONTENT
