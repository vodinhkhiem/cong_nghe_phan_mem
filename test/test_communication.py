import unittest
import json
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from app import create_app
from infrastructure.databases.mssql import engine
from sqlalchemy.orm import Session
from infrastructure.models.user_model import UserModel
from infrastructure.models.team_model import TeamModel, TeamMemberModel
from infrastructure.models.meeting_model import MeetingModel, MeetingAttendeeModel
from infrastructure.models.messager_model import MessageModel

class TestCommunicationIntegration(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        session = self.get_db_session()
        try:
            # 1. Xử lý LEADER (Get or Create)
            leader_email = "leader_test@test.com"
            leader = session.query(UserModel).filter_by(email=leader_email).first()
            
            if not leader:
                leader = UserModel(
                    full_name="Leader User", 
                    email=leader_email, 
                    password="123", 
                    role="Student",
                    status=True
                )
                session.add(leader)
                session.commit()
            
            self.leader_id = leader.id

            # 2. Xử lý MEMBER (Get or Create)
            member_email = "member_test@test.com"
            member = session.query(UserModel).filter_by(email=member_email).first()
            
            if not member:
                member = UserModel(
                    full_name="Member User", 
                    email=member_email, 
                    password="123", 
                    role="Student",
                    status=True
                )
                session.add(member)
                session.commit()
            
            self.member_id = member.id 

            # 3. Xử lý CLASS (Cần thiết để tạo Team)
            from infrastructure.models.academic_model import ClassModel, SubjectModel
            
            # Tạo Subject giả nếu chưa có
            subject = session.query(SubjectModel).filter_by(code="SUB_TEST").first()
            if not subject:
                subject = SubjectModel(code="SUB_TEST", name="Test Subject")
                session.add(subject)
                session.commit()

            # Tạo Class giả nếu chưa có
            clazz = session.query(ClassModel).filter_by(name="TEST_CLASS_01").first()
            if not clazz:
                clazz = ClassModel(name="TEST_CLASS_01", subject_id=subject.id, semester="SP26")
                session.add(clazz)
                session.commit()

            # 4. Xử lý TEAM
            team_name = "Unit Test Team"
            team = session.query(TeamModel).filter_by(name=team_name).first()
            
            if not team:
                team = TeamModel(name=team_name, leader_id=self.leader_id, class_id=clazz.id)
                session.add(team)
                session.commit()
            
            self.team_id = team.id

            # --- Kiểm tra và thêm Leader vào TeamMember ---
            tm_leader = session.query(TeamMemberModel).filter_by(team_id=team.id, user_id=self.leader_id).first()
            if not tm_leader:
                tm_leader = TeamMemberModel(team_id=team.id, user_id=self.leader_id, role='Leader')
                session.add(tm_leader)
                session.commit()

            # --- Kiểm tra và thêm Member vào TeamMember ---
            tm_member = session.query(TeamMemberModel).filter_by(team_id=team.id, user_id=self.member_id).first()
            if not tm_member:
                tm_member = TeamMemberModel(team_id=team.id, user_id=self.member_id, role='Member')
                session.add(tm_member)
                session.commit()
            
            self.team_id = team.id

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_db_session(self):
        return Session(bind=engine)

    # TEST CASE 1: CHAT FLOW (Gửi & Nhận tin nhắn)
    def test_chat_flow(self):
        print("\n[Test 1] 💬 Testing Chat Flow (Send & Get)...")
        
        # 1. Gửi tin nhắn mới
        payload = {
            "sender_id": self.member_id,
            "content": "Test message from Unit Test"
        }
        res_post = self.client.post(
            f'/api/v1/chat/conversations/{self.team_id}/messages',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res_post.status_code, 201)
        print("   ✅ Gửi tin nhắn thành công (201 Created)")

        # 2. Lấy danh sách tin nhắn để kiểm tra
        res_get = self.client.get(f'/api/v1/chat/conversations/{self.team_id}/messages')
        self.assertEqual(res_get.status_code, 200)
        messages = res_get.get_json()['data']

        print(f"   🔍 DEBUG: Tìm thấy {len(messages)} tin nhắn.")
        for m in messages:
            print(f"      - [{m['id']}] {m['sender_name']}: {m['content']}")

        # Kiểm tra xem tin nhắn vừa gửi có nằm trong danh sách không
        found = any(m['content'] == "Test message from Unit Test" for m in messages)
        
        if found:
            print("   ✅ Đã tìm thấy tin nhắn vừa gửi trong Database.")
        else:
            self.fail("   ❌ Lỗi: Không tìm thấy tin nhắn vừa gửi!")

    # TEST CASE 2: MEETING FLOW 
    def test_create_meeting_auto_invite(self):
        print("\n[Test 2] 📅 Testing Meeting Creation & Auto-Invite Logic...")
        
        session = self.get_db_session()
        try:
            # 1. Tạo cuộc họp mới
            start_time = datetime.now() + timedelta(days=1)
            end_time = start_time + timedelta(hours=1)
            
            payload = {
                "team_id": self.team_id,
                "creator_id": self.leader_id,
                "title": "Hop Test Auto Invite",
                "description": "Kiểm tra xem thành viên có được add tự động không",
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "meeting_link": "https://meet.google.com/abc-xyz",
                "is_online": True
            }

            res_post = self.client.post(
                '/api/v1/meetings',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            self.assertEqual(res_post.status_code, 201)
            meeting_id = res_post.get_json()['id']
            print(f"   ✅ Đã tạo cuộc họp ID: {meeting_id}")

            # 2. KIỂM TRA LOGIC TỰ ĐỘNG THÊM THÀNH VIÊN (Crucial Step)
            attendees = session.query(MeetingAttendeeModel).filter_by(meeting_id=meeting_id).all()
            
            count = len(attendees)
            print(f"   🔍 Tìm thấy {count} thành viên được mời tự động.")
            
            # Team 1 (theo seed.py) có ít nhất 2 người (Leader & Member)
            if count >= 2:
                print("   ✅ Logic Auto-Invite hoạt động ĐÚNG (Có > 1 người).")
            else:
                self.fail(f"   ❌ Lỗi: Logic Auto-Invite SAI. Chỉ có {count} người (Kỳ vọng >= 2).")

            # Kiểm tra trạng thái mặc định phải là 'Pending'
            for att in attendees:
                self.assertEqual(att.status, 'Pending')
            print("   ✅ Trạng thái mặc định là 'Pending'.")

        finally:
            session.close()

    # TEST CASE 3: ATTENDANCE (Điểm danh)
    def test_mark_attendance(self):
        print("\n[Test 3] 🙋 Testing Attendance Marking...")
        
        session = self.get_db_session()
        try:
            meeting = session.query(MeetingModel).filter_by(team_id=self.team_id).order_by(MeetingModel.id.desc()).first()
            
            if not meeting:
                print("   ⚠️ Không có cuộc họp nào để test điểm danh. Bỏ qua.")
                return

            # Leader điểm danh "Present"
            payload = {
                "user_id": self.leader_id,
                "status": "Present"
            }
            
            res_put = self.client.put(
                f'/api/v1/meetings/{meeting.id}/attendance',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            self.assertEqual(res_put.status_code, 200)
            print(f"   ✅ API trả về 200 OK cho Meeting ID {meeting.id}")
    
            session.expire_all() 
            
            attendee = session.query(MeetingAttendeeModel).filter_by(meeting_id=meeting.id, user_id=self.leader_id).first()
            self.assertEqual(attendee.status, 'Present')
            print(f"   ✅ DB đã cập nhật trạng thái: {attendee.status}")

        finally:
            session.close()

if __name__ == '__main__':
    unittest.main()