def config_route(app):
    @app.route('/')
    def home():
        return '<h1>Hello, World!</h1>'