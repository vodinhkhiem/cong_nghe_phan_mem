# File: ai_post.py
from flask import Blueprint, request, jsonify
import google.generativeai as genai
import os

ai_bp = Blueprint("ai_bp", __name__)

# --- Cấu hình Gemini ---
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    # Dùng model flash cho nhanh và rẻ
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None
    print("⚠️ Cảnh báo: Chưa tìm thấy GEMINI_API_KEY trong file .env")

# Hàm helper để gọi AI và xử lý lỗi
def ask_gemini(prompt):
    if not model:
        return "Lỗi Server: Chưa cấu hình API Key cho AI."
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Lỗi xử lý AI: {str(e)}"

# --- 1. Chat thông thường (kèm ngữ cảnh System Prompt) ---
@ai_bp.route("/chat", methods=["POST"])
def ai_chat():
    data = request.json
    user_msg = data.get("message", "")
    conversation_id = data.get("conversation_id")

    # System Prompt: Quan trọng để AI không trả lời lan man
    system_instruction = """
    Bạn là một trợ lý học tập AI (Tutor).
    Nhiệm vụ: Chỉ trả lời các câu hỏi liên quan đến môn học, lập trình, và bài tập.
    Phong cách: Thân thiện, khuyến khích tư duy, không giải bài tập hộ mà chỉ gợi ý hướng làm.
    Câu hỏi của sinh viên: 
    """
    
    full_prompt = f"{system_instruction} {user_msg}"
    response_text = ask_gemini(full_prompt)

    return jsonify({
        "conversation_id": conversation_id,
        "reply": response_text
    })

# --- 2. Chia nhỏ Task (Scaffolding) ---
@ai_bp.route("/tasks/<taskId>/breakdown", methods=["POST"])
def task_breakdown(taskId):
    data = request.json
    task_desc = data.get("task_description", "")

    # Prompt chuyên biệt cho Scaffolding
    prompt = f"""
    Tôi có một nhiệm vụ lớn: "{task_desc}".
    Hãy đóng vai một Project Manager, giúp tôi chia nhỏ nhiệm vụ này thành 3-5 bước nhỏ (checklist) cụ thể để dễ thực hiện.
    Định dạng trả về: Chỉ gạch đầu dòng các bước, không giải thích dài dòng.
    """
    
    response_text = ask_gemini(prompt)

    return jsonify({
        "taskId": taskId,
        "checklist_suggestion": response_text
    })

# --- 3. Giải thích lỗi Code ---
@ai_bp.route("/code/explain", methods=["POST"])
def explain_code():
    data = request.json
    code_snippet = data.get("code_snippet", "")
    error_log = data.get("error_log", "")

    prompt = f"""
    Tôi gặp lỗi khi chạy đoạn code sau:
    CODE:
    {code_snippet}
    
    LỖI (LOG):
    {error_log}
    
    Hãy giải thích ngắn gọn tại sao lỗi và gợi ý cách sửa (đưa ra code sửa nếu cần).
    """
    
    response_text = ask_gemini(prompt)
    return jsonify({"explanation": response_text})

# --- 4. Gợi ý tài liệu (Resources) ---
@ai_bp.route("/resources/recommend", methods=["POST"])
def recommend_resource():
    data = request.json
    topic = data.get("topic", "")

    # Logic: AI dùng kiến thức nội tại để gợi ý
    prompt = f"""
    Sinh viên đang cần tài liệu học về chủ đề: "{topic}".
    Hãy gợi ý 3 đầu mục tài liệu uy tín (tên sách, từ khóa tìm kiếm, hoặc link docs chính thức) để học chủ đề này.
    """
    
    response_text = ask_gemini(prompt)
    return jsonify({"topic": topic, "recommendations": response_text})

# --- 5. Lịch sử Chat ---
@ai_bp.route("/history", methods=["GET"])
def get_history():
    # Phần này thường lấy từ DB, tạm thời mock data
    return jsonify({
        "history": [
            {"role": "user", "msg": "OOP là gì?"},
            {"role": "ai", "msg": "OOP là Lập trình hướng đối tượng..."}
        ]
    })