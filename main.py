from typing import Dict, List, Callable
import os
import json
import logging

from dotenv import load_dotenv
from notion_client import Client as NotionClient
from openai import OpenAI

load_dotenv()

class Item:
    title: str 
    raw_item: Dict
    type: str
    _process_func: Callable

    def __init__(self, item: Dict):
        self.life_lessons_database_id = os.environ["LIFE_LESSONS_DATABASE_ID"]
        self.reading_database_id = os.environ["READING_DATABASE_ID"]
        self.new_book_template_id = os.environ["NEW_BOOK_TEMPLATE_ID"]


        # Map the type shortcuts to the correct types and processor functions
        type_map = {
            "p": ("principle", self.handle_principle),
            "t": ("task", self.handle_task),
            "q": ("quote", self.handle_qoute),
            "j": ("journal", self.handle_journal),
            "b": ("book", self.handle_book)
        }

        self.raw_item = item

        # Handle not found type
        split_title = self._get_title().split(":")
        if len(split_title) != 2:
            self.type = "unregistered_type"
            self.title = self._get_title()
            self._process_func = self.handle_unregistered_type
            return

        self.title = split_title[1].strip()
        self.type, self._process_func =  type_map.get(
            split_title[0].lower(), 
            ("unregistered_type", self.handle_unregistered_type)
        )


    def _get_title(self) -> str:
        return self.raw_item["properties"]["Task name"]["title"][0]["plain_text"]
        
    @property
    def page_id(self) -> str:
        return self.raw_item["id"]
        
    def process_item(self, notion):
        self._process_func(notion)

    def handle_qoute(self, notion):
        print(f"Processing quote: {self.title}")

        notion.pages.create(
            parent={"database_id": self.life_lessons_database_id},
            properties={
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": self.title
                            }
                        }
                    ]
                },
                "Type": {
                    "select": {
                        "name": "Quote"
                    }
                }
            }
        )

        self.complete_item(notion)

        print(f"Completed quote: {self.title}")

    def handle_principle(self, notion):
        print(f"Processing principle: {self.title}")

        # Create principle page in the Life Lessons database
        notion.pages.create(
            parent={"database_id": self.life_lessons_database_id},
            properties={
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": self.title
                            }
                        }
                    ]
                },
                "Type": {
                    "select": {
                        "name": "Principle"
                    }
                }
            }
        )

        self.complete_item(notion)

    def handle_task(self, notion):
        # Update status to in progress to review the next day
        notion.pages.update(
            page_id=self.page_id,
            properties={
                "Task name": {
                    "title": [
                        {
                            "text": {
                                "content": self.title
                            }
                        }
                    ]
                },
                "Status": {
                    "status": {
                        "name": "In progress"
                    }
                }
            }
        )

    def handle_journal(self, notion) -> None:
        print(f"Processing journal: {self.title}")
        journal_db_id = os.environ["JOURNAL_DATABASE_ID"]

        # Create journal page in the Journal database
        notion.pages.create(
            parent={"database_id": journal_db_id},
            properties={
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": self.title
                            }
                        }
                    ]
                },
                "Type": {
                    "select": {
                        "name": "Prompt"
                    }
                }
            }
        )

        self.complete_item(notion)


    def handle_book(self, notion) -> None:
        print("INFO: Processing book")
        openai_client = OpenAI(api_key=os.environ["OPEN_AI_API_KEY"])
        
        # Get book details using the openai API
        res = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={ "type": "json_object" },
            messages=[
            {"role": "system", "content": "You are a helpful assistant that provides book details in JSON format."},
            {"role": "user", "content": f"Can you give me the full title and author \
                of this book in JSON format with keys title and author? If it doesn't\
                seem a title exists, can you respond with a json key error? The book \
                title is close to: {self.title}"}
            ]
        )

        book_details = json.loads(res.choices[0].message.content)

        # TODO: Show errors in notion
        if "error" in book_details:
            print("ERROR: no title found")
            return

        print(f"INFO: Process book {book_details['title']} by {book_details['author']}")

        template_page = notion.pages.retrieve(self.new_book_template_id)

        new_book_page = {
            "parent": {"database_id": self.reading_database_id},
            "icon": template_page["icon"],
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": book_details["title"]
                            }
                        }
                    ]
                },
                "Author": {
                    "multi_select": [
                        {"name": book_details["author"]}
                    ]
                },
                "Status": {
                    "select": {
                        "name": "Not Read",
                    }
                }
            },
        }
        notion_client.pages.create(**new_book_page)
        
        
        self.complete_item(notion)
        print("INFO: Completed book processing")
        
    
    def complete_item(self, notion) -> None:
        notion.pages.update(
            page_id=self.page_id,
            properties={
                "Status": {
                    "status": {
                        "name": "Done"
                    }
                }
            }
        )

    def handle_unregistered_type(self, notion):
        pass


def get_inbox_items(notion) -> List[Item]:
    task_db_id = os.environ["SOURCE_DATABASE_ID"]
    filter_params = {
        "property": "Status",
        "status": {
            "equals": "Inbox"
        }
    }
    res = notion.databases.query(
        **{
            "database_id": task_db_id,
            "filter": filter_params
        }
    )
    return [Item(item) for item in res.get('results', [])]


# Books
# Bucket list item
# Journal Items

if __name__ == "__main__":
    notion_client = NotionClient(auth=os.getenv("NOTION_API_KEY"))
    inbox_items = get_inbox_items(notion_client)
    for item in inbox_items:
        item.process_item(notion_client)