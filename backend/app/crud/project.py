"""CRUD operations for projects."""

from uuid import UUID
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.threat_intel import Project


async def get_project(db: AsyncSession, project_id: UUID) -> Optional[Project]:
    """Get project by ID."""
    return await db.get(Project, project_id)


async def get_projects_by_org(
    db: AsyncSession,
    org_id: UUID,
    include_archived: bool = False,
    limit: int = 100,
    offset: int = 0,
) -> List[Project]:
    """
    Get all projects for an organization.

    Args:
        db: Database session
        org_id: Organization ID
        include_archived: Include archived projects
        limit: Maximum number of results
        offset: Offset for pagination

    Returns:
        List of projects
    """
    query = select(Project).filter(Project.org_id == org_id)

    if not include_archived:
        query = query.filter(Project.archived == False)

    query = query.order_by(Project.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    return list(result.scalars().all())


async def create_project(
    db: AsyncSession,
    org_id: UUID,
    name: str,
    created_by: UUID,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    settings: Optional[dict] = None,
) -> Project:
    """
    Create new project.

    Args:
        db: Database session
        org_id: Organization ID
        name: Project name
        created_by: User ID who created the project
        description: Optional description
        tags: Optional tags
        settings: Optional settings

    Returns:
        Created project
    """
    project = Project(
        org_id=org_id,
        name=name,
        description=description,
        tags=tags or [],
        settings=settings or {},
        created_by=created_by,
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def update_project(
    db: AsyncSession,
    project_id: UUID,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    settings: Optional[dict] = None,
    archived: Optional[bool] = None,
) -> Optional[Project]:
    """
    Update project.

    Args:
        db: Database session
        project_id: Project ID
        name: New name
        description: New description
        tags: New tags
        settings: New settings (merged with existing)
        archived: Archive status

    Returns:
        Updated project or None if not found
    """
    project = await db.get(Project, project_id)
    if not project:
        return None

    if name is not None:
        project.name = name
    if description is not None:
        project.description = description
    if tags is not None:
        project.tags = tags
    if settings is not None:
        # Merge settings
        project.settings = {**(project.settings or {}), **settings}
    if archived is not None:
        project.archived = archived

    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project_id: UUID) -> bool:
    """
    Delete project (cascades to all related entities).

    Args:
        db: Database session
        project_id: Project ID

    Returns:
        True if deleted, False if not found
    """
    project = await db.get(Project, project_id)
    if not project:
        return False

    await db.delete(project)
    await db.commit()
    return True


async def get_project_stats(db: AsyncSession, project_id: UUID) -> dict:
    """
    Get project statistics.

    Args:
        db: Database session
        project_id: Project ID

    Returns:
        Dictionary with statistics
    """
    from app.models.threat_intel import Indicator, ThreatActor, Campaign

    project = await db.get(Project, project_id)
    if not project:
        return {}

    # Count indicators
    indicator_result = await db.execute(
        select(func.count(Indicator.id)).filter(Indicator.project_id == project_id)
    )
    indicator_count = indicator_result.scalar() or 0

    # Count threat actors
    threat_actor_result = await db.execute(
        select(func.count(ThreatActor.id)).filter(ThreatActor.project_id == project_id)
    )
    threat_actor_count = threat_actor_result.scalar() or 0

    # Count campaigns
    campaign_result = await db.execute(
        select(func.count(Campaign.id)).filter(Campaign.project_id == project_id)
    )
    campaign_count = campaign_result.scalar() or 0

    # Count recent activity (last 7 days)
    from datetime import datetime, timedelta

    recent_date = datetime.utcnow() - timedelta(days=7)
    recent_indicators_result = await db.execute(
        select(func.count(Indicator.id)).filter(
            Indicator.project_id == project_id,
            Indicator.created_at >= recent_date,
        )
    )
    recent_activity_count = recent_indicators_result.scalar() or 0

    return {
        "total_indicators": indicator_count,
        "total_threat_actors": threat_actor_count,
        "total_campaigns": campaign_count,
        "recent_activity_count": recent_activity_count,
        "risk_score": None,  # TODO: Calculate risk score based on indicators
    }


async def archive_project(db: AsyncSession, project_id: UUID) -> Optional[Project]:
    """Archive project."""
    return await update_project(db, project_id, archived=True)


async def unarchive_project(db: AsyncSession, project_id: UUID) -> Optional[Project]:
    """Unarchive project."""
    return await update_project(db, project_id, archived=False)
