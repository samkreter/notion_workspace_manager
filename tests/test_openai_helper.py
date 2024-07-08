import json

import pytest
from unittest.mock import MagicMock, patch
from notion_workspace_manager.openai_helper import OpenAIHelper

@pytest.fixture
def openai_client_mock():
    return MagicMock()

@pytest.fixture
def openai_helper(openai_client_mock):
    with patch('notion_workspace_manager.openai_helper.OpenAI', return_value=openai_client_mock):
        return OpenAIHelper(api_key='fake_api_key')

def test_get_book_details(openai_helper, openai_client_mock):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps({
        "title": "Sample Book Title",
        "author": "Sample Author"
    })
    openai_client_mock.chat.completions.create.return_value = mock_response
    
    book_title = "Sample Book"
    book_details = openai_helper.get_book_details(book_title)
    
    openai_client_mock.chat.completions.create.assert_called_once()
    
    assert book_details == {
        "title": "Sample Book Title",
        "author": "Sample Author"
    }

def test_get_book_details_error(openai_helper, openai_client_mock):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps({
        "error": "Title not found"
    })
    openai_client_mock.chat.completions.create.return_value = mock_response
    
    book_title = "Unknown Book"
    book_details = openai_helper.get_book_details(book_title)
    
    openai_client_mock.chat.completions.create.assert_called_once()
    
    assert book_details == {
        "error": "Title not found"
    }
