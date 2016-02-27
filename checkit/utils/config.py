"""Load environment configs"""
import os

def get_github_confs():
    """Returns GitHub client_id and client_secret"""
    creds = {
        'GITHUB_CLIENT_ID': os.environ.get('GITHUB_CLIENT', None),
        'GITHUB_CLIENT_SECRET': os.environ.get('GITHUB_SECRET', None)
    }
    return creds


def get_db_url():
    """Returns DB URI"""
    return os.environ.get('DB_URI', None)


def get_app_secret():
    """Return app secret key"""
    return os.environ.get('APP_SECRET', None)
