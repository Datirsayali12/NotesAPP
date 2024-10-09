import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import BASE


db_user = 'postgres'
db_password = 'root'
db_host = 'db'
# db_host='localhost'
db_port = 5432
db_name = 'to-do-app'

uri = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(uri)

# Retrieve database connection details from environment variables
# db_user: str = os.getenv('DB_USER', 'postgres')  # Default to 'postgres'
# db_password: str = os.getenv('DB_PASSWORD', 'password')  # Default to 'password'
# db_host: str = os.getenv('DB_HOST', 'db')  # Default to 'db' (the name of the PostgreSQL service in docker-compose)
# db_port: str = os.getenv('DB_PORT', '5432')  # Default to '5432'
# db_name: str = os.getenv('DB_NAME', 'to-do-app')  # Default to 'to-do-app'
#
# # Create the database URI
# uri = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(uri)

BASE.metadata.create_all(engine) #it contain blueprint schema of tables ,keep track of all tables

SessionLocal = sessionmaker(bind=engine, autoflush=True)

# Dependency to get a database session
def get_db():
    db = SessionLocal()  # Get a new session from the sessionmaker
    try:
        yield db  # Return the session to use in the route
    finally:
        db.close()

try:
    connection=engine.connect()
    connection.close()
    print('ping,connected')
except Exception as e:
    print(str(e))





