from pydantic import BaseModel, ConfigDict


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resource: str
    action: str
    description: str | None


class AssignPermissionRequest(BaseModel):
    permission_id: int
