import bcrypt


class PasswordHelper():
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(password.encode(), salt)

        return hash.decode()

    @staticmethod
    def verify_password(hashed_password: str, password: str) -> bool:
        result = bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

        return result
