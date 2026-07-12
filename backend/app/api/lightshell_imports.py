from pathlib import Path
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.integrations.lightshell.pdf_parser import (
    LightShellPdfParseError,
    parse_lightshell_inventory_pdf,
)
from app.integrations.lightshell.schemas import (
    LightShellImportPreview,
)
from app.services.lightshell_import import (
    lightshell_import_service,
)


router = APIRouter(
    prefix="/lightshell-imports",
    tags=["LightShell imports"],
)


DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


MAX_PDF_SIZE = 10 * 1024 * 1024


@router.post(
    "/preview",
    response_model=LightShellImportPreview,
    summary="Предпросмотр импорта ревизии LightShell",
)
async def preview_lightshell_import(
    db: DatabaseSession,
    file: UploadFile = File(...),
):
    source_filename = Path(
        file.filename
        or "lightshell_inventory.pdf"
    ).name

    if not source_filename.lower().endswith(
        ".pdf"
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail="Можно загрузить только PDF-файл.",
        )

    if len(source_filename) > 255:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=(
                "Название PDF-файла "
                "слишком длинное."
            ),
        )

    file_content = await file.read(
        MAX_PDF_SIZE + 1
    )

    if len(file_content) > MAX_PDF_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=(
                "Размер PDF превышает "
                "допустимые 10 МБ."
            ),
        )

    try:
        document = (
            parse_lightshell_inventory_pdf(
                file_content
            )
        )

    except LightShellPdfParseError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=str(error),
        ) from error

    return lightshell_import_service.build_preview(
        db,
        document=document,
        source_filename=source_filename,
    )