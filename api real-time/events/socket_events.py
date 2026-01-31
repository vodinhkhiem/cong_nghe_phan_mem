from flask import request
from flask_socketio import emit, join_room, leave_room # type: ignore[import-untyped]
from extensions import socketio
import datetime

# 1. KẾT NỐI & QUẢN LÝ PHÒNG (ROOMS)
@socketio.on('connect')
def handle_connect():
    print(f"✅ Client connected: {request.sid}") # type: ignore

@socketio.on('disconnect')
def handle_disconnect():
    print(f"❌ Client disconnected: {request.sid}") # type: ignore

@socketio.on('join_room')
def handle_join_room(data):
    """
    Client gửi lên: { "room_id": "team_1" hoặc "doc_5" }
    """
    room = data.get('room_id')
    join_room(room)
    print(f"📢 User {request.sid} joined room: {room}") # type: ignore
    emit('status', {'msg': f'User joined {room}'}, room=room) # type: ignore

@socketio.on('leave_room')
def handle_leave_room(data):
    room = data.get('room_id')
    leave_room(room)
    print(f"👋 User {request.sid} left room: {room}") # type: ignore

# 2. XỬ LÝ DOCUMENT (SOẠN THẢO VĂN BẢN)
@socketio.on('doc_change')
def handle_doc_change(data):
    """
    Khi User A gõ chữ, sự kiện này được kích hoạt.
    Data: { "room_id": "doc_5", "delta": {...}, "content": "..." }
    """
    room = data.get('room_id')
    
    # Gửi lại cho TẤT CẢ mọi người trong phòng (TRỪ người gửi)
    # include_self=False để người gõ không bị lặp lại chữ của chính mình
    emit('doc_update', data, room=room, include_self=False) # type: ignore

# 3. XỬ LÝ WHITEBOARD (BẢNG TRẮNG)
@socketio.on('wb_draw')
def handle_wb_draw(data):
    """
    Khi User A vẽ 1 nét.
    Data: { "room_id": "team_1", "type": "line", "coords": [...] }
    """
    room = data.get('room_id')
    
    # Bắn ngay lập tức cho người khác thấy nét vẽ
    emit('wb_update', data, room=room, include_self=False) # type: ignore

@socketio.on('wb_clear')
def handle_wb_clear(data):
    """Xóa bảng"""
    room = data.get('room_id')
    emit('wb_cleaned', {'msg': 'Board cleared'}, room=room, include_self=False) # type: ignore

# 4. XỬ LÝ CHAT (TIN NHẮN)
@socketio.on('send_message')
def handle_chat_message(data):
    """
    Data: { "room_id": "team_1", "sender": "UserA", "message": "Hello" }
    """
    room = data.get('room_id')
    timestamp = datetime.datetime.now().strftime('%H:%M')
    
    response = {
        "sender": data.get('sender'),
        "message": data.get('message'),
        "time": timestamp
    }
    
    # Chat thì gửi cho TẤT CẢ (bao gồm cả người gửi để họ thấy tin mình vừa chat)
    emit('receive_message', response, room=room) # type: ignore