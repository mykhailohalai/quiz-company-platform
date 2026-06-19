from uuid import UUID

from fastapi import APIRouter, Depends, Query, status, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.quiz import (
    QuizCreateRequestSchema,
    QuizUpdateRequestSchema,
    QuizResponseSchema,
    PaginatedQuizResponseSchema,
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
