import json
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import engine
from infrastructure.services.collab_service import CollabService, VersionConflictError

collab_bp = Blueprint('collab', __name__, url_prefix='/api/v1')

def get_db():
    return Session(bind=engine)

# PHẦN 1: WHITEBOARD API
@collab_bp.route('/whiteboards/<int:project_id>/state', methods=['GET'])
def get_whiteboard_state(project_id):
    """
    Lấy dữ liệu bảng trắng của dự án (Initial Load)
    ---
    tags:
      - Collab (Whiteboard)
    parameters:
      - name: project_id
        in: path
        type: integer
        required: true
    """
    session = get_db()
    try:
        # Gọi Service mới viết
        data = CollabService.get_whiteboard_state(session, project_id)
        
        # Data trong DB là chuỗi JSON, ta trả về dạng JSON object
        return jsonify({
            "status": "success",
            "data": json.loads(data) if data else {}
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        session.close()

@collab_bp.route('/whiteboards/<int:project_id>/snapshot', methods=['POST'])
def save_whiteboard_snapshot(project_id):
    """
    Lưu trạng thái bảng trắng (Save Snapshot)
    ---
    tags:
      - Collab (Whiteboard)
    parameters:
      - name: project_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            state:
              type: object
              description: JSON chứa toàn bộ nét vẽ
    """
    session = get_db()
    try:
        req_data = request.json
        state_data = req_data.get('state', {})
        
        # Chuyển Dict thành String để lưu vào DB (Cột Text)
        state_str = json.dumps(state_data)
        
        CollabService.save_whiteboard_snapshot(session, project_id, state_str)
        
        return jsonify({"status": "success", "message": "Đã lưu bảng trắng"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        session.close()

# PHẦN 2: COLLABORATIVE EDITOR API
# --- API LẤY DANH SÁCH DOCUMENT THEO DỰ ÁN ---
@collab_bp.route('/teams/<int:team_id>/documents', methods=['GET'])
def get_documents(team_id):
    db = get_db()
    try:
        docs = CollabService.get_all_documents(db, team_id)
        result = [{
            "id": d.id,
            "name": d.name,
            "file_type": d.file_type,
            "updated_at": d.updated_at
        } for d in docs]
        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()

# --- API TẠO MỚI DOCUMENT ---
@collab_bp.route('/documents', methods=['POST'])
def create_document():
    db = get_db()
    try:
        body = request.json
        team_id = body.get('team_id')
        name = body.get('name')
        file_type = body.get('type', 'CODE')

        if not team_id or not name:
            return jsonify({"status": "error", "message": "Missing team_id or name"}), 400

        new_doc = CollabService.create_document(db, team_id, name, file_type)
        
        return jsonify({
            "status": "success",
            "data": {
                "id": new_doc.id,
                "name": new_doc.name,
                "type": new_doc.file_type
            }
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()

# --- API LẤY CHI TIẾT DOCUMENT THEO ID ---
@collab_bp.route('/documents/<int:doc_id>', methods=['GET'])
def get_document_detail(doc_id):
    db = get_db()
    try:
        doc = CollabService.get_document_by_id(db, doc_id)
        if not doc:
            return jsonify({"status": "error", "message": "Document not found"}), 404
            
        return jsonify({
            "status": "success",
            "data": {
                "id": doc.id,
                "name": doc.name,
                "content": doc.content,
                "file_type": doc.file_type,
                "updated_at": doc.updated_at # Frontend cần lấy cái này để gửi lại khi Save
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()

# --- API SAVE VỚI OPTIMISTIC LOCKING ---
@collab_bp.route('/documents/<int:doc_id>/content', methods=['PUT'])
def save_document_content(doc_id):
    """
    Save Snapshot: Lưu nội dung file xuống DB.
    Payload bắt buộc: 
    { 
      "content": "code mới...", 
      "last_updated": "2023-10-30T10:00:00" (Thời gian của bản mà user đang sửa)
    }
    """
    db = get_db()
    try:
        body = request.json
        content = body.get('content', '')
        # Lấy thời gian phiên bản cũ từ client gửi lên
        last_updated = body.get('last_updated') 
        
        success = CollabService.save_document_content(db, doc_id, content, last_updated)
        
        if not success:
            return jsonify({"status": "error", "message": "Document not found"}), 404
            
        return jsonify({"status": "success", "message": "Saved successfully"}), 200

    except VersionConflictError as ve:
        # [ALGORITHM TRIGGERED]
        # Nếu bắt được lỗi xung đột -> Trả về mã 409 Conflict
        return jsonify({
            "status": "fail", 
            "code": "VERSION_CONFLICT",
            "message": str(ve)
        }), 409
        
    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()

# --- API MỚI: XEM DIFF TRƯỚC KHI LƯU (LCS Algorithm) ---
@collab_bp.route('/documents/<int:doc_id>/diff', methods=['POST'])
def preview_diff(doc_id):
    # API này nhận nội dung mới từ client, so sánh với nội dung hiện tại trong DB,
    # và trả về phần khác biệt (diff) mà không lưu xuống DB.
    db = get_db()
    try:
        new_content = request.json.get('content', '')
        
        # Gọi thuật toán so sánh chuỗi
        diff_result = CollabService.compare_document_versions(db, doc_id, new_content)
        
        if diff_result is None:
            return jsonify({"status": "error", "message": "Document not found"}), 404
            
        return jsonify({
            "status": "success", 
            "data": diff_result # Trả về mảng các dòng thay đổi (+/-)
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()