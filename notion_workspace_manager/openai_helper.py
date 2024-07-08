from openai import OpenAI
import json

class OpenAIHelper:
    def __init__(self, api_key: str):
        self._openai_client = OpenAI(api_key=api_key)

    def get_book_details(self, book_title: str) -> dict:
        res = self._openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={ "type": "json_object" },
            messages=[
            {"role": "system", "content": "You are a helpful assistant that provides book details in JSON format."},
            {"role": "user", "content": f"Can you give me the full title and author \
                of this book in JSON format with keys title and author? If it doesn't\
                seem a title exists, can you respond with a json key error? The book \
                title is close to: {book_title}"}
            ]
        )
        
        return json.loads(res.choices[0].message.content)
    


            