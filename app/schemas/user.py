from typing import Annotated
from pydantic import BaseModel, constr


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: Annotated[
        str,
        constr(min_length=8, regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).+$"),
    ]
