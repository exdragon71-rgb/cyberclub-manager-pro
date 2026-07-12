import json
from pathlib import Path
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from pydantic import (
    TypeAdapter,
    ValidationError,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.integrations.lightshell.pdf_parser import (
    LightShellPdfParseError,
    parse_lightshell_inventory_pdf,
)
from app.integrations.lightshell.schemas import (
    LightShellImportApplyResult,
    LightShellImportPreview,
    LightShellImportResolution,
)
from app.services.lightshell_import import (
    LightShellImportValidationError,
    lightshell_import_service,
)
from app.services.product import (
    ProductAlreadyExistsError,
    ProductValidationError,
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


resolution_list_adapter = TypeAdapter(
    list[LightShellImportResolution]
)


def validate_source_filename(
    filename: str | None,
) -> str:
    source_filename = Path(
        filename
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

    return source_filename


async def read_pdf_content(
    file: UploadFile,
) -> bytes:
    file_content = await file.read(
        MAX_PDF_SIZE + 1
    )

    if len(file_content) > MAX_PDF_SIZE:
        raise HTTPException(
            status_code=(
                status.HTTP_413_CONTENT_TOO_LARGE
            ),
            detail=(
                "Размер PDF превышает "
                "допустимые 10 МБ."
            ),
        )

    return file_content


def parse_pdf_document(
    file_content: bytes,
):
    try:
        return parse_lightshell_inventory_pdf(
            file_content
        )

    except LightShellPdfParseError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=str(error),
        ) from error


@router.post(
    "/preview",
    response_model=LightShellImportPreview,
    summary="Предпросмотр импорта ревизии LightShell",
)
async def preview_lightshell_import(
    db: DatabaseSession,
    file: UploadFile = File(...),
):
    source_filename = (
        validate_source_filename(
            file.filename
        )
    )

    file_content = await read_pdf_content(
        file
    )

    document = parse_pdf_document(
        file_content
    )

    return lightshell_import_service.build_preview(
        db,
        document=document,
        source_filename=source_filename,
    )


@router.post(
    "/apply",
    response_model=LightShellImportApplyResult,
    summary="Применить импорт ревизии LightShell",
)
async def apply_lightshell_import(
    db: DatabaseSession,
    file: UploadFile = File(...),
    resolutions_json: str = Form(...),
):
    source_filename = (
        validate_source_filename(
            file.filename
        )
    )

    file_content = await read_pdf_content(
        file
    )

    document = parse_pdf_document(
        file_content
    )

    try:
        raw_resolutions = json.loads(
            resolutions_json
        )

        resolutions = (
            resolution_list_adapter
            .validate_python(
                raw_resolutions
            )
        )

    except (
        json.JSONDecodeError,
        ValidationError,
    ) as error:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=(
                "Список решений по позициям "
                "имеет неверный формат."
            ),
        ) from error

    try:
        return (
            lightshell_import_service
            .apply_import(
                db,
                document=document,
                source_filename=(
                    source_filename
                ),
                resolutions=resolutions,
            )
        )

    except LightShellImportValidationError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=str(error),
        ) from error

    except ProductValidationError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=str(error),
        ) from error

    except ProductAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error