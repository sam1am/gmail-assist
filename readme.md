# Gmail Importance Classifier using GPT-3

This script uses OpenAI's GPT-3 to classify the importance of unread emails in Gmail and labels them accordingly. The labels used are:
- gptJunk (for junk or spam)
- gptLow (for non-urgent updates from companies or organizations)
- gptNormal (for general correspondence or updates)
- gptImportant (for important personal messages)
- gptUrgent (for urgent or time-sensitive messages)

## Prerequisites

To run this script, you need:
- Python 3
- A Google Cloud Platform project with the Gmail API enabled
- Credentials for the Gmail API
- An OpenAI API key
- Add the labels listed above to your gmail account

## Installation

1. Clone this repository
2. Install the required Python packages by running `pip install -r requirements.txt`
3. Set up the Google Cloud Platform project and the Gmail API credentials by following the instructions [here](https://developers.google.com/gmail/api/quickstart/python) and saving the credentials file as `credentials.json` in the project directory
4. Obtain an OpenAI API key by following the instructions [here](https://beta.openai.com/docs/quickstart)
5. Save the OpenAI API key to a text file named `openaikey.txt` in the project directory

## Usage

1. Run the script by running `python gmail_assist.py`
2. The script will connect to the Gmail API and find *unread* emails *not already labeled* by the script. They will be labeled based on their importance. 

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- OpenAI for providing the GPT-3 API
- Google for providing the Gmail API
