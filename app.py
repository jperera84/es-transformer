from flask import Flask
from routes import home_route

app = Flask(__name__)
app.register_blueprint(home_route)

if __name__ == "__main__":
    app.run(debug=True)  # debug=True for development (auto-reloads)
