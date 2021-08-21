from views.auth import UserRegister, UserLogin, RefreshToken
from views.users import UserListView, UserDetailView


def setup_routes(app):
    app.router.add_view('/auth/v1/register', UserRegister)
    app.router.add_view('/auth/v1/login', UserLogin)
    app.router.add_view('/auth/v1/refresh', RefreshToken)
    app.router.add_view('/auth/v1/users', UserListView)
    app.router.add_view('/auth/v1/users/{id}', UserDetailView)