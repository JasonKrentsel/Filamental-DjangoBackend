import os
import subprocess

# Define the base directory
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'db.sqlite3')

# Define the media directory
media_dir = os.path.join(base_dir, 'media')

# Function to find all apps with a migrations folder


def find_migrations_dirs(base_dir):
    migrations_dirs = []
    for root, dirs, files in os.walk(base_dir):
        if 'migrations' in dirs:
            migrations_dirs.append(os.path.join(root, 'migrations'))
    return migrations_dirs


# Get all migrations directories
migrations_dirs = find_migrations_dirs(base_dir)

# Delete the database file
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Deleted {db_path}")

# Delete all migration files except __init__.py
for migrations_dir in migrations_dirs:
    if os.path.exists(migrations_dir):
        for filename in os.listdir(migrations_dir):
            file_path = os.path.join(migrations_dir, filename)
            if filename != '__init__.py' and os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted {file_path}")

# Delete the media directory
if os.path.exists(media_dir):
    for root, dirs, files in os.walk(media_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(media_dir)
    print(f"Deleted {media_dir}")

# Run makemigrations
subprocess.run(['python', 'manage.py', 'makemigrations'])

# Run migrate
subprocess.run(['python', 'manage.py', 'migrate'])
