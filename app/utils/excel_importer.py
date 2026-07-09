import io

import openpyxl
from pydantic import ValidationError

from app.exceptions.quiz_exceptions import InvalidQuizFileException
from app.models.quiz import QuestionType
from app.schemas.quiz import (
    AnswerCreateRequestSchema,
    QuestionCreateRequestSchema,
    QuizCreateRequestSchema,
)

REQUIRED_COLUMNS = [
    "quiz_title",
    "quiz_description",
    "quiz_frequency",
    "question_title",
    "question_type",
    "answer_1_text",
    "answer_1_correct",
    "answer_2_text",
    "answer_2_correct",
]
ANSWER_SLOTS = 4


class ExcelImporter:
    @staticmethod
    def parse_quizzes(file_bytes: bytes) -> list[QuizCreateRequestSchema]:
        try:
            workbook = openpyxl.load_workbook(
                io.BytesIO(file_bytes), read_only=True, data_only=True
            )
        except Exception as exc:
            raise InvalidQuizFileException("file is not a valid .xlsx workbook") from exc

        sheet = workbook.active
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            raise InvalidQuizFileException("file has no rows")

        header = [str(cell).strip().lower() if cell is not None else "" for cell in rows[0]]
        missing = [c for c in REQUIRED_COLUMNS if c not in header]
        if missing:
            raise InvalidQuizFileException(f"missing required columns: {', '.join(missing)}")
        col_index = {name: header.index(name) for name in header if name}

        quizzes: dict[str, dict] = {}
        for row_num, row in enumerate(rows[1:], start=2):
            if row is None or all(cell is None for cell in row):
                continue

            def cell(name: str):
                idx = col_index.get(name)
                return row[idx] if idx is not None and idx < len(row) else None

            title = cell("quiz_title")
            if not title:
                raise InvalidQuizFileException(f"row {row_num}: quiz_title is required")
            title = str(title).strip()

            question_title = cell("question_title")
            if not question_title:
                raise InvalidQuizFileException(f"row {row_num}: question_title is required")

            question_type_raw = str(cell("question_type") or "multiple answer").strip().lower()
            try:
                question_type = QuestionType(question_type_raw)
            except ValueError:
                raise InvalidQuizFileException(
                    f"row {row_num}: invalid question_type '{question_type_raw}'"
                )

            answers = []
            for i in range(1, ANSWER_SLOTS + 1):
                text = cell(f"answer_{i}_text")
                if text is None or str(text).strip() == "":
                    continue
                answers.append(
                    AnswerCreateRequestSchema(
                        text=str(text).strip(),
                        is_correct=ExcelImporter._to_bool(cell(f"answer_{i}_correct")),
                    )
                )
            if len(answers) < 2:
                raise InvalidQuizFileException(
                    f"row {row_num}: at least 2 answers are required"
                )

            quiz_entry = quizzes.setdefault(
                title,
                {
                    "title": title,
                    "description": str(cell("quiz_description") or "").strip(),
                    "frequency": cell("quiz_frequency"),
                    "questions": [],
                },
            )
            quiz_entry["questions"].append(
                QuestionCreateRequestSchema(
                    title=str(question_title).strip(),
                    question_type=question_type,
                    answers=answers,
                )
            )

        if not quizzes:
            raise InvalidQuizFileException("file contains no quiz data")

        try:
            return [QuizCreateRequestSchema(**entry) for entry in quizzes.values()]
        except ValidationError as exc:
            raise InvalidQuizFileException(str(exc)) from exc

    @staticmethod
    def _to_bool(value) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        return str(value).strip().lower() in {"true", "1", "yes", "y"}
