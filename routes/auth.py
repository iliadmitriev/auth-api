from views.auth import RefreshToken, UserLogin, UserRegister
from views.users import UserDetailView, UserListView


def setup_routes(app):
    app.router.add_route("*", "/auth/v1/register", UserRegister, name="register")
    app.router.add_route("*", "/auth/v1/login", UserLogin, name="login")
    app.router.add_route("*", "/auth/v1/refresh", RefreshToken, name="refresh")
    app.router.add_route("*", "/auth/v1/users", UserListView, name="user_list")
    app.router.add_route("*", "/auth/v1/users/{id}", UserDetailView, name="user_detail")
