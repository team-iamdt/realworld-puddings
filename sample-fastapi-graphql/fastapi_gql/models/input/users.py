from pydantic import BaseModel, EmailStr, Field
import strawberry


class BaseUserInput(BaseModel):
    email: EmailStr
    name: str = Field(min_length=3)
    password: str


class BaseSignInInput(BaseModel):
    email: EmailStr
    password: str


# Be careful, we are using experimental features of strawberry.
@strawberry.experimental.pydantic.input(model=BaseUserInput)
class UserInput:
    email: strawberry.auto
    name: strawberry.auto
    password: strawberry.auto


@strawberry.experimental.pydantic.input(model=BaseSignInInput)
class SignInInput:
    email: strawberry.auto
    password: strawberry.auto
