class MongoUser:
    def __init__(self, user_dict):
        self._user_dict = user_dict
        self.id = str(user_dict.get('_id'))
        self.email = user_dict.get('email')
        self.role = user_dict.get('role')
        self.full_name = user_dict.get('fullName')
        self.profile = user_dict.get('profile', {})

    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return self.full_name or self.email or self.id
