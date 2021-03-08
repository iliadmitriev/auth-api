from views import UserRegister


def setup_routes(app):
    app.router.add_view('/auth/v1/register', UserRegister)
