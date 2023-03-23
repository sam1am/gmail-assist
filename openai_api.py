import openai
import time
from bs4 import BeautifulSoup
from termcolor import colored

def load_openai_api_key():
    with open('openaikey.txt', 'r') as f:
        openai.api_key = f.read()

def evaluate_importance(sender, subject, body):
    # Remove markup from body using BeautifulSoup
    time.sleep(1)
    soup = BeautifulSoup(body, "html.parser")
    body = soup.get_text()
    # remove spaces and newlines
    body = body.replace(" ", "").replace("\n", "")
    # truncate body to 140 characters max
    body = body[:140]
    print("------------------------------------\n")
    print(colored(f"{sender}", 'green'))
    print(colored(f"{subject}\n", 'blue'))
    try:
        # Load the prompt text from the file
        with open('prompt.txt', 'r') as f:
            prompt = f.read()
        # Replace the variables in the prompt with the actual values
        prompt = prompt.format(sender=sender, subject=subject, body=body)
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0.5,
            max_tokens=1,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        importance = response.choices[0].text.strip()
        print (f"Score: {importance}")
        # Update the importance value to match the keys in the label_ids dictionary
        if importance == "1":
            return "gptJunk"
        elif importance == "2":
            return "gptLow"
        elif importance == "3":
            return "gptNormal"
        elif importance == "4":
            return "gptImportant"
        elif importance == "5":
            return "gptUrgent"
        else:
            return None

    except Exception as e:
        print(f"Error during importance evaluation: {e}")
        return None


def get_prompt_text():
    with open("prompt.txt", "r") as f:
        return f.read()

load_openai_api_key()