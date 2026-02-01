from flask_socketio import SocketIO  # type: ignore[import-untyped]

# Khởi tạo SocketIO, cho phép mọi nguồn (CORS *) để Frontend gọi được
socketio = SocketIO(cors_allowed_origins="*")