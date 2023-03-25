import openai
import time
from bs4 import BeautifulSoup
from termcolor import colored

def load_openai_api_key():
    with open('openaikey.txt', 'r') as f:
        openai.api_key = f.read()

def evaluate_importance(sender, subject, body):
    time.sleep(0)
    soup = BeautifulSoup(body, "html.parser")
    body = soup.get_text()
    body = body.replace(" ", "").replace("\n", "")
    body = body[:140] # Truncate body to first 140 characters
    print("------------------------------------\n")
    print(time.strftime("%I:%M:%S %p"))
    print(colored(f"{sender}", 'green'))
    print(colored(f"{subject}\n", 'blue'))
    try:
        with open('prompt.txt', 'r') as f:
            prompt = f.read()
        prompt = prompt.format(sender=sender, subject=subject, body=body)
        response = openai.Completion.create(
            engine="text-davinci-003", # define the model here
            prompt=prompt,
            temperature=0.5,
            max_tokens=1,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        importance = response.choices[0].text.strip()
        print (f"Score: {importance}")
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