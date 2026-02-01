import unittest
import json
import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from app import create_app
from infrastructure.services.collab_service import CollabService

class TestCollabAlgorithms(unittest.TestCase):
    
    def test_binary_search_algorithm(self):
        print("\n[Unit Test] Đang test Binary Search Algorithm...")
        
        # Tạo Mock Object giả lập
        class MockVersion:
            def __init__(self, ts):
                self.created_at = datetime.fromtimestamp(ts)

        # Tạo dữ liệu giả: 1000, 2000, 3000, 4000
        versions = [MockVersion(1000), MockVersion(2000), MockVersion(3000), MockVersion(4000)]

        # Case 1: Tìm chính xác (3000)
        result = CollabService.find_version_by_timestamp_algorithm(versions, 3000)
        self.assertIsNotNone(result)
        self.assertEqual(result.created_at.timestamp(), 3000)

        # Case 2: Tìm gần đúng (2600 -> Gần 3000 hơn là 2000)
        result_approx = CollabService.find_version_by_timestamp_algorithm(versions, 2600)
        self.assertIsNotNone(result_approx)
        self.assertEqual(result_approx.created_at.timestamp(), 3000)
        
        print(" -> Binary Search: ✅ OK")

    def test_diff_algorithm(self):
        print("[Unit Test] Đang test Diff Algorithm (LCS)...")
        import difflib
        text1 = ["Hello World"]
        text2 = ["Hello Python"]
        
        # Thuật toán LCS
        diff = list(difflib.unified_diff(text1, text2, lineterm=''))
        
        # Kiểm tra diff có nội dung không
        self.assertTrue(len(diff) > 0)
        print(" -> Diff Algorithm: ✅ OK")


class TestCollabIntegration(unittest.TestCase):

    def setUp(self):
        # Khởi tạo App ở chế độ Testing
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # ID tài liệu giả định (Phải chắc chắn DB đã có ID này sau khi Seed)
        self.doc_id = 1 

    def test_optimistic_locking_flow(self):
        """
        Kịch bản Test:
        1. User A đọc dữ liệu.
        2. User A sửa và lưu thành công (Updated At thay đổi).
        3. User B (đang cầm bản cũ) cố gắng lưu đè.
        4. Hệ thống phải chặn User B và trả về 409 Conflict.
        """
        print("\n[Integration Test] Đang test Optimistic Locking API...")

        # BƯỚC 0: Reset dữ liệu (Warm-up)
        print(" 1. Reset dữ liệu...")
        setup_payload = {"content": "Khoi tao", "last_updated": None}
        self.client.put(f'/api/v1/documents/{self.doc_id}/content',
                        data=json.dumps(setup_payload),
                        content_type='application/json')
        
        # [QUAN TRỌNG] Ngủ 2s để thời gian trôi qua, tránh trùng giây
        print("    (Chờ 2s để đồng hồ nhảy giây...)")
        time.sleep(2) 

        # BƯỚC 1: Lấy thông tin hiện tại (Phiên bản gốc)
        print(" 2. Lấy version hiện tại...")
        res_get = self.client.get(f'/api/v1/documents/{self.doc_id}')
        
        if res_get.status_code != 200:
            self.fail(f"❌ Không tìm thấy document ID={self.doc_id}. Hãy chạy Seed Data trước!")
            
        data = res_get.get_json()['data']
        original_ts = data['updated_at']
        print(f"    Original Time: {original_ts}")

        # BƯỚC 2: User A update thành công
        print(" 3. User A update (Hợp lệ)...")
        payload_a = {
            "content": "User A update",
            "last_updated": original_ts # Gửi kèm thời gian gốc
        }
        res_put_a = self.client.put(
            f'/api/v1/documents/{self.doc_id}/content',
            data=json.dumps(payload_a),
            content_type='application/json'
        )
        self.assertEqual(res_put_a.status_code, 200)

        # [QUAN TRỌNG] Ngủ tiếp 2s để DB chắc chắn cập nhật thời gian mới
        print("    (Chờ tiếp 2s...)")
        time.sleep(2)

        # BƯỚC 3: Kiểm tra DB đã có thời gian mới chưa
        res_get_new = self.client.get(f'/api/v1/documents/{self.doc_id}')
        new_ts = res_get_new.get_json()['data']['updated_at']
        print(f"    New Time DB:   {new_ts}")

        self.assertNotEqual(new_ts, original_ts, "❌ Lỗi: Thời gian trong DB không thay đổi!")

        # BƯỚC 4: User B cố tình dùng thời gian CŨ (original_ts) -> Gây xung đột
        print(" 4. User B cố tình update bằng version cũ (Gây xung đột)...")
        payload_b = {
            "content": "User B update fail",
            "last_updated": original_ts # CỐ TÌNH DÙNG CÁI CŨ
        }
        res_put_b = self.client.put(
            f'/api/v1/documents/{self.doc_id}/content',
            data=json.dumps(payload_b),
            content_type='application/json'
        )

        # BƯỚC 5: Kiểm tra kết quả
        if res_put_b.status_code == 409:
            print(" -> ✅ Test Pass: Hệ thống đã chặn xung đột (409 Conflict)")
        elif res_put_b.status_code == 200:
            print(" -> ❌ Test Fail: Hệ thống vẫn cho lưu đè (Lỗi logic)!")
        else:
            print(f" -> ⚠️ Test Error: Mã lỗi lạ {res_put_b.status_code}")

        self.assertEqual(res_put_b.status_code, 409)

if __name__ == '__main__':
    unittest.main()