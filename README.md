# Lexington Development Updates Slack Bot

A Python script that automatically gathers recent Lexington, KY development news using OpenAI's **Agents API** and posts updates to a Slack channel.

## Features

- 🤖 Uses OpenAI's **Agents API** with web search for intelligent news gathering
- 📅 Runs automatically twice a week (Monday & Thursday at 9:00am ET)
- 📱 Posts formatted updates to a specified Slack channel
- 🚫 Posts "No new updates" message when no significant news is found
- ⚙️ Configurable via GitHub Secrets
- 🔍 Advanced reasoning and multi-source search capabilities

## Why Agents API?

The OpenAI Agents API provides several advantages over the Responses API:

- **Better Reasoning**: More sophisticated planning and decision-making capabilities
- **Built-in Tools**: Native web search integration with better context understanding
- **Conversational Memory**: Maintains context across multiple search iterations
- **Robust Error Handling**: Better handling of complex queries and edge cases
- **Multi-source Analysis**: Can search and synthesize information from multiple sources

## Setup

### 1. GitHub Repository Setup

1. Create a new GitHub repository
2. Push this code to the repository
3. Go to Settings → Secrets and variables → Actions
4. Add the following repository secrets:

#### Required Secrets

- `OPENAI_API_KEY`: Your OpenAI API key
- `SLACK_BOT_TOKEN`: Your Slack bot token (xoxb-...)
- `SLACK_CHANNEL_ID`: The Slack channel ID where updates will be posted

### 2. Slack Bot Setup

1. Create a new Slack app at https://api.slack.com/apps
2. Add the following OAuth scopes:
   - `chat:write` - To post messages to channels
   - `chat:write.public` - To post to public channels
3. Install the app to your workspace
4. Copy the Bot User OAuth Token (starts with `xoxb-`)
5. Add the bot to your target channel

### 3. OpenAI API Setup

1. Get an OpenAI API key from https://platform.openai.com/api-keys
2. Ensure you have access to the Agents API (beta feature)

## How It Works

1. **Scheduling**: The GitHub Action runs twice a week (Monday & Thursday at 9:00am ET)
2. **Agent Creation**: Creates an intelligent assistant with web search capabilities
3. **Multi-source Search**: Searches multiple sources for Lexington development news from the past 14 days
4. **Intelligent Analysis**: Uses advanced reasoning to identify and summarize the most relevant updates
5. **Processing**: Formats the results into a readable Slack message
6. **Posting**: Sends the message to the specified Slack channel

## Message Format

### When Updates Are Found:
```
:construction: *Lexington Development Updates*

• *Project Title* — Brief summary of the development  <URL|Read more>
• *Another Project* — Another summary  <URL|Read more>
...
```

### When No Updates Are Found:
```
:no_entry_sign: No significant new development updates in Lexington in the past 14 days.
```

## Manual Execution

You can manually trigger the workflow:
1. Go to the Actions tab in your GitHub repository
2. Select "Lexington Development Updates"
3. Click "Run workflow"

## Local Development

To test locally:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export SLACK_BOT_TOKEN="your-slack-bot-token"
   export SLACK_CHANNEL_ID="your-channel-id"
   ```

3. Run the script:
   ```bash
   python lexington_dev_updates.py
   ```

## Configuration

### Schedule
The bot runs twice a week by default. To modify the schedule, edit the cron expression in `.github/workflows/lexington_dev_updates.yml`:

```yaml
- cron: "0 13 * * 1,4"  # Monday and Thursday at 13:00 UTC
```

### Search Parameters
The script searches for news from the past 14 days. To modify this, edit the `get_date_range()` method in `lexington_dev_updates.py`.

### Agent Configuration
The agent is configured to search for:
- Real estate development projects
- Infrastructure improvements
- Zoning approvals and changes
- Major site plans and proposals
- Funding announcements
- RFPs (Request for Proposals)
- Economic development initiatives
- Commercial and residential projects

## Troubleshooting

### Common Issues

1. **"Missing required environment variables"**
   - Ensure all GitHub Secrets are properly set
   - Check that secret names match exactly

2. **"Error calling OpenAI Agents API"**
   - Verify your OpenAI API key is valid
   - Check that you have access to the Agents API (beta feature)
   - Ensure you have sufficient API credits

3. **"Error posting to Slack"**
   - Verify your Slack bot token is correct
   - Ensure the bot has been added to the target channel
   - Check that the channel ID is correct

4. **"Run failed with status"**
   - This usually indicates an issue with the Agents API
   - Check your API key permissions and credits
   - Review the GitHub Actions logs for detailed error messages

### Logs
Check the GitHub Actions logs for detailed error messages and debugging information.

## Dependencies

- `openai>=1.0.0` - OpenAI Python client for Agents API
- `requests>=2.31.0` - HTTP library for Slack API calls

## License

This project is open source and available under the MIT License. 