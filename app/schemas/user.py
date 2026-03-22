from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    last_name: str
    first_name: str
    middle_name: str | None
    status: str


class UpdateUserRequest(BaseModel):
    email: EmailStr | None = None
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    middle_name: str | None = Field(default=None, max_length=50)


class CurrentUserResponse(BaseModel):
    id: int
    email: EmailStr
    last_name: str
    first_name: str
    middle_name: str | None
    status: str
    roles: list[str]
