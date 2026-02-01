from infrastructure.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.repo = user_repo

    def get_profile(self, user_id):
        user = self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return user

    def update_profile(self, user_id, data):
        user = self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if 'full_name' in data: user.full_name = data['full_name']
        if 'avatar_url' in data: user.avatar_url = data['avatar_url']
        if 'description' in data: user.description = data['description']
        return self.repo.update(user)