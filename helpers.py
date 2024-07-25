from typing import List
from SimplerLLM.language.llm import LLM,LLMProvider
from SimplerLLM.language.llm_addons import generate_pydantic_json_model
from SimplerLLM.tools.rapid_api import RapidAPIClient
from pydantic import BaseModel
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Constants
wordpress_url = os.getenv("WORDPRESS_URL", "")
wordpress_user = os.getenv("WORDPRESS_USER", "")
wordpress_pass = os.getenv("WORDPRESS_APP_PASSWORD", "")

class SubTopics(BaseModel):
    sub_topics: List[str]

llm_instance = LLM.create(provider=LLMProvider.OPENAI,model_name="gpt-4o")

sub_topics_prompt = """as an expert in keyword and topic research specialized in {topic}, 
    generate {count} sub topics to write about in the form of SEARCHABLE keywords
    for the the following parent topic: {topic}"""

draft_prompt = """
I will provide you with a [TOPIC], and your task is to generate a blog post draft for that [TOPIC].
maske the draft is SEO optimized, and covers all the aspects of the [TOPIC].
The draft should me a minimum of {word_count} words.
[TOPIC] = {topic}

Draft:

"""

def generate_draft(topic :str, word_count = 500):
    prompt = draft_prompt.format(topic=topic, word_count = word_count)
    response = llm_instance.generate_response(prompt=prompt,max_tokens=4096)
    return response

def get_topic_children(topic :str, num_results = 3):
    prompt = sub_topics_prompt.format(topic=topic,count = num_results)

    response  = generate_pydantic_json_model(model_class=SubTopics,
                                             prompt=prompt,llm_instance=llm_instance,
                                             max_tokens=1024)
    return response.sub_topics

def post_on_wordpress(topic, content):

    wp_endpoint = f"{wordpress_url}/wp-json/wp/v2/posts"

    # The content of your new blog post
    post = {
        "title": topic,
        "content": content,
        "status": "draft"  # Other statuses can be 'publish', 'pending', etc.
    }

    # Make the request to create the post
    response = requests.post(wp_endpoint, json=post, auth=HTTPBasicAuth(wordpress_user, wordpress_pass))

    if response.status_code == 201:
        print("Post created successfully")
    else:
        print(f"Failed to create post. Status code: {response.status_code}")
        print(response.json())

def get_keyword_metrics(keywords):
    rapid = RapidAPIClient()
    response = rapid.call_api(api_url=f"https://bulk-keyword-metrics.p.rapidapi.com/seo-tools/get-bulk-keyword-metrics?keywords_count=20&query={keywords}&countryCode=US")
    return response