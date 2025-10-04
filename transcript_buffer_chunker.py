import vertexai
from vertexai.generative_models import GenerativeModel, Tool, GenerationConfig
from typing import List

from time import time

from config import (
    GEMINI_MODEL,
    PROJECT_ID,
    LOCATION,
    GEMINI_SYSTEM_PROMPT,
)

from pydantic import BaseModel

class ResponseSchema(BaseModel):
    chunks: List[List[str]]

class TranscriptBufferChunker:

    def __init__(self, topics_manager):


        # lines of transcript
        self.buffer = []
        self.topics_manager = topics_manager

        vertexai.init(project=PROJECT_ID, location=LOCATION)
        self.model = GenerativeModel(GEMINI_MODEL)
        print(f"Using model: {GEMINI_MODEL}")

        self.last_clean_time = time()

        self.clean_interval = 10 # seconds

    
    def add_transcript_line(self, line):
        self.buffer.append(line)

        if time() - self.last_clean_time >= self.clean_interval:
            print("Chunking buffer")
            chunks = self.chunk_buffer(self.topics_manager.list_topics())

            print("Final chunks output:")
            for i, chunk in enumerate(chunks):
                print(f"Chunk {i+1}: {chunk}")

            res = self.topics_manager.classify_chunk(chunks)
            print("res", res.topic_key, res.updated_description)
            if not res.topic_key:
                self.topics_manager.add_new_topic(res.updated_description)
            else:
                self.topics_manager.update_topic(res.topic_key, res.updated_description)

            print("topics_manager.list_topics()", self.topics_manager.list_topics())
            
            self.last_clean_time = time()
            self.clear_buffer()


    
    def clear_buffer(self):
        self.buffer = []
    

    def _clean_buffer(self):

        prompt = f"""
        You are a transcript cleaning assistant. 
        Your task is to clean and format the provided transcript by:
        - Removing filler words (um, uh, like, you know, etc.)
        - Fixing grammar and punctuation
        - Maintaining speaker labels
        - Keeping the original meaning intact
        - Making it more readable while staying faithful to the content
        
        IMPORTANT: Return ONLY a JSON array of strings, where each string is a cleaned line of the transcript.
        Do not include any other text, explanations, or formatting.
        Example format: ["Speaker1: Cleaned line 1", "Speaker2: Cleaned line 2", "Speaker1: Cleaned line 3"]
        """

        print("inside cleaning buffer")
        
        # Create the full prompt
        full_prompt = f"{prompt}\n\nHere is the transcript to clean:\n{"\n".join(self.buffer)}"
        
        # Use Vertex AI model directly
        response = self.model.generate_content(full_prompt)
        
        # Parse the response as JSON to get a list of lines
        try:
            import json
            response_text = response.candidates[0].content.parts[0].text.strip()
            # Try to extract JSON from the response
            if response_text.startswith('[') and response_text.endswith(']'):
                cleaned_lines = json.loads(response_text)
            else:
                # If not JSON, try to find JSON in the response
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                if start_idx != -1 and end_idx != 0:
                    json_text = response_text[start_idx:end_idx]
                    cleaned_lines = json.loads(json_text)
                else:
                    # Fallback: split by lines and clean each
                    cleaned_lines = [line.strip() for line in response_text.split('\n') if line.strip()]
            
            print("Cleaned lines:", cleaned_lines)
            self.buffer = cleaned_lines
            
        except Exception as e:
            print(f"Error parsing cleaned response: {e}")
            print("Raw response:", response.candidates[0].content.parts[0].text)
            # Fallback: use original buffer
            self.buffer = [line.strip() for line in self.buffer if line.strip()]

    def chunk_buffer(self, topics):

        # use the topics to chunk the buffer

        print("Cleaning buffer")
        self._clean_buffer()

        prompt = f"""
        You are given lines of text of a conversation transcript. 
        This transcript may correspond to a single conversation topic or several conversation topics.

        Your job is to group the lines of the transcript by the topics given to you.
        The topics you must group by are:
        {topics}

        If topics is empty, split based on your judgement of the separation of topics.

        The lines of text are:
        {"\n".join(self.buffer)}
        
        IMPORTANT: Return ONLY a JSON array of arrays, where each inner array contains lines that belong to the same topic.
        Do not include any other text, explanations, or formatting.
        Example format: [["Speaker1: Line about topic 1", "Speaker2: Another line about topic 1"], ["Speaker1: Line about topic 2", "Speaker2: Another line about topic 2"]]
        
        If a line of text does not belong to any of the topics, add it to a new group.
        """

        print("Chunking buffer")
        
        # Use Vertex AI model directly
        response = self.model.generate_content(prompt)
        
        # Parse the response as JSON to get a list of lists
        try:
            import json
            response_text = response.candidates[0].content.parts[0].text.strip()
            # Try to extract JSON from the response
            if response_text.startswith('[') and response_text.endswith(']'):
                chunks = json.loads(response_text)
            else:
                # If not JSON, try to find JSON in the response
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                if start_idx != -1 and end_idx != 0:
                    json_text = response_text[start_idx:end_idx]
                    chunks = json.loads(json_text)
                else:
                    # Fallback: create a single chunk with all lines
                    chunks = [self.buffer]
            
            print("Chunks:", chunks)
            return chunks
            
        except Exception as e:
            print(f"Error parsing chunked response: {e}")
            print("Raw response:", response.candidates[0].content.parts[0].text)
            # Fallback: create a single chunk with all lines
            return [self.buffer]

        



