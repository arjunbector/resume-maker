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
def get_user(email: str):
    try:
        logger.info(f"Fetching user with email: {email}")
        result = UserOperations.get_user(email)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch user: {str(e)}")

@router.put("")
def update_user(email: str, updates: Dict[str, Any]):
    try:
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
    Add items to the user's knowledge graph.

    This endpoint allows adding one or multiple items to different categories
    of the knowledge graph in a single request. Items are appended to existing data.

    Categories:
    - education: List of education entries (degree, institution, year, etc.)
    - work_experience: List of work experience entries (company, role, duration, etc.)
    - research_work: List of research work entries
    - projects: List of project entries
    - certifications: List of certification entries
    - skills: List of skill strings
    - misc: Dictionary for miscellaneous information
    """
    try:
        user_id = current_user['user_id']
        email = current_user['email']

        logger.info(f"Adding items to knowledge graph for user: {email}")

        # Get current user data
        user = UserOperations.get_user_by_id(user_id)
        current_kg = user.get('knowledge_graph', {})

        # Track what was added
        added_items = {}

        # Build update operations using MongoDB $push for arrays and $set for objects
        update_operations = {}

        if updates.education is not None and len(updates.education) > 0:
            update_operations["knowledge_graph.education"] = current_kg.get('education', []) + updates.education
            added_items['education'] = len(updates.education)

        if updates.work_experience is not None and len(updates.work_experience) > 0:
            update_operations["knowledge_graph.work_experience"] = current_kg.get('work_experience', []) + updates.work_experience
            added_items['work_experience'] = len(updates.work_experience)

        if updates.research_work is not None and len(updates.research_work) > 0:
            update_operations["knowledge_graph.research_work"] = current_kg.get('research_work', []) + updates.research_work
            added_items['research_work'] = len(updates.research_work)

        if updates.projects is not None and len(updates.projects) > 0:
            update_operations["knowledge_graph.projects"] = current_kg.get('projects', []) + updates.projects
            added_items['projects'] = len(updates.projects)

        if updates.certifications is not None and len(updates.certifications) > 0:
            update_operations["knowledge_graph.certifications"] = current_kg.get('certifications', []) + updates.certifications
            added_items['certifications'] = len(updates.certifications)

        if updates.skills is not None and len(updates.skills) > 0:
            # For skills, avoid duplicates
            current_skills = set(current_kg.get('skills', []))
            new_skills = [skill for skill in updates.skills if skill not in current_skills]
            if new_skills:
                update_operations["knowledge_graph.skills"] = list(current_skills) + new_skills
                added_items['skills'] = len(new_skills)

        if updates.misc is not None:
            # Merge misc dictionaries
            current_misc = current_kg.get('misc', {})
            current_misc.update(updates.misc)
            update_operations["knowledge_graph.misc"] = current_misc
            added_items['misc'] = len(updates.misc)

        if not update_operations:
            raise HTTPException(status_code=400, detail="No items provided to add")

        # Update the user
        result = UserOperations.update_user(email, update_operations)

        logger.info(f"Successfully added items to knowledge graph: {added_items}")

        return {
            "message": "Items added to knowledge graph successfully",
            "user_id": user_id,
            "email": email,
            "added_items": added_items,
            "total_items_added": sum(v for v in added_items.values() if isinstance(v, int))
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding to knowledge graph: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add to knowledge graph: {str(e)}")
