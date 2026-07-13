import os

from django.core.exceptions import ValidationError

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
ALLOWED_MEDIA_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | {'.mp4', '.webm', '.mov'}

MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_VIDEO_SIZE = 100 * 1024 * 1024


def _extension(name: str) -> str:
    return os.path.splitext(name)[1].lower()


def validate_image_upload(upload) -> None:
    if not upload:
        return

    extension = _extension(upload.name)
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f'Unsupported image type "{extension or "unknown"}". '
            f'Allowed: {", ".join(sorted(ALLOWED_IMAGE_EXTENSIONS))}.'
        )

    if upload.size > MAX_IMAGE_SIZE:
        raise ValidationError(
            f'Image is too large ({upload.size // (1024 * 1024)} MB). '
            f'Maximum size is {MAX_IMAGE_SIZE // (1024 * 1024)} MB.'
        )


def validate_media_upload(upload) -> None:
    if not upload:
        return

    extension = _extension(upload.name)
    if extension not in ALLOWED_MEDIA_EXTENSIONS:
        raise ValidationError(
            f'Unsupported file type "{extension or "unknown"}". '
            f'Allowed: {", ".join(sorted(ALLOWED_MEDIA_EXTENSIONS))}.'
        )

    max_size = MAX_VIDEO_SIZE if extension in {'.mp4', '.webm', '.mov'} else MAX_IMAGE_SIZE
    if upload.size > max_size:
        raise ValidationError(
            f'File is too large ({upload.size // (1024 * 1024)} MB). '
            f'Maximum size is {max_size // (1024 * 1024)} MB.'
        )
