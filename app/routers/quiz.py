import io
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status, Security
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.utils.formatter import Formatter

from app.schemas.quiz import (
    QuizCreateRequestSchema,
    QuizUpdateRequestSchema,
    QuizResponseSchema,
    PaginatedQuizResponseSchema,
)
from app.schemas.quiz_result import (
    QuizResultResponseSchema,
    QuizSubmitSchema
)
from app.services.quiz_service import QuizService, get_quiz_service
from app.services.user_service import UserService, get_user_service

quiz_router = APIRouter()


@quiz_router.post(
    "/companies/{company_id}/quizzes",
    response_model=QuizResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_quiz(
    company_id: UUID,
    data: QuizCreateRequestSchema,
    user_details: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    user_service: UserService = Depends(get_user_service),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    current_user = await user_service.get_current_user(user_details.credentials)
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
    user_details: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    user_service: UserService = Depends(get_user_service),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    current_user = await user_service.get_current_user(user_details.credentials)
    quiz = await quiz_service.update_quiz(quiz_id, company_id, current_user.id, data)
    return QuizResponseSchema.model_validate(quiz)


@quiz_router.delete(
    "/companies/{company_id}/quizzes/{quiz_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_quiz(
    company_id: UUID,
    quiz_id: UUID,
    user_details: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    user_service: UserService = Depends(get_user_service),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    current_user = await user_service.get_current_user(user_details.credentials)
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
    "/companies/{company_id}/quizzes/{quiz_id}/take",
    response_model=QuizResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_quiz_for_member(
    company_id: UUID,
    quiz_id: UUID,
    user_details: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    user_service: UserService = Depends(get_user_service),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    current_user = await user_service.get_current_user(user_details.credentials)
    quiz = await quiz_service.get_quiz_by_company_member(company_id, current_user.id, quiz_id)
    return QuizResponseSchema.model_validate(quiz)


@quiz_router.post(
    "/companies/{company_id}/quizzes/{quiz_id}/submit",
    response_model=QuizResultResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def submit_quiz(
    company_id: UUID,
    quiz_id: UUID,
    data: QuizSubmitSchema,
    user_details: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    user_service: UserService = Depends(get_user_service),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    current_user = await user_service.get_current_user(user_details.credentials)
    result = await quiz_service.submit_quiz(company_id, quiz_id, current_user.id, data)
    return QuizResultResponseSchema.model_validate(result)


@quiz_router.get(
    "/companies/{company_id}/users/me/average",
    response_model=float,
    status_code=status.HTTP_200_OK,
)
async def get_average_by_company(
    company_id: UUID,
    user_details: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    user_service: UserService = Depends(get_user_service),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    current_user = await user_service.get_current_user(user_details.credentials)
    return await quiz_service.get_average_by_company(current_user.id, company_id)


@quiz_router.get(
    "/users/me/average",
    response_model=float,
    status_code=status.HTTP_200_OK,
)
async def get_average_by_system(
    user_details: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    user_service: UserService = Depends(get_user_service),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    current_user = await user_service.get_current_user(user_details.credentials)
    return await quiz_service.get_average_by_system(current_user.id)


@quiz_router.get(
    "/companies/{company_id}/users/{user_id}/results",
    status_code=status.HTTP_200_OK
)
async def get_user_quiz_results(
    company_id: UUID,
    user_id: UUID,
    user_details: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    user_service: UserService = Depends(get_user_service),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    current_user = await user_service.get_current_user(user_details.credentials)
    return await quiz_service.get_user_results_by_admin_and_owner(current_user.id, user_id, company_id)


@quiz_router.get(
    "/companies/{company_id}/results",
    status_code=status.HTTP_200_OK
)
async def get_everyone_quiz_results(
    company_id: UUID,
    user_details: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    user_service: UserService = Depends(get_user_service),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    current_user = await user_service.get_current_user(user_details.credentials)
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
    user_details: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    user_service: UserService = Depends(get_user_service),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    current_user = await user_service.get_current_user(user_details.credentials)
    return await quiz_service.get_my_quiz_result(current_user.id, company_id, quiz_id)


@quiz_router.get(
    "/companies/{company_id}/quizzes/{quiz_id}/results/export",
    status_code=status.HTTP_200_OK,
)
async def export_quiz_results(
    company_id: UUID,
    quiz_id: UUID,
    user_details: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    user_service: UserService = Depends(get_user_service),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    current_user = await user_service.get_current_user(user_details.credentials)
    results = await quiz_service.get_quiz_results_for_export(
        current_user.id, company_id, quiz_id
    )
    csv_data = Formatter.quiz_results_to_csv(results)
    return StreamingResponse(
        io.StringIO(csv_data),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=quiz_{quiz_id}_results.csv"},
    )
