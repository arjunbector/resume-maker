from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from database.models import User
from database.operations import UserOperations
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])


class KnowledgeGraphUpdate(BaseModel):
    education: Optional[List[Dict]] = None
    work_experience: Optional[List[Dict]] = None
    research_work: Optional[List[Dict]] = None
    projects: Optional[List[Dict]] = None
    certifications: Optional[List[Dict]] = None
    skills: Optional[List[str]] = None
    misc: Optional[Dict] = None

@router.get("")
def get_user(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user's profile.
    Uses authentication (cookie or Authorization header) to identify the user.
    """
    try:
        email = current_user['email']
        logger.info(f"Fetching user with email: {email}")
        result = UserOperations.get_user(email)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch user: {str(e)}")

@router.put("")
def update_user(updates: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    """
    Update current authenticated user's profile.
    Uses authentication (cookie or Authorization header) to identify the user.
    """
    try:
        email = current_user['email']
        logger.info(f"Updating user with email: {email}")
        result = UserOperations.update_user(email, updates)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")


@router.post("/knowledge-graph/add")
def add_to_knowledge_graph(
    updates: KnowledgeGraphUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Set/replace items in the user's knowledge graph.

    This endpoint allows setting one or multiple categories of the knowledge graph
    in a single request. Items are SET directly, replacing existing data in those categories.

    Categories:
    - education: List of education entries (degree, institution, year, etc.)
    - work_experience: List of work experience entries (company, role, duration, etc.)
    - research_work: List of research work entries
    - projects: List of project entries
    - certifications: List of certification entries
    - skills: List of skill strings
    - misc: Dictionary for miscellaneous information

    Note: Only the categories provided in the request will be updated.
    Categories not included will remain unchanged.
    """
    try:
        user_id = current_user['user_id']
        email = current_user['email']

        logger.info(f"Setting knowledge graph items for user: {email}")

        # Track what was set
        set_items = {}

        # Build update operations - directly set the provided data
        update_operations = {}

        if updates.education is not None:
            update_operations["knowledge_graph.education"] = updates.education
            set_items['education'] = len(updates.education)

        if updates.work_experience is not None:
            update_operations["knowledge_graph.work_experience"] = updates.work_experience
            set_items['work_experience'] = len(updates.work_experience)

        if updates.research_work is not None:
            update_operations["knowledge_graph.research_work"] = updates.research_work
            set_items['research_work'] = len(updates.research_work)

        if updates.projects is not None:
            update_operations["knowledge_graph.projects"] = updates.projects
            set_items['projects'] = len(updates.projects)

        if updates.certifications is not None:
            update_operations["knowledge_graph.certifications"] = updates.certifications
            set_items['certifications'] = len(updates.certifications)

        if updates.skills is not None:
            update_operations["knowledge_graph.skills"] = updates.skills
            set_items['skills'] = len(updates.skills)

        if updates.misc is not None:
            update_operations["knowledge_graph.misc"] = updates.misc
            set_items['misc'] = len(updates.misc) if isinstance(updates.misc, dict) else 1

        if not update_operations:
            raise HTTPException(status_code=400, detail="No items provided to set")

        # Update the user
        result = UserOperations.update_user(email, update_operations)

        logger.info(f"Successfully set knowledge graph items: {set_items}")

        return {
            "message": "Knowledge graph items set successfully",
            "user_id": user_id,
            "email": email,
            "set_items": set_items,
            "total_items_set": sum(v for v in set_items.values() if isinstance(v, int))
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding to knowledge graph: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add to knowledge graph: {str(e)}")
