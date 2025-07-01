import os
import re
import subprocess
import asyncio
import requests
import webbrowser
import time
import pyautogui
import keyboard
from dotenv import dotenv_values
from pywhatkit import search, playonyt
from bs4 import BeautifulSoup
from AppOpener import close, open as appopen
from rich import print
from groq import Groq

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None

thread_map = {
    "silent_vortex": "17842852758323478", 
}

SystemChatBot_Messages = [{
    "role": "system",
    "content": "You're a professional content writer. You write articles, letters, notes, applications, essays, poems, and code clearly and formally."
}]

def GoogleSearch(query):
    print(f"[yellow]Performing Google search for: {query}[/yellow]")
    search(query)
    return True

def OpenYouTubeHomepage():
    print("[yellow]Opening YouTube homepage...[/yellow]")
    webbrowser.open("http://youtube.com") 
    return True

def YouTubeSearch(topic):
    print(f"[yellow]Performing Youtube for: {topic}[/yellow]")
    webbrowser.open(f"http://youtube.com/results?search_query={topic}")
    return True

def PlayYoutube(query):
    try:
        print(f"[yellow]Playing YouTube video/searching for: {query}[/yellow]")
        playonyt(query)
        return True
    except Exception as e:
        print(f"[red]YouTube Play Error: {e}[/red]")
        return False

def InstagramDM(username_or_id, message):
    thread_id = thread_map.get(username_or_id, username_or_id)
    message = message.replace("VS", "❤️") 
    try:
        url = f"https://www.instagram.com/direct/t/{thread_id}/"
        print(f"[green]Opening Instagram DM: {url}[/green]")
        webbrowser.open(url)
        time.sleep(10)
        print(f"[yellow]Clicking on message box at 784, 696...[/yellow]")
        pyautogui.click(784, 696)
        print("[yellow]Waiting for input focus (2 seconds)...[/yellow]")
        time.sleep(2)
        print(f"[yellow]Typing message: {message}[/yellow]")
        pyautogui.write(message, interval=0.01)
        pyautogui.press('enter')
        print(f"[cyan]Message sent to {username_or_id}[/cyan]")
        return True
    except Exception as e:
        print(f"[red]Instagram DM Error: {e}[/red]")
        return False

def Content(topic):
    def ContentWriterAI(prompt):
        if not client:
            return "Error: Missing Groq API key. Please set it in your .env file."
        current_messages = list(SystemChatBot_Messages)
        current_messages.append({"role": "user", "content": prompt})
        try:
            print(f"[yellow]Generating content for: {prompt}...[/yellow]")
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=current_messages,
                max_tokens=2048,
                temperature=0.7,
                top_p=1,
                stream=True
            )
            answer = ""
            for chunk in completion:
                content_piece = chunk.choices[0].delta.content if chunk.choices[0].delta else ""
                if content_piece:
                    answer += content_piece
            return answer.strip()
        except Exception as e:
            return f"Error during content generation: {e}"

    topic = topic.replace("content", "").strip()
    filename_base = re.sub(r'[\\/*?:"<>|]', "", topic.lower().replace(" ", "_"))
    if not filename_base:
        filename_base = "untitled_content"
        print("[yellow]Warning: Content topic was empty, saving as 'untitled_content.txt'.[/yellow]")

    result = ContentWriterAI(topic)
    os.makedirs("Data", exist_ok=True)
    filepath = os.path.join("Data", f"{filename_base}.txt")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(result)
        subprocess.Popen(["notepad.exe", filepath])
        print(f"[green]Content saved and opened: {filepath}[/green]")
        return True
    except Exception as e:
        print(f"[red]File writing/opening error: {e}[/red]")
        return False

def OpenApp(app):
    try:
        print(f"[yellow]Attempting to open app: {app}[/yellow]")
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        print(f"[red]Failed to open app {app}: {e}[/red]")
        return False

def CloseApp(app):
    try:
        print(f"[yellow]Attempting to close app: {app}[/yellow]")
        if "chrome" in app.lower():
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], check=True)
            print("[green]Closed Chrome via taskkill.[/green]")
        else:
            close(app, match_closest=True, output=True, throw_error=True)
            print(f"[green]Closed app {app} via AppOpener.[/green]")
        return True
    except Exception as e:
        print(f"[red]CloseApp error for {app}: {e}[/red]")
        return False

def System(command):
    try:
        print(f"[yellow]Executing system command: {command}[/yellow]")
        if command in ["mute", "unmute"]:
            keyboard.press_and_release("volume mute")
        elif command == "volume up":
            keyboard.press_and_release("volume up")
        elif command == "volume down":
            keyboard.press_and_release("volume down")
        else:
            print("[red]Unknown system command.[/red]")
            return False
        print(f"[green]System command '{command}' executed.[/green]")
        return True
    except Exception as e:
        print(f"[red]System command error: {e}[/red]")
        return False

async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        print(f"[bold blue]Processing command:[/bold blue] {command}")
        if command.startswith("open "):
            target = command[5:].strip().lower()
            if target == "youtube":
                funcs.append(asyncio.to_thread(OpenYouTubeHomepage))
            else:
                funcs.append(asyncio.to_thread(OpenApp, target))
        elif command.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, command[6:].strip()))
        elif command.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, command[5:].strip()))
        elif command.startswith("content "):
            funcs.append(asyncio.to_thread(Content, command[8:].strip()))
        elif command.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, command[14:].strip()))
        elif command.startswith("Youtube "):
            funcs.append(asyncio.to_thread(YouTubeSearch, command[15:].strip()))
        elif command.startswith("system "):
            funcs.append(asyncio.to_thread(System, command[7:].strip()))
        elif command.startswith("message instagram "):
            parts = command[18:].strip().split(" ", 1)
            if len(parts) == 2:
                username, msg = parts
                funcs.append(asyncio.to_thread(InstagramDM, username, msg))
            else:
                print(f"[red]Invalid Instagram message command format: {command}. Expected 'message instagram [username] [message]'.[/red]")
        else:
            print(f"[red]No specific handler found for: {command}[/red]")

    if funcs:
        results = await asyncio.gather(*funcs, return_exceptions=True)
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"[bold red]Command {i+1} failed with error:[/bold red] {result}")
            else:
                print(f"[bold green]Command {i+1} result:[/bold green] {result}")
    else:
        print("[yellow]No executable automation functions were identified.[/yellow]")
    return True

async def Automation(commands: list[str]):
    print(f"\U0001f7e1 Starting automation for commands: {commands}")
    return await TranslateAndExecute(commands)

if __name__ == "__main__":
    asyncio.run(Automation([""]))
