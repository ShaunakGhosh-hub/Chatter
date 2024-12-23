from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

active_users = {}  # Maps socket IDs to user IDs
chat_rooms = {}  # Maps user IDs to their chat partners

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    user_id = f"User_{request.sid[:5]}"
    active_users[request.sid] = user_id
    print(f"{user_id} connected.")
    emit('active_users', list(active_users.values()), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    user_id = active_users.pop(request.sid, None)
    if user_id:
        print(f"{user_id} disconnected.")
        # Remove user from chat rooms
        chat_rooms.pop(user_id, None)
    emit('active_users', list(active_users.values()), broadcast=True)

@socketio.on('join')
def handle_join():
    user_id = active_users[request.sid]
    print(f"{user_id} is looking for a chat partner.")

    available_users = [uid for uid in active_users.values() if uid != user_id and uid not in chat_rooms]

    if available_users:
        partner = available_users[0]
        chat_rooms[user_id] = partner
        chat_rooms[partner] = user_id

        emit('system_message', f"You are now chatting with {partner}.", room=request.sid)
        partner_sid = next(sid for sid, uid in active_users.items() if uid == partner)
        emit('system_message', f"You are now chatting with {user_id}.", room=partner_sid)
    else:
        emit('system_message', "No other users available. You can chat with the chatbot.", room=request.sid)

@socketio.on('message')
def handle_message(data):
    user_id = active_users.get(request.sid)
    message = data.get('message', '')
    print(f"Message from {user_id}: {message}")

    if user_id in chat_rooms:
        partner = chat_rooms[user_id]
        partner_sid = next(sid for sid, uid in active_users.items() if uid == partner)
        emit('chat_message', {'sender': user_id, 'message': message}, room=partner_sid)
    else:
        # Respond with chatbot
        emit('chat_message', {'sender': 'Chatbot', 'message': f"You said: {message}"}, room=request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True)
