from flask import session, redirect, url_for
from flask_socketio import emit
from ..database import Message, Room, User
from app import socketio
import json


connection = Room('Chat', 'Room')
message = Message('Chat', 'Message')
Userdb = User('Chat', 'User')


@socketio.on('chat_message')
def handle_message(msg):

    message.commit(msg['message'], msg['user'])

    color = Userdb.get_color(msg['user'])
    color_split = color.split(' ')
    new_color = 'class="title {}-text text-{} message_title"'.format(color_split[0], color_split[1])

    string = '<li class="collection-item"><span {}>{}</span><p class="">{}</p></li>'
    full = string.format(new_color, msg['user'], msg['message'])

    emit('chat_response', {'message': msg['message'],
                           'user': msg['user'],
                           'color': new_color,
                           'string': full}, broadcast=True)


@socketio.on('message')
def handle_connect(msg):

    users, user_count = connection.user_list()

    if session['username'] in users:
        user_color = []
        for user in users:
            string ='<tr><td class="{} white-text">{}</td></tr>'
            color = Userdb.get_color(user)
            full = string.format(color, user)
            user_color.append(full)

        msg = 'not'
        message_sending = {"message": msg,
                           "connections": user_count,
                           "users": users,
                           'user_color': user_color}

    else:
        connection.add_user(session['username'])
        users, user_count = connection.user_list()

        user_color = []
        for user in users:
            string = '<tr><td class="{} white-text">{}</td></tr>'
            color = Userdb.get_color(user)
            full = string.format(color, user)
            user_color.append(full)

        message_sending = {"message": msg,
                           "connections": user_count,
                           "users": users,
                           'new_user': session['username'],
                           'user_color': user_color}

    emit("new connection", message_sending, broadcast=True)


@socketio.on('leave_room')
def handle_leave_room(obj):

    user = session['username']
    connection.user_leave(user)

    try:
        del session['username']
    except Exception as e:
        print(str(e))

    users, user_count = connection.user_list()

    user_color = []
    for user in users:
        string = '<tr><td class="{} white-text">{}</td></tr>'
        color = Userdb.get_color(user)
        full = string.format(color, user)
        user_color.append(full)

    message_sending = {'message': 'user {} left room'.format(user),
                       "connections": user_count,
                       "users": users,
                       'user_color': user_color}

    emit('user_left', message_sending, broadcast=True)


@socketio.on('typing')
def handle_tying(obj):

    message_sending = {"message": "{} is typing".format(obj['user'])}

    emit('typing_response', message_sending, broadcast=True)
