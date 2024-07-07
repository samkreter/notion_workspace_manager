from notion_client import Client as NotionClient

class NotionHelper:
    def __init__(self, api_key: str):
        self.client = NotionClient(auth=api_key)

    def create_page(self, parent, properties, icon=None):
        page_data = {
            "parent": parent,
            "properties": properties
        }
        if icon:
            page_data["icon"] = icon

        return self.client.pages.create(**page_data)

    def update_page(self, page_id: str, properties: dict):
        return self.client.pages.update(page_id=page_id, properties=properties)

    def query_database(self, database_id: str, filter_params: dict):
        return self.client.databases.query(database_id=database_id, filter=filter_params)

    def retrieve_page(self, page_id: str):
        return self.client.pages.retrieve(page_id)