from uuid import UUID


class QuizNotFoundException(Exception):
    def __init__(self, quiz_id: UUID):
        self.quiz_id = quiz_id
        super().__init__(f"Quiz with id {quiz_id} was not found.")


class QuizAlreadyExistsException(Exception):
    def __init__(self, field: str):
        self.field = field
        super().__init__(f"Quiz with the same {field} already exists.")


class QuizFrequencyException(Exception):
    def __init__(self):
        super().__init__("You cannot take this quiz yet. Please wait until the frequency period has passed.")

