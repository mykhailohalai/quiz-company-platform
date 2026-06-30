import io
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse

from app.dependencies import get_current_user_dep, get_quiz_service
from app.models.user import User
from app.schemas.quiz import (
    QuizCreateRequestSchema,
    QuizUpdateRequestSchema,
    QuizResponseSchema,
    PaginatedQuizResponseSchema,
)
from app.schemas.quiz_result import (
    AverageScoreResponseSchema,
    QuizResultResponseSchema,
    QuizSubmitSchema,
)
from app.services.quiz_service import QuizService
from app.utils.formatter import Formatter

quiz_router = APIRouter()


@quiz_router.post(
    "/companies/{company_id}/quizzes",
    response_model=QuizResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_quiz(
    company_id: UUID,
    data: QuizCreateRequestSchema,
    current_user: User = Depends(get_current_user_dep),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    quiz = await quiz_service.create_quiz(company_id, current_user.id, data)
    return QuizResponseSchema.model_validate(quiz)


@quiz_router.patch(
    "/companies/{company_id}/quizzes/{quiz_id}",
    response_model=QuizResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_quiz(
    company_id: UUID,
    quiz_id: UUID,
    data: QuizUpdateRequestSchema,
    current_user: User = Depends(get_current_user_dep),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    quiz = await quiz_service.update_quiz(quiz_id, company_id, current_user.id, data)
    return QuizResponseSchema.model_validate(quiz)


@quiz_router.delete(
    "/companies/{company_id}/quizzes/{quiz_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_quiz(
    company_id: UUID,
    quiz_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    await quiz_service.delete_quiz(quiz_id, company_id, current_user.id)


@quiz_router.get(
    "/companies/{company_id}/quizzes",
    response_model=PaginatedQuizResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_quizzes(
    company_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    quizzes, total = await quiz_service.get_quizzes(company_id, skip, limit)
    return PaginatedQuizResponseSchema(
        quizzes=quizzes,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total,
    )


@quiz_router.get(
    "/companies/{company_id}/quizzes/{quiz_id}",
    response_model=QuizResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_quiz_for_member(
    company_id: UUID,
    quiz_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    quiz = await quiz_service.get_quiz_by_company_member(company_id, current_user.id, quiz_id)
    return QuizResponseSchema.model_validate(quiz)


@quiz_router.post(
    "/companies/{company_id}/quizzes/{quiz_id}/results",
    response_model=QuizResultResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def submit_quiz(
    company_id: UUID,
    quiz_id: UUID,
    data: QuizSubmitSchema,
    current_user: User = Depends(get_current_user_dep),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    result = await quiz_service.submit_quiz(company_id, quiz_id, current_user.id, data)
    return QuizResultResponseSchema.model_validate(result)


@quiz_router.get(
    "/companies/{company_id}/users/me/score",
    response_model=AverageScoreResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_average_by_company(
    company_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    average_score = await quiz_service.get_average_by_company(current_user.id, company_id)
    return AverageScoreResponseSchema(average_score=average_score)


@quiz_router.get(
    "/users/me/score",
    response_model=AverageScoreResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_average_by_system(
    current_user: User = Depends(get_current_user_dep),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    average_score = await quiz_service.get_average_by_system(current_user.id)
    return AverageScoreResponseSchema(average_score=average_score)


@quiz_router.get(
    "/companies/{company_id}/users/{user_id}/results",
    status_code=status.HTTP_200_OK,
)
async def get_user_quiz_results(
    company_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    return await quiz_service.get_user_results_by_admin_and_owner(current_user.id, user_id, company_id)


@quiz_router.get(
    "/companies/{company_id}/results",
    status_code=status.HTTP_200_OK,
)
async def get_everyone_quiz_results(
    company_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    return await quiz_service.get_all_results_by_admin_and_owner(
        current_user.id, company_id
    )


@quiz_router.get(
    "/companies/{company_id}/quizzes/{quiz_id}/results/me",
    status_code=status.HTTP_200_OK,
)
async def get_my_quiz_results(
    company_id: UUID,
    quiz_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    return await quiz_service.get_my_quiz_result(current_user.id, company_id, quiz_id)


@quiz_router.get(
    "/companies/{company_id}/quizzes/{quiz_id}/results/export",
    status_code=status.HTTP_200_OK,
)
async def export_quiz_results(
    company_id: UUID,
    quiz_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    results = await quiz_service.get_quiz_results_for_export(
        current_user.id, company_id, quiz_id
    )
    csv_data = Formatter.quiz_results_to_csv(results)
    return StreamingResponse(
        io.StringIO(csv_data),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=quiz_{quiz_id}_results.csv"},
    )
