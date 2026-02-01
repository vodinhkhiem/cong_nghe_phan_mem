import google.generativeai as genai
import os

# Cấu hình API Key (Lấy tại https://aistudio.google.com/)
# Tốt nhất nên để trong biến môi trường hoặc file config.py
GEMINI_API_KEY = "DIEN_API_KEY_CUA_BAN_VAO_DAY" 

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class AILLMClient:
    @staticmethod
    def generate_response(prompt: str, system_context: str = "") -> str:
        if not GEMINI_API_KEY or GEMINI_API_KEY == "AIzaSyARbNWnKszZ7CEAcOG0vENkVlvuGyeaejU":
            return "[MOCK] Chưa có API Key. Vui lòng cấu hình Gemini API Key."

        try:
            # Chọn model (gemini-pro hoặc gemini-1.5-flash)
            model = genai.GenerativeModel('gemini-pro')
            
            # Ghép system context vào prompt (Gemini Pro cũ chưa hỗ trợ system instruction tốt bằng prompt ghép)
            full_prompt = f"{system_context}\n\nUser query: {prompt}"
            
            response = model.generate_content(full_prompt)
            
            return response.text
        except Exception as e:
            return f"Lỗi khi gọi Gemini AI: {str(e)}"