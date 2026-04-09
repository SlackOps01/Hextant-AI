from fastapi import Depends, HTTPException, status, Path
from app.core.oauth2 import TokenData
from app.shared.enums import Role
# Assuming you already have a dependency that gets the token/user
from app.core.deps import get_current_user 

class UserActionForbiddenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Action forbidden!")

# 1. Dependency for Admin-Only routes
def require_admin(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    if current_user.role != Role.ADMIN.value:
        raise UserActionForbiddenException()
    return current_user

# 2. Dependency for Owner-OR-Admin routes
def require_owner_or_admin(
    # FastAPI automatically pulls the {user_id} from your route's URL!
    user_id: str = Path(...), 
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    if current_user.role != Role.ADMIN.value and current_user.id != user_id:
        raise UserActionForbiddenException()
    return current_user