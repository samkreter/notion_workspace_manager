import pytest
from unittest.mock import MagicMock, patch
from typing import Dict

from notion_workspace_manager.notion_helper import NotionHelper
from notion_workspace_manager.openai_helper import OpenAIHelper
from notion_workspace_manager.inbox_item import InboxItem

from .helpers import get_raw_item


@pytest.fixture
def notion_mock():
    return MagicMock(spec=NotionHelper)

@pytest.fixture
def openai_mock():
    return MagicMock(spec=OpenAIHelper)


def get_mock_item(title: str, notion_mock: MagicMock, openai_mock: MagicMock):
    raw_item = get_raw_item(title)
    
    return InboxItem(
        raw_item, 
        notion_mock, 
        openai_mock, 
        "life_lessons_db",
        "journal_db",
        "book_template_id",
        "reading_db"
    )


def test_item_initialization(notion_mock, openai_mock):
    item = get_mock_item("q: Sample Quote", notion_mock, openai_mock)
    assert item.title == "Sample Quote"
    assert item.type == "quote"
    assert item.handler_method.__name__ == "handle_quote"

def test_handle_quote(notion_mock, openai_mock):
    item = get_mock_item("q: Sample Quote", notion_mock, openai_mock)
    item.handle_quote()
    notion_mock.create_page.assert_called_once_with(
        parent={"database_id": "life_lessons_db"},
        properties={
            "Name": {"title": [{"text": {"content": "Sample Quote"}}]},
            "Type": {"select": {"name": "Quote"}},
        },
        icon=None
    )
    notion_mock.update_page.assert_called_once_with(
        page_id="test_id",
        properties={"Status": {"status": {"name": "Done"}}}
    )

def test_handle_task(notion_mock, openai_mock):
    item = get_mock_item("t: Sample Task", notion_mock, openai_mock)
    item.handle_task()
    notion_mock.update_page.assert_called_once_with(
        page_id="test_id",
        properties={
            "Status": {"status": {"name": "In progress"}}
        }
    )

def test_handle_book(notion_mock, openai_mock):
    openai_mock.get_book_details.return_value = {
        "title": "Sample Book Title",
        "author": "Sample Author"
    }
    item = get_mock_item("b: Sample Book", notion_mock, openai_mock)
    item.handle_book()
    
    notion_mock.create_page.assert_called_once_with(
        parent={"database_id": "reading_db"},
        properties={
            "Name": {"title": [{"text": {"content": "Sample Book Title"}}]},
            "Author": {"multi_select": [{"name": "Sample Author"}]},
            "Status": {"select": {"name": "Not Read"}}
        },
        icon=notion_mock.retrieve_page.return_value["icon"]
    )
    notion_mock.update_page.assert_called_once_with(
        page_id="test_id",
        properties={"Status": {"status": {"name": "Done"}}}
    )

def test_handle_unregistered_type(notion_mock, openai_mock):
    item = get_mock_item("x: Unknown Type", notion_mock, openai_mock)
    item.handle_unregistered_type()
    notion_mock.create_page.assert_not_called()
    notion_mock.update_page.assert_not_called()