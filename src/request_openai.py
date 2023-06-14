import json
import os

from dotenv import load_dotenv; load_dotenv()
import openai; openai.api_key = os.getenv('OPENAI_API_KEY')
import requests

def get_tag_info(tag: str):
    try:
        res = requests.get(f'https://qiita.com/api/v2/tags/{tag}')
        return res.json()
    except ValueError as e:
        print(e)
        
def make_completion(messages: list, functions: list):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions
    )
    
    if completion.choices[0].finish_reason == 'function_call':
        params = json.loads(completion.choices[0].message.function_call.arguments)
        tag = params['tag']
        function_name = completion.choices[0].message.function_call.name
        function = globals()[function_name]
        res = function(tag)
        add_dict = {"role": "function", "name": "get_tag_info", "content": json.dumps(res)}
        messages.append(add_dict)
        
        return make_completion(messages, functions)
        
    else:
        return completion.choices[0].message.content
    
    
if __name__ == '__main__':
    
    messages=[
        {"role": "system", "content": "You are a Qiita website engineer."},
        {"role": "user", "content": "javascriptタグのフォロワー数を教えてください。"},
        ]
    functions=[
        {
            "name": "get_tag_info",
            "description": "Get the qiita info in a given tag",
            "parameters": {
                "type": "object",
                "properties": {
                    "tag": {
                        "type": "string",
                        "description": "Tech word, e.g. Python, JavaScript, React"
                        },
                    "unit": {
                        "type": "string",
                        "enum": ["followers_count", "items_count"]
                        }
                    },
                "required": ["tag"]
                }
            }
        ]
    
    reply_text = make_completion(messages, functions)
    print(reply_text)