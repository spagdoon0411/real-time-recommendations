

from typing import Optional
import json
from vertexai.generative_models import GenerativeModel
import vertexai

from config import GEMINI_MODEL, PROJECT_ID, LOCATION


class TopicClassification:
    def __init__(self, topic_key: Optional[str] = None, updated_description: Optional[str] = None):
        self.topic_key = topic_key
        self.updated_description = updated_description


class TopicManager:
    def __init__(self):
        self.topics = {}

        vertexai.init(project=PROJECT_ID, location=LOCATION)
        self.model = GenerativeModel(GEMINI_MODEL)

    def add_new_topic(self, summary):

        # generate a new topic key 
        prompt = f"""Generate a new unique topic identifier for the following summary: {summary}

Return only a JSON response with this exact format:
{{"topic_key": "your_generated_topic_key_here"}}"""
        
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Parse JSON response
        try:
            # Extract JSON from response if it's wrapped in markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            parsed_response = json.loads(json_text)
            topic_key = parsed_response.get("topic_key")
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing topic_key response: {e}")
            print(f"Response text: {response_text}")
            # Fallback to using the raw response as topic_key
            topic_key = response_text.strip()

        print(f"\n generated topic_key: {topic_key}\n")

        self.topics[topic_key] = {"summary": summary, "content_stack": []}

        print(f"\n self.topics: {self.topics}\n")

    def list_topics(self):
        return {key: topic["summary"] for key, topic in self.topics.items()}

    def list_topics_string(self):
        if not self.topics:
            return "No topics available"

        topics_list = []
        for key, topic in self.topics.items():
            topics_list.append(f"{key}: {topic['summary']}")
        return "\n".join(topics_list)

    def update_topic(self, topic_key, summary):
        self.topics[topic_key]["summary"] = summary

    def extend_topic(self, topic_key, content):
        if topic_key not in self.topics:
            raise ValueError(f"Topic key '{topic_key}' does not exist")
        self.topics[topic_key]["content_stack"].append(content)

    def get_topic_content(self, topic_key):
        if topic_key not in self.topics:
            raise ValueError(f"Topic key '{topic_key}' does not exist")
        return self.topics[topic_key]["content_stack"]

    def get_topic_summary(self, topic_key):
        if topic_key not in self.topics:
            raise ValueError(f"Topic key '{topic_key}' does not exist")
        return self.topics[topic_key]["summary"]

    def classify_chunk(self, chunk: str) -> TopicClassification:
        try:
            topics_context = self.list_topics_string()

            prompt = f"""Given the following existing topics:
{topics_context}

Analyze this chunk of conversation and determine which topic it belongs to:
"{chunk}"

Return a JSON response with the following structure:
{{
    "topic_key": "the_key_if_matches_existing_topic_or_null_if_new_topic",
    "updated_description": "description_of_topic_based_on_chunk"
}}

If the chunk matches an existing topic, return the existing topic_key and an updated_description.
If the chunk doesn't fit any existing topic, return null for topic_key and generate a description for the new topic given the chunk.

Do not try to merge topics into one topic_key. 
"""

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Try to parse JSON response
            try:
                # Extract JSON from response if it's wrapped in markdown code blocks
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_text = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    json_text = response_text[json_start:json_end].strip()
                else:
                    json_text = response_text
                
                parsed_response = json.loads(json_text)
                topic_key = parsed_response.get("topic_key")
                updated_description = parsed_response.get("updated_description")
                
                return TopicClassification(topic_key=topic_key, updated_description=updated_description)
                
            except json.JSONDecodeError as json_error:
                print(f"JSON parsing error: {json_error}")
                print(f"Response text: {response_text}")
                return TopicClassification(topic_key=None, updated_description=None)

        except Exception as e:
            print(f"Error classifying chunk: {e}")
            return TopicClassification(topic_key=None, updated_description=None)
