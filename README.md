#  RUGGUARD Bot

An X (Twitter) bot that analyzes account trustworthiness for the Solana ecosystem. When triggered with "riddle me this" in a reply, the bot analyzes the original tweet's author and provides a comprehensive trustworthiness report.

## Features

- **Trigger-based Analysis**: Responds to "riddle me this" mentions
- **Comprehensive Account Analysis**: 
  - Account age and metrics
  - Follower/following ratios
  - Bio analysis with crypto keywords
  - Engagement pattern analysis
  - Trusted follower verification
- **Trustworthiness Scoring**: 0-100 scale with risk factors and positive indicators
- **Database Storage**: SQLite database for caching and avoiding duplicates
- **Rate Limit Handling**: Built-in rate limit management
- **Replit Deployable**: Designed for easy deployment on Replit

## Prerequisites

1. **X Developer Account**: Sign up at https://developer.x.com
2. **API Keys**: Get your API keys from the X Developer Portal
3. **Python 3.8+**: Required for running the bot

##  Installation

### Local Setup

1. **Clone and Setup**:
\`\`\`bash
git clone <repository-url>
cd rugguard-bot
pip install -r requirements.txt
\`\`\`

2. **Environment Configuration**:
\`\`\`bash
cp .env.example .env
# Edit .env with your X API credentials
\`\`\`

3. **Database Setup**:
\`\`\`bash
python scripts/setup_database.py
\`\`\`

4. **Run the Bot**:
\`\`\`bash
python main.py
\`\`\`

### Replit Deployment

1. **Import to Replit**:
   - Create new Repl
   - Import from GitHub or upload files
   - Set language to Python

2. **Configure Secrets**:
   - Go to Secrets tab in Replit
   - Add all environment variables from .env.example

3. **Install Dependencies**:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. **Run Setup**:
\`\`\`bash
python scripts/setup_database.py
\`\`\`

5. **Start Bot**:
\`\`\`bash
python main.py
\`\`\`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `X_API_KEY` | X API Key | ✅ |
| `X_API_SECRET` | X API Secret | ✅ |
| `X_ACCESS_TOKEN` | X Access Token | ✅ |
| `X_ACCESS_TOKEN_SECRET` | X Access Token Secret | ✅ |
| `X_BEARER_TOKEN` | X Bearer Token | ✅ |
| `MONITOR_ACCOUNT` | Specific account to monitor | ❌ |

### Trusted Accounts

The bot uses a trusted accounts list from:
`https://github.com/devsyrem/turst-list/main/list`

Accounts followed by 2+ trusted accounts receive higher trust scores.

## 📊 Monitoring & Status

### Check if Bot is Running

**Method 1: Status Checker Script**
\`\`\`bash
python status_checker.py
\`\`\`

**Method 2: Check Process**
\`\`\`bash
# Linux/Mac
ps aux | grep "python main.py"

# Windows
tasklist | findstr python
\`\`\`

**Method 3: Check Log File**
\`\`\`bash
tail -f rugguard_bot.log
\`\`\`

### Health Check Server

Run a simple web server to monitor bot status:

\`\`\`bash
python health_check.py
\`\`\`

Then visit:
- `http://localhost:8080/health` - Simple health check
- `http://localhost:8080/status` - Detailed statistics

### Log Monitoring

The bot creates detailed logs in `rugguard_bot.log`:

\`\`\`bash
# View recent logs
tail -20 rugguard_bot.log

# Monitor logs in real-time
tail -f rugguard_bot.log

# Search for specific events
grep "Successfully processed" rugguard_bot.log
grep "ERROR" rugguard_bot.log
\`\`\`

### Status Indicators

**🟢 Bot is Active**: Recent activity within 1 hour
**🟡 Bot is Idle**: No activity for 1-6 hours  
**🔴 Bot is Inactive**: No activity for 6+ hours

### Troubleshooting Status Issues

1. **Bot Not Responding**:
   \`\`\`bash
   # Check if process is running
   ps aux | grep python
   
   # Check recent errors
   tail -50 rugguard_bot.log | grep ERROR
   \`\`\`

2. **No Recent Activity**:
   - Check X API rate limits
   - Verify trigger phrase is being used
   - Check network connectivity

3. **Database Issues**:
   \`\`\`bash
   # Reinitialize database
   python scripts/setup_database.py
   \`\`\`

## 🎯 How It Works

1. **Monitoring**: Bot continuously monitors X for "riddle me this" mentions
2. **Trigger Detection**: When phrase is found in a reply, bot identifies the original tweet
3. **Analysis**: Comprehensive analysis of the original tweet's author:
   - Account metrics and age
   - Bio keyword analysis
   - Engagement patterns
   - Trusted follower verification
4. **Scoring**: Calculates trustworthiness score (0-100)
5. **Response**: Posts detailed analysis as a reply

## 📊 Analysis Factors

### Positive Indicators
- ✅ Account age (1+ years)
- ✅ Followed by trusted accounts
- ✅ Verified status
- ✅ Healthy follower ratios
- ✅ Relevant bio content
- ✅ Good engagement rates

### Risk Factors
- ⚠️ Very new accounts (<30 days)
- ⚠️ Suspicious follower ratios
- ⚠️ No trusted followers
- ⚠️ Minimal bio information
- ⚠️ Low engagement
- ⚠️ Spam patterns

## 🔒 Security & Privacy

- No sensitive data stored
- Analysis based on public information only
- Rate limiting to respect X API limits
- Local SQLite database for caching

## 📝 Usage Example

**User posts**: "Check out this new Solana project! 🚀"
**Reply**: "@projectrugguard riddle me this"
**Bot responds**: 
\`\`\`
🟡 RUGGUARD ANALYSIS: @username
Trust Level: MODERATE TRUST (65/100)

 Account Age: 180 days
 Followers: 1,250
 Trusted Connections: 1

⚠ Risk Factors:
• No verified status
• Limited trusted followers

✅ Positive Signs:
• Healthy follower/following ratio
• Relevant bio keywords present

🛡️ Analysis by @projectrugguard
\`\`\`

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Verify all API keys are correct
   - Check API key permissions

2. **Rate Limiting**:
   - Bot has built-in rate limiting
   - Free tier has limited requests

3. **Database Issues**:
   - Run setup script again
   - Check file permissions

### Logs

Check `rugguard_bot.log` for detailed error information.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📞 Support

For issues or questions:
- Telegram: @joshehh
- X: @Dereboyo1
- Create GitHub issue

## ⚖️ License

This project is licensed under the MIT License.

## 🚨 Disclaimer

This bot provides analysis based on publicly available data. Results should not be considered financial advice. Always do your own research (DYOR) before making investment decisions.
