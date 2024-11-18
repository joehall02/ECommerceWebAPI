from main import create_app
from config import Development, Test

if __name__ == '__main__':
    app = create_app(Development)
    app.run(host="0.0.0.0", port=5050)