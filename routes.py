from views import UserRegister, UserLogin, RefreshToken


def setup_routes(app):
    app.router.add_view('/auth/v1/register', UserRegister)
    app.router.add_view('/auth/v1/login', UserLogin)
    app.router.add_view('/auth/v1/refresh', RefreshToken)
