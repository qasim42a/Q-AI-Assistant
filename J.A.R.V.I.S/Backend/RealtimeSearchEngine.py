from duckduckgo_search import DDGS
from openai import OpenAI
from json import load, dump
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GroqAPIKey
)
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""
# For JSON file
try:
    with open("Data\\ChatLog.json", "r") as f:
        messages = load(f)
except:
    with open("Data\\ChatLog.json", "w") as f:
        dump([], f)
# our search       
def GoogleSearch(query):
    Answer = f"The search results for '{query}' are:\n[start]\n"
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)
        for result in results:
            title = result.get("title", "No Title")
            snippet = result.get("body", "No Description")
            Answer += f"Title: {title}\nDescription: {snippet}\n\n"
    Answer += "[end]"
    return Answer
# Remove blank lline
def AnswerModifier(Answer):
    if not Answer or not isinstance(Answer, str):
        return "Oops! No valid answer was generated. 😢"
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

# Initial system
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, Sir, how can I help you?"}
]

# Get time data
def Information():
    now = datetime.datetime.now()
    return (
        "Use This Real-time Information if needed:\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours: {now.strftime('%M')} minutes: {now.strftime('%S')} seconds.\n"
    )

# Main function
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    with open("Data\\ChatLog.json", "r") as f:
        messages = load(f)
    messages.append({"role": "user", "content": prompt})

    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        max_tokens=2048,
        temperature=0.7,
        top_p=1
    )

    Answer = completion.choices[0].message.content.strip()
    messages.append({"role": "assistant", "content": Answer})

    # Save chat
    with open("Data\\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

    SystemChatBot.pop()
    return AnswerModifier(Answer)

# Run loop
if __name__ == "__main__":
    while True:
        prompt = input("Enter Your Query: ")
        print(RealtimeSearchEngine(prompt))
