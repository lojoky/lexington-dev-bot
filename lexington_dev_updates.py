#!/usr/bin/env python3
"""
Lexington Development Updates Slack Bot

This script uses OpenAI's Chat Completions API with web search to gather recent
Lexington, KY development stories and posts them to a Slack channel.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class LexingtonDevBot:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
        self.slack_channel_id = os.getenv('SLACK_CHANNEL_ID')
        
        if not all([self.openai_api_key, self.slack_bot_token, self.slack_channel_id]):
            raise ValueError("Missing required environment variables. Please set OPENAI_API_KEY, SLACK_BOT_TOKEN, and SLACK_CHANNEL_ID.")
    
    def get_date_range(self) -> str:
        """Get the date range for the past 14 days."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=14)
        return f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    
    def call_openai_chat_api(self) -> Optional[List[Dict]]:
        """Call OpenAI's Chat Completions API to search for Lexington development news."""
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""You are a real estate research assistant specializing in Lexington, Kentucky development news.

Your task is to search for NEW development projects or related news in Lexington, Kentucky from the past 14 days ({self.get_date_range()}).

Focus on:
- Real estate development projects
- Infrastructure improvements
- Zoning approvals and changes
- Major site plans and proposals
- Funding announcements
- RFPs (Request for Proposals)
- Economic development initiatives
- Commercial and residential projects

Search multiple sources including:
- Local news websites (Lexington Herald-Leader, WKYT, WLEX, etc.)
- City government websites
- Real estate industry publications
- Business journals

After gathering information, return ONLY a JSON array with the most significant findings. Each item should contain:
- title (string): Clear, descriptive title
- summary (string): 1-2 sentence summary of the development
- url (string): Direct link to the source article

Limit to 5-8 items. If no significant updates are found, return an empty array.

Format your final response as valid JSON only, no additional text."""
        
        data = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "tools": [
                {
                    "type": "web_search"
                }
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract the content from the response
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                # Parse the JSON content
                parsed_content = json.loads(content)
                
                # Look for the results array in the parsed content
                if isinstance(parsed_content, dict):
                    # Try to find the array in the response
                    for key, value in parsed_content.items():
                        if isinstance(value, list):
                            return value
                    # If no array found, return empty
                    return []
                elif isinstance(parsed_content, list):
                    return parsed_content
                else:
                    return []
            else:
                print("No choices found in OpenAI response")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Error calling OpenAI Chat API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def format_slack_message(self, results: List[Dict]) -> str:
        """Format the results into a Slack message."""
        if not results:
            return ":no_entry_sign: No significant new development updates in Lexington in the past 14 days."
        
        message = ":construction: *Lexington Development Updates*\n\n"
        
        for item in results:
            title = item.get('title', 'No title')
            summary = item.get('summary', 'No summary')
            url = item.get('url', '#')
            
            message += f"• *{title}* — {summary}  <{url}|Read more>\n"
        
        return message
    
    def post_to_slack(self, message: str) -> bool:
        """Post the message to Slack."""
        url = "https://slack.com/api/chat.postMessage"
        
        headers = {
            "Authorization": f"Bearer {self.slack_bot_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "channel": self.slack_channel_id,
            "text": message,
            "unfurl_links": False
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('ok'):
                print("Message posted to Slack successfully!")
                return True
            else:
                print(f"Error posting to Slack: {result.get('error', 'Unknown error')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Error posting to Slack: {e}")
            return False
    
    def run(self):
        """Main execution method."""
        print("Starting Lexington Development Updates Bot...")
        print(f"Date range: {self.get_date_range()}")
        
        # Get development news from OpenAI Chat API
        print("Searching for Lexington development news using OpenAI Chat API...")
        results = self.call_openai_chat_api()
        
        if results is None:
            print("Failed to get results from OpenAI Chat API")
            return False
        
        # Format the message
        message = self.format_slack_message(results)
        print(f"Found {len(results) if results else 0} development updates")
        
        # Post to Slack
        print("Posting to Slack...")
        success = self.post_to_slack(message)
        
        if success:
            print("Bot execution completed successfully!")
        else:
            print("Bot execution failed!")
        
        return success


def main():
    """Main entry point."""
    try:
        bot = LexingtonDevBot()
        bot.run()
    except Exception as e:
        print(f"Error initializing bot: {e}")
        return False


if __name__ == "__main__":
    main() 