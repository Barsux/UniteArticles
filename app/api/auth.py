from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models.auth import UserCreate, User, Token, Roles, UserRole
from app.services.auth import AuthService, get_curr_user

router = APIRouter(
    prefix = "/auth"
)

@router.post('/sign-up', response_model=Token)
def sign_up(
        user_data: UserCreate,
        service: AuthService = Depends()
):
    return service.register(user_data)

@router.post('/sign-in', response_model=Token)
def sign_in(
        form_data: OAuth2PasswordRequestForm = Depends(),
        service: AuthService = Depends()
):
    return service.login(
        form_data.username,
        form_data.password,
    )

@router.put('/role', response_model=User)
def change_role(
        replace: bool,
        role: UserRole,
        user_id: int,
        user: User = Depends(get_curr_user),
        service: AuthService = Depends()
):
    return service.change_role(user, user_id, role, replace)
@router.get('/user', response_model=User)
def get_user(user: User = Depends(get_curr_user)):
    return user

@router.get('/user/{user_id}', response_model=User)
def show_user(
        user_id:int,
        user: User = Depends(get_curr_user),
        service: AuthService = Depends()
):
    return service.get_user(user, user_id)

@router.put('/user/{user_id}/', response_model=User)
def update_user(
        user_data: User,
        user: User = Depends(get_curr_user),
        service: AuthService = Depends()
):
    return service.update_user(user, user_data)