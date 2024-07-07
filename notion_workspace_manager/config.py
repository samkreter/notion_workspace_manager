import os

class Config:
    @staticmethod
    def validate():
        required_vars = [
            'LIFE_LESSONS_DATABASE_ID', 'JOURNAL_DATABASE_ID', 'NEW_BOOK_TEMPLATE_ID',
            'READING_DATABASE_ID', 'SOURCE_DATABASE_ID', 'NOTION_API_KEY', 'OPENAI_API_KEY'
        ]
        for var in required_vars:
            if not os.getenv(var):
                raise EnvironmentError(f'Missing required environment variable: {var}')

    @staticmethod
    def life_lessons_database_id():
        return os.getenv('LIFE_LESSONS_DATABASE_ID')

    @staticmethod
    def journal_database_id():
        return os.getenv('JOURNAL_DATABASE_ID')

    @staticmethod
    def new_book_template_id():
        return os.getenv('NEW_BOOK_TEMPLATE_ID')

    @staticmethod
    def reading_database_id():
        return os.getenv('READING_DATABASE_ID')

    @staticmethod
    def source_database_id():
        return os.getenv('SOURCE_DATABASE_ID')

    @staticmethod
    def notion_api_key():
        return os.getenv('NOTION_API_KEY')

    @staticmethod
    def openai_api_key():
        return os.getenv('OPENAI_API_KEY')