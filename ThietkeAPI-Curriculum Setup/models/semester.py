# models/semester.py
# Mô hình dữ liệu Semester

class Semester:
    def __init__(self, id, name, is_current=False):
        self.id = id
        self.name = name
        self.is_current = is_current
