"""API routes for user feedback submission."""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel

from backend.exceptions import EmailError
from backend.services.email_service import get_email_service

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api", tags=["feedback"])

# Constants
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB for images
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB for videos
MAX_TOTAL_SIZE = 100 * 1024 * 1024  # 100MB total
MAX_FILES = 5
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}
ALLOWED_CONTENT_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES


class FeedbackResponse(BaseModel):
    """Response schema for feedback submission."""

    success: bool
    message: str


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit user feedback",
    description="Submit feedback with optional file attachments (images/videos).",
)
async def submit_feedback(
    feedback_text: str = Form(..., min_length=1, max_length=5000),
    user_name: Optional[str] = Form(default=None),
    user_email: Optional[str] = Form(default=None),
    files: Optional[List[UploadFile]] = File(default=None),
) -> FeedbackResponse:
    """
    Submit user feedback with optional file attachments.

    Args:
        feedback_text: The feedback message (required, 1-5000 characters)
        files: Optional list of image/video files (max 5 files, 10MB each)

    Returns:
        FeedbackResponse with success status and message

    Raises:
        HTTPException: If validation fails or email sending fails
    """
    logger.info("Feedback submission received")

    # Validate files if provided
    validated_files: List[tuple[str, bytes, str]] = []

    if files:
        # Check file count
        if len(files) > MAX_FILES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {MAX_FILES} files allowed",
            )

        total_size = 0

        for file in files:
            # Skip empty file inputs
            if not file.filename:
                continue

            # Check content type
            if file.content_type not in ALLOWED_CONTENT_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type '{file.content_type}' not allowed. Only images and videos are accepted.",
                )

            # Read file content
            content = await file.read()
            file_size = len(content)

            # Check individual file size (different limits for images vs videos)
            is_video = file.content_type in ALLOWED_VIDEO_TYPES
            max_size = MAX_VIDEO_SIZE if is_video else MAX_IMAGE_SIZE
            max_size_label = "50MB" if is_video else "10MB"
            if file_size > max_size:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File '{file.filename}' exceeds maximum size of {max_size_label}",
                )

            total_size += file_size

            # Check total size
            if total_size > MAX_TOTAL_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Total file size exceeds maximum of 100MB",
                )

            validated_files.append((file.filename, content, file.content_type))
            logger.info(f"Validated file: {file.filename} ({file_size} bytes)")

    # Send feedback email
    try:
        email_service = get_email_service()
        await email_service.send_feedback_email(
            feedback_text=feedback_text,
            user_name=user_name,
            user_email=user_email,
            attachments=validated_files if validated_files else None,
        )
        logger.info("Feedback email sent successfully")
        return FeedbackResponse(
            success=True,
            message="Thank you for your feedback!",
        )

    except EmailError as e:
        logger.error(f"Failed to send feedback email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send feedback. Please try again later.",
        )
    except Exception as e:
        logger.error(f"Unexpected error submitting feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )
