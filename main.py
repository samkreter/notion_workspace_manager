from typing import List
import logging

from notion_workspace_manager import InboxItem
from notion_workspace_manager.config import Config
from notion_workspace_manager.notion_helper import NotionHelper
from notion_workspace_manager.openai_helper import OpenAIHelper


def get_inbox_items(notion_helper: NotionHelper) -> List[InboxItem]:
    filter_params = {"property": "Status", "status": {"equals": "Inbox"}}
    res = notion_helper.query_database(database_id=Config.source_database_id, filter_params=filter_params)
    
    openai_helper = OpenAIHelper(api_key=Config.openai_api_key)
    
    return [InboxItem(
            item, 
            notion_helper,
            openai_helper,
            Config.life_lessons_database_id,
            Config.journal_database_id,
            Config.new_book_template_id,
            Config.reading_database_id
        ) for item in res.get('results', [])
    ]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    Config.validate()
    
    
    notion_helper = NotionHelper(Config.notion_api_key)
    inbox_items = get_inbox_items(notion_helper)
    for item in inbox_items:
        item.process_item()