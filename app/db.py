from sqlmodel import create_engine, Session, SQLModel

sqlite_file_name = "main_database_test.db"
sqlite_url =f"sqlite:///app/databases/{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def init_database():
    SQLModel.metadata.create_all(engine)