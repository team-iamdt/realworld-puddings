from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field

import strawberry


class BaseUserInput(BaseModel):
    email: EmailStr
    name: str = Field(min_length=3)
    password: str


class BaseSignInInput(BaseModel):
    email: EmailStr
    password: str


# Be careful, we are using experimental features of strawberry.
@strawberry.experimental.pydantic.input(model=BaseUserInput, all_fields=True)
class UserInput:
    pass


@strawberry.experimental.pydantic.input(model=BaseSignInInput, all_fields=True)
class SignInInput:
    pass
