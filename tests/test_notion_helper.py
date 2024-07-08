import pytest
from unittest.mock import MagicMock, patch
from notion_workspace_manager.notion_helper import NotionHelper

@pytest.fixture
def notion_client_mock():
    return MagicMock()

@pytest.fixture
def notion_helper(notion_client_mock):
    with patch('notion_workspace_manager.notion_helper.NotionClient', return_value=notion_client_mock):
        return NotionHelper(api_key='fake_api_key')

def test_create_page(notion_helper, notion_client_mock):
    parent = {"database_id": "test_db_id"}
    properties = {"Name": {"title": [{"text": {"content": "Test Page"}}]}}
    icon = {"emoji": "📄"}

    notion_helper.create_page(parent, properties, icon)

    notion_client_mock.pages.create.assert_called_once_with(
        parent=parent,
        properties=properties,
        icon=icon
    )

def test_update_page(notion_helper, notion_client_mock):
    page_id = "test_page_id"
    properties = {"Status": {"status": {"name": "Completed"}}}

    notion_helper.update_page(page_id, properties)

    notion_client_mock.pages.update.assert_called_once_with(
        page_id=page_id,
        properties=properties
    )

def test_query_database(notion_helper, notion_client_mock):
    database_id = "test_db_id"
    filter_params = {"property": "Status", "status": {"equals": "Incomplete"}}

    notion_helper.query_database(database_id, filter_params)

    notion_client_mock.databases.query.assert_called_once_with(
        database_id=database_id,
        filter=filter_params
    )

def test_retrieve_page(notion_helper, notion_client_mock):
    page_id = "test_page_id"

    notion_helper.retrieve_page(page_id)

    notion_client_mock.pages.retrieve.assert_called_once_with(page_id)