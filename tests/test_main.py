import pytest
from unittest.mock import MagicMock, patch


from notion_workspace_manager.config import Config
from notion_workspace_manager.notion_helper import NotionHelper
from notion_workspace_manager.openai_helper import OpenAIHelper
from notion_workspace_manager.inbox_item import InboxItem
import main

from .test_helpers import get_raw_item

@pytest.fixture
def notion_helper_mock():
    return MagicMock(spec=NotionHelper)

@pytest.fixture
def openai_helper_mock():
    return MagicMock(spec=OpenAIHelper)

@pytest.fixture
def inbox_item_mock():
    return MagicMock(spec=InboxItem)


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    monkeypatch.setenv('LIFE_LESSONS_DATABASE_ID', 'life_lessons_db')
    monkeypatch.setenv('JOURNAL_DATABASE_ID', 'journal_db')
    monkeypatch.setenv('NEW_BOOK_TEMPLATE_ID', 'book_template_id')
    monkeypatch.setenv('READING_DATABASE_ID', 'reading_db')
    monkeypatch.setenv('SOURCE_DATABASE_ID', 'source_db')
    monkeypatch.setenv('NOTION_API_KEY', 'notion_key')
    monkeypatch.setenv('OPENAI_API_KEY', 'openai_key')
    yield

def test_get_inbox_items(notion_helper_mock, openai_helper_mock):
    sample_response = {
        'results': [
            get_raw_item("Sample Task")
        ]
    }
    notion_helper_mock.query_database.return_value = sample_response
    
    with patch('main.OpenAIHelper', return_value=openai_helper_mock), \
         patch('main.InboxItem') as inbox_item_patch:
        items = main.get_inbox_items(notion_helper_mock)
    
    assert len(items) == 1
    inbox_item_patch.assert_called_once_with(
        sample_response['results'][0],
        notion_helper_mock,
        openai_helper_mock,
        'life_lessons_db',
        'journal_db',
        'book_template_id',
        'reading_db'
    )
