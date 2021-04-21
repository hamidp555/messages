import sys
import os

from app import create_app

env = os.environ.get('ENV_NAME')
application = create_app(env)
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))

if __name__ == "__main__":
    application.run()