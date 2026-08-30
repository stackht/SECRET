"""Case data source endpoints (Phase 2-3)."""
from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile, status

from app.api.deps import CurrentUser, DbSession, RequireAnalyst
from app.schemas.source import SourceCreate, SourceProcessResult, SourceRead, SourceUploadResult
from app.services.source_service import SourceService

router = APIRouter()


@router.post(
    "/{case_key}/sources/upload",
    response_model=SourceUploadResult,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and ingest a case data source file",
)
async def upload_source(
    case_key: str,
    session: DbSession,
    _: RequireAnalyst,
    file: Annotated[UploadFile, File()],
    source_type: Annotated[str, Form()],
    source_id: Annotated[str | None, Form()] = None,
) -> SourceUploadResult:
    content = await file.read()
    result = await SourceService(session).upload(case_key, source_type, file.filename, content, source_id)
    await session.commit()
    return result


@router.post(
    "/{case_key}/sources",
    response_model=SourceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a case data source",
)
async def register_source(
    case_key: str,
    payload: SourceCreate,
    session: DbSession,
    _: RequireAnalyst,
) -> SourceRead:
    source = await SourceService(session).register(case_key, payload)
    await session.commit()
    await session.refresh(source)
    return _to_read(source)


@router.get(
    "/{case_key}/sources",
    response_model=list[SourceRead],
    summary="List case data sources",
)
async def list_sources(
    case_key: str,
    session: DbSession,
    _user: CurrentUser,
) -> list[SourceRead]:
    sources = await SourceService(session).list_for_case(case_key)
    return [_to_read(s) for s in sources]


@router.post(
    "/{case_key}/sources/{source_id}/process",
    response_model=SourceProcessResult,
    summary="Process a registered source through the ingestion pipeline",
)
async def process_source(
    case_key: str,
    source_id: str,
    session: DbSession,
    _: RequireAnalyst,
) -> SourceProcessResult:
    result = await SourceService(session).process(case_key, source_id)
    await session.commit()
    return SourceProcessResult(**result)


@router.delete(
    "/{case_key}/sources/{source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a case data source",
)
async def delete_source(
    case_key: str,
    source_id: str,
    session: DbSession,
    _: RequireAnalyst,
) -> None:
    await SourceService(session).delete(case_key, source_id)
    await session.commit()


def _to_read(source) -> SourceRead:
    return SourceRead(
        id=source.id,
        source_id=source.source_id,
        filename=source.filename,
        file_type=source.file_type,
        source_type=source.source_type,
        status=source.status,
        record_count=source.record_count,
        processing_error=source.processing_error,
        metadata_json=source.metadata_json or {},
        uploaded_at=source.uploaded_at,
        processed_at=source.processed_at,
    )
