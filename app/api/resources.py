from fastapi import APIRouter, Depends

from app.api.deps import require_permission


router = APIRouter(prefix="/resources", tags=["Resources"])


@router.get("/documents")
def get_documents(
    _: None = Depends(require_permission("documents", "read")),
) -> dict[str, list[dict[str, str]]]:

    return {
        "items": [
            {"id": "1", "title": "Public document"},
            {"id": "2", "title": "Internal document"},
        ]
    }


@router.get("/reports")
def get_reports(
    _: None = Depends(require_permission("reports", "read")),
) -> dict[str, list[dict[str, str]]]:
    
    return {
        "items": [
            {"id": "1", "name": "Sales report"},
            {"id": "2", "name": "Audit report"},
        ]
    }


@router.get("/admin-panel")
def get_admin_panel(
    _: None = Depends(require_permission("roles", "manage"))
) -> dict[str, str]:
    
    return {"message": "Welcome to admin panel"}
