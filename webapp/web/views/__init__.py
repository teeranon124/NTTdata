from .chat_view import chat_bp

def register_blueprint(app):
    app.register_blueprint(chat_bp)
