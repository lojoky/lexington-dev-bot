#!/usr/bin/env python3
"""
Lexington Development Updates Slack Bot

This script uses OpenAI's Agents API to gather recent Lexington, KY development
stories and posts them to a Slack channel.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from openai import OpenAI


class LexingtonDevBot:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
        self.slack_channel_id = os.getenv('SLACK_CHANNEL_ID')
        
        if not all([self.openai_api_key, self.slack_bot_token, self.slack_channel_id]):
            raise ValueError("Missing required environment variables. Please set OPENAI_API_KEY, SLACK_BOT_TOKEN, and SLACK_CHANNEL_ID.")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.openai_api_key)
    
    def get_date_range(self) -> str:
        """Get the date range for the past 14 days."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=14)
        return f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    
    def call_openai_agent(self) -> Optional[List[Dict]]:
        """Call OpenAI's Agents API to search for Lexington development news."""
        try:
            # Create a thread for the conversation
            thread = self.client.beta.threads.create()
            
            # Define the system message with instructions
            system_message = f"""You are a real estate research assistant specializing in Lexington, Kentucky development news.

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
            
            # Add the system message to the thread
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=system_message
            )
            
            # Create and run the assistant
            assistant = self.client.beta.assistants.create(
                name="Lexington Development Researcher",
                instructions=system_message,
                model="gpt-4o",
                tools=[{"type": "web_search"}]
            )
            
            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id
            )
            
            # Wait for the run to complete
            while True:
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                
                if run_status.status == 'completed':
                    break
                elif run_status.status in ['failed', 'cancelled', 'expired']:
                    print(f"Run failed with status: {run_status.status}")
                    return None
                
                # Wait a bit before checking again
                import time
                time.sleep(2)
            
            # Get the messages from the thread
            messages = self.client.beta.threads.messages.list(thread_id=thread.id)
            
            # Find the assistant's response
            for message in messages.data:
                if message.role == 'assistant':
                    content = message.content[0].text.value
                    
                    # Try to extract JSON from the response
                    try:
                        # Look for JSON in the response
                        start_idx = content.find('[')
                        end_idx = content.rfind(']') + 1
                        
                        if start_idx != -1 and end_idx != 0:
                            json_str = content[start_idx:end_idx]
                            results = json.loads(json_str)
                            
                            if isinstance(results, list):
                                return results
                        
                        # If no array found, try parsing the entire response as JSON
                        parsed_content = json.loads(content)
                        if isinstance(parsed_content, list):
                            return parsed_content
                        elif isinstance(parsed_content, dict):
                            # Look for a results array in the dict
                            for key, value in parsed_content.items():
                                if isinstance(value, list):
                                    return value
                        
                        return []
                        
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON response: {e}")
                        print(f"Raw response: {content}")
                        return []
            
            print("No assistant response found")
            return []
            
        except Exception as e:
            print(f"Error calling OpenAI Agents API: {e}")
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
        
        # Get development news from OpenAI Agents API
        print("Searching for Lexington development news using OpenAI Agents API...")
        results = self.call_openai_agent()
        
        if results is None:
            print("Failed to get results from OpenAI Agents API")
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