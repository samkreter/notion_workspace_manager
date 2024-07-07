from typing import Dict

def get_raw_item(title: str) -> Dict:
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