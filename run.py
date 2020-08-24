import os

from app import create_app

config_name = os.getenv('FLASK_CONFIG')
if config_name is None:
        config_name = 'production'
app = create_app(config_name)

if __name__ == '__main__':
    app.run()
