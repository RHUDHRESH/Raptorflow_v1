"""Project endpoints for threat intelligence projects."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_with_org, require_role
from app.crud.project import (
    create_project,
    delete_project,
    get_project,
    get_projects_by_org,
    get_project_stats,
    update_project,
    archive_project,
    unarchive_project,
)
from app.db.session import get_db
from app.models.user import Organization
from app.schemas.auth import Principal

router = APIRouter(prefix="/projects", tags=["projects"])


# ==========================================
# Request/Response Schemas
# ==========================================


class CreateProjectRequest(BaseModel):
    """Request to create project."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    tags: List[str] = Field(default_factory=list)
    settings: dict = Field(default_factory=dict)


class UpdateProjectRequest(BaseModel):
    """Request to update project."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    tags: List[str] | None = None
    settings: dict | None = None
    archived: bool | None = None


class ProjectResponse(BaseModel):
    """Project response."""

    id: UUID
    org_id: UUID
    name: str
    description: str | None
    tags: List[str]
    settings: dict
    archived: bool
    created_at: str
    updated_at: str
    created_by: UUID
    indicator_count: int | None = None
    threat_actor_count: int | None = None

    class Config:
        from_attributes = True


class ProjectStatsResponse(BaseModel):
    """Project statistics."""

    total_indicators: int
    total_threat_actors: int
    total_campaigns: int
    recent_activity_count: int
    risk_score: float | None


# ==========================================
# Project Endpoints
# ==========================================


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    principal: Principal = Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db),
    include_archived: bool = False,
):
    """
    List all projects in organization.

    By default, only active projects are returned.
    Use `include_archived=true` to include archived projects.
    """
    projects = await get_projects_by_org(
        db,
        org_id=principal.org_id,
        include_archived=include_archived,
    )

    return [
        ProjectResponse(
            id=p.id,
            org_id=p.org_id,
            name=p.name,
            description=p.description,
            tags=p.tags or [],
            settings=p.settings or {},
            archived=p.archived,
            created_at=p.created_at.isoformat(),
            updated_at=p.updated_at.isoformat(),
            created_by=p.created_by,
        )
        for p in projects
    ]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project_endpoint(
    request: CreateProjectRequest,
    principal: Principal = Depends(require_role("editor")),
    db: AsyncSession = Depends(get_db),
):
    """
    Create new project.

    Requires editor role or higher.
    """
    # Verify organization exists
    org = await db.get(Organization, principal.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Create project
    project = await create_project(
        db,
        org_id=principal.org_id,
        name=request.name,
        created_by=principal.user_id,
        description=request.description,
        tags=request.tags,
        settings=request.settings,
    )

    return ProjectResponse(
        id=project.id,
        org_id=project.org_id,
        name=project.name,
        description=project.description,
        tags=project.tags or [],
        settings=project.settings or {},
        archived=project.archived,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat(),
        created_by=project.created_by,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_endpoint(
    project_id: UUID,
    principal: Principal = Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db),
):
    """
    Get project details.

    Project must belong to user's current organization.
    """
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify org ownership
    if project.org_id != principal.org_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return ProjectResponse(
        id=project.id,
        org_id=project.org_id,
        name=project.name,
        description=project.description,
        tags=project.tags or [],
        settings=project.settings or {},
        archived=project.archived,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat(),
        created_by=project.created_by,
    )


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project_endpoint(
    project_id: UUID,
    request: UpdateProjectRequest,
    principal: Principal = Depends(require_role("editor")),
    db: AsyncSession = Depends(get_db),
):
    """
    Update project.

    Requires editor role or higher.
    """
    # Verify project exists and belongs to org
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.org_id != principal.org_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update project
    updated_project = await update_project(
        db,
        project_id=project_id,
        name=request.name,
        description=request.description,
        tags=request.tags,
        settings=request.settings,
        archived=request.archived,
    )

    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectResponse(
        id=updated_project.id,
        org_id=updated_project.org_id,
        name=updated_project.name,
        description=updated_project.description,
        tags=updated_project.tags or [],
        settings=updated_project.settings or {},
        archived=updated_project.archived,
        created_at=updated_project.created_at.isoformat(),
        updated_at=updated_project.updated_at.isoformat(),
        created_by=updated_project.created_by,
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_endpoint(
    project_id: UUID,
    principal: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete project.

    Requires admin role or higher.
    This will cascade delete all related data (indicators, threat actors, etc.).
    """
    # Verify project exists and belongs to org
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.org_id != principal.org_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Delete project
    success = await delete_project(db, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")

    return None


@router.get("/{project_id}/stats", response_model=ProjectStatsResponse)
async def get_project_stats_endpoint(
    project_id: UUID,
    principal: Principal = Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db),
):
    """
    Get project statistics.

    Returns counts and analytics for project entities.
    """
    # Verify project exists and belongs to org
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.org_id != principal.org_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get statistics
    stats = await get_project_stats(db, project_id)

    return ProjectStatsResponse(**stats)


@router.post("/{project_id}/archive", response_model=ProjectResponse)
async def archive_project_endpoint(
    project_id: UUID,
    principal: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    Archive project.

    Archived projects are hidden by default but data is preserved.
    Requires admin role or higher.
    """
    # Verify project exists and belongs to org
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.org_id != principal.org_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Archive project
    archived_project = await archive_project(db, project_id)
    if not archived_project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectResponse(
        id=archived_project.id,
        org_id=archived_project.org_id,
        name=archived_project.name,
        description=archived_project.description,
        tags=archived_project.tags or [],
        settings=archived_project.settings or {},
        archived=archived_project.archived,
        created_at=archived_project.created_at.isoformat(),
        updated_at=archived_project.updated_at.isoformat(),
        created_by=archived_project.created_by,
    )


@router.post("/{project_id}/unarchive", response_model=ProjectResponse)
async def unarchive_project_endpoint(
    project_id: UUID,
    principal: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    Unarchive project.

    Restores project to active state.
    Requires admin role or higher.
    """
    # Verify project exists and belongs to org
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.org_id != principal.org_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Unarchive project
    unarchived_project = await unarchive_project(db, project_id)
    if not unarchived_project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectResponse(
        id=unarchived_project.id,
        org_id=unarchived_project.org_id,
        name=unarchived_project.name,
        description=unarchived_project.description,
        tags=unarchived_project.tags or [],
        settings=unarchived_project.settings or {},
        archived=unarchived_project.archived,
        created_at=unarchived_project.created_at.isoformat(),
        updated_at=unarchived_project.updated_at.isoformat(),
        created_by=unarchived_project.created_by,
    )
