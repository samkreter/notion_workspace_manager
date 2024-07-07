import pytest
from unittest.mock import MagicMock, patch
from typing import Dict

from notion_workspace_manager.notion_helper import NotionHelper
from notion_workspace_manager.openai_helper import OpenAIHelper
from notion_workspace_manager.inbox_item import InboxItem, Config

def get_test_item(title: str) -> Dict:
    return {
        "id": "test_id",
            "object": "page",
        "created_time": "2024-07-02T22:20:00.000Z",
        "last_edited_time": "2024-07-02T22:20:00.000Z",
        "created_by": {
            "object": "user",
            "id": "test-user-id"
        },
        "last_edited_by": {
            "object": "user",
            "id": "test-user-id"
        },
        "icon": {
            "type": "external",
            "external": {
                "url": "https://www.notion.so/icons/clipping_lightgray.svg"
            }
        },
        "parent": {
            "type": "database_id",
            "database_id": "source-database-id"
        },
        "properties": {
            "Task name": {
                "id": "title",
                "type": "title",
                "title": [
                    {
                        "plain_text": title,

                    }
                ]
            },
            "Status": {
                "type": "status",
                "status": {
                    "id": "Nmav",
                    "name": "Inbox",
                    "color": "blue"
                },
            },
            "Status": {
                "status": {
                    "name": "Inbox"
                }
            }
        }
    }

@pytest.fixture
def notion_mock():
    return MagicMock(spec=NotionHelper)

@pytest.fixture
def openai_mock():
    return MagicMock(spec=OpenAIHelper)

@pytest.fixture 
def config():
    return Config(
        life_lessons_database_id="life_lessons_db",
        journal_database_id="journal_db",
        new_book_template_id="book_template_id",
        reading_database_id="reading_db"
    )


def test_item_initialization(notion_mock, openai_mock, config):
    raw_item = get_test_item("q: Sample Quote")
    item = InboxItem(raw_item, notion_mock, openai_mock, config)
    assert item.title == "Sample Quote"
    assert item.type == "quote"
    assert item.handler_method.__name__ == "handle_quote"

def test_handle_quote(notion_mock, openai_mock, config):
    sample_quote_item = get_test_item("q: Sample Quote")
    item = InboxItem(sample_quote_item, notion_mock, openai_mock, config)
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

def test_handle_task(notion_mock, openai_mock, config):
    sample_task_item = get_test_item("t: Sample Task")
    item = InboxItem(sample_task_item, notion_mock, openai_mock, config)
    item.handle_task()
    notion_mock.update_page.assert_called_once_with(
        page_id="test_id",
        properties={
            "Status": {"status": {"name": "In progress"}}
        }
    )

def test_handle_book(notion_mock, openai_mock, config):
    sample_book_item = get_test_item("b: Sample Book")
    openai_mock.get_book_details.return_value = {
        "title": "Sample Book Title",
        "author": "Sample Author"
    }
    item = InboxItem(sample_book_item, notion_mock, openai_mock, config)
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

def test_handle_unregistered_type(notion_mock, openai_mock, config):
    sample_unknown_item = get_test_item("x: Unknown Type")
    item = InboxItem(sample_unknown_item, notion_mock, openai_mock, config)
    item.handle_unregistered_type()
    notion_mock.create_page.assert_not_called()
    notion_mock.update_page.assert_not_called()