from config import settings
from app import create_app

app = create_app(settings)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=settings['PORT'], debug=settings['DEBUG'],
            workers=settings['WORKER'], auto_reload=True)

