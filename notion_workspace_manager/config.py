import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    life_lessons_database_id = os.getenv("LIFE_LESSONS_DATABASE_ID")
    reading_database_id = os.getenv("READING_DATABASE_ID")
    new_book_template_id = os.getenv("NEW_BOOK_TEMPLATE_ID")
    journal_database_id = os.getenv("JOURNAL_DATABASE_ID")
    source_database_id = os.getenv("SOURCE_DATABASE_ID")
    notion_api_key = os.getenv("NOTION_API_KEY")
    openai_api_key = os.getenv("OPEN_AI_API_KEY")

    @staticmethod
    def validate():
        missing_vars = [var for var in dir(Config) if not var.startswith("__") and getattr(Config, var) is None]
        if missing_vars:
            raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")