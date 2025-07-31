import openai
import os
from dotenv import load_dotenv

# openai.api_key = os.getenv("OPENAI_API_KEY")
# Get the API key from .evn file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def summarize_text(text, rules, style_guidelines):
    prompt = f"""
        You are a professional technical specialist and technical assistant helping a developer study a new technologies.
        
        Follow these summarization rules strictly:
        <rules>
        {rules}
        </rules>

        Summarize the content in a clear, structured Markdown format.
        Use the following style guidelines:
        <style_guidelines>
        {style_guidelines}
        </style_guidelines>

        Now summarize the following content Markdown format:

        <content>
        {text}
        </content>
        """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
                    You are a professional technical specialist and professional technical writer.
                    Produce clear, exam-focused summaries in Markdown.
                    Follow the provided rules and style guidelines strictly.
                    """
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4
    )

    return response.choices[0].message.content