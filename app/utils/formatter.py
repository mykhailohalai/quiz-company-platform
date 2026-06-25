import csv
import io

from app.models.quiz_result import QuizResult


class Formatter:
    @staticmethod
    def quiz_results_to_csv(results: list[QuizResult]):
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            "user_id", "quiz_id", "company_id",
            "correct_answers", "total_questions", "score_percentage", "created_at"
        ])
        
        for r in results:
            score = round(r.correct_answers / r.total_questions * 100, 2) if r.total_questions else 0.0
            writer.writerow([
                r.user_id, r.quiz_id, r.company_id,
                r.correct_answers, r.total_questions, score, r.created_at
            ])
        
        return output.getvalue()
