from typing import Dict
import logging
from dataclasses import dataclass

from notion_workspace_manager.notion_helper import NotionHelper
from notion_workspace_manager.openai_helper import OpenAIHelper


@dataclass
class Config:
    life_lessons_database_id: str
    journal_database_id: str
    new_book_template_id: str
    reading_database_id: str


class InboxItem:
    TYPE_MAP = {
        "p": ("principle", "handle_principle"),
        "t": ("task", "handle_task"),
        "q": ("quote", "handle_quote"),
        "j": ("journal", "handle_journal"),
        "b": ("book", "handle_book")
    }

    def __init__(self, item: Dict, notion: NotionHelper, 
                 openai: OpenAIHelper, config: Config
    ):
        self.notion = notion
        self.openai = openai
        self.raw_item = item
        self.config = config

        self.title, self.type, self.handler_method = self._parse_item()

    def _parse_item(self):
        split_title = self._get_title().split(":")
        if len(split_title) != 2:
            return self._get_title(), "unregistered_type", self.handle_unregistered_type
        
        type_key, title = split_title[0].lower(), split_title[1].strip()
        type_info = self.TYPE_MAP.get(type_key, ("unregistered_type", "handle_unregistered_type"))
        return title, type_info[0], getattr(self, type_info[1])

    def _get_title(self) -> str:
        return self.raw_item["properties"]["Task name"]["title"][0]["plain_text"]

    @property
    def page_id(self) -> str:
        return self.raw_item["id"]

    def process_item(self):
        self.handler_method()

    def handle_quote(self):
        self._create_page(
            database_id=self.config.life_lessons_database_id,
            properties={
                "Name": {"title": [{"text": {"content": self.title}}]},
                "Type": {"select": {"name": "Quote"}}
            }
        )
        self.complete_item()

    def handle_principle(self):
        self._create_page(
            database_id=self.config.life_lessons_database_id,
            properties={
                "Name": {"title": [{"text": {"content": self.title}}]},
                "Type": {"select": {"name": "Principle"}}
            }
        )
        self.complete_item()

    def handle_task(self):
        self._update_page_status("In progress")

    def handle_journal(self):
        self._create_page(
            database_id=self.config.journal_database_id,
            properties={
                "Name": {"title": [{"text": {"content": self.title}}]},
                "Type": {"select": {"name": "Prompt"}}
            }
        )
        self.complete_item()

    def handle_book(self):
        book_details = self.openai.get_book_details(self.title)

        if "error" in book_details:
            logging.error(f"error while parsing title: {book_details['error']}")
            return

        template_page = self.notion.retrieve_page(self.config.new_book_template_id)
        
        book_title = book_details['title']
        author = book_details["author"].split(",")[0]
        
        logging.info(f"handling book: {book_title} by {author}")
        self._create_page(
            database_id=self.config.reading_database_id,
            properties={
                "Name": {"title": [{"text": {"content": book_title}}]},
                "Author": {"multi_select": [{"name": author}]},
                "Status": {"select": {"name": "Not Read"}}
            },
            icon=template_page["icon"]
        )
        self.complete_item()

    def handle_unregistered_type(self):
        logging.debug(f"Unregistered type for item: {self.title}")

    def _create_page(self, database_id: str, properties: dict, icon=None):
        self.notion.create_page(
            parent={"database_id": database_id},
            properties=properties,
            icon=icon
        )
        logging.info(f"Created page for item: {self.title}")

    def _update_page_status(self, status: str):
        self.notion.update_page(
            page_id=self.page_id,
            properties={
                "Status": {"status": {"name": status}}
            }
        )
        logging.info(f"Updated status for item: {self.title} to {status}")

    def complete_item(self):
        self._update_page_status("Done")