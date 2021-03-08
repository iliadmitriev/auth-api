from views import UserRegister, UserLogin


def setup_routes(app):
    app.router.add_view('/auth/v1/register', UserRegister)
    app.router.add_view('/auth/v1/login', UserLogin)
