from Frontend.GUI import (
    GraphicalUserInterface,
    SetAsssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus,
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechtoText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")

DefaultMessage = f""" {Username}: Hello {Assistantname}, How are you?
{Assistantname}: Welcome {Username}. I am doing well. How may I help you? """

functions = ["open", "close", "play", "system", "content", "search", "Youtube", "message instagram"]
subprocess_list = []

def ShowDefaultChatIfNoChats():
    try:
        if not os.path.exists(r'Data\ChatLog.json') or os.path.getsize(r'Data\ChatLog.json') < 5:
            with open(r'Data\ChatLog.json', "w", encoding='utf-8') as file:
                file.write("[]")
        if not os.path.exists(TempDirectoryPath('Database.data')) or os.path.getsize(TempDirectoryPath('Database.data')) == 0:
            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as response_file:
                response_file.write(DefaultMessage)
    except FileNotFoundError:
        os.makedirs("Data", exist_ok=True)
        with open(r'Data\ChatLog.json', "w", encoding='utf-8') as file:
            file.write("[]")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as response_file:
            response_file.write(DefaultMessage)

def ReadChatLogJson():
    try:
        with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
            chatlog_data = json.load(file)
        return chatlog_data
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"{Username}: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"{Assistantname}: {entry['content']}\n"
    temp_dir_path = TempDirectoryPath('')
    if not os.path.exists(temp_dir_path):
        os.makedirs(temp_dir_path)
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), 'r', encoding='utf-8') as file:
            data = file.read()
        if len(str(data)) > 0:
            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as response_file:
                response_file.write(data)
        else:
            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as response_file:
                response_file.write(DefaultMessage)
    except FileNotFoundError:
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as response_file:
            response_file.write(DefaultMessage)

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatOnGUI()

def MainExecution():
    try:
        TaskExecution = False
        ImageExecution = False
        ImageGenerationQuery = ""
        SetAsssistantStatus("Listening...")
        Query = SpeechRecognition()
        if not Query:
            SetAsssistantStatus("Available...")
            return
        ShowTextToScreen(f"{Username}: {Query}")
        SetAsssistantStatus("Thinking...")
        Decision = FirstLayerDMM(Query)
        R = any([i for i in Decision if i.startswith("realtime")])
        merged_search_query_parts = []
        for item in Decision:
            if item.startswith("general") or item.startswith("realtime"):
                merged_search_query_parts.append(" ".join(item.split()[1:]))
        Merged_query = " and ".join(merged_search_query_parts) if merged_search_query_parts else Query
        for queries in Decision:
            if "generate" in queries:
                ImageGenerationQuery = str(queries)
                ImageExecution = True
                break
        automation_commands = []
        for query_item in Decision:
            if any(query_item.startswith(func) for func in functions):
                automation_commands.append(query_item)
        if automation_commands:
            run(Automation(automation_commands))
            TaskExecution = True
        if ImageExecution:
            with open(r'Frontend\Files\ImageGeneration.data', "w") as file:
                cleaned_image_query = ImageGenerationQuery.replace("generate ", "", 1).strip()
                file.write(f"{cleaned_image_query},True")
            try:
                p1 = subprocess.Popen([
                    'python', r"Backend\ImageGeneration.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    shell=False,
                )
                subprocess_list.append(p1)
            except Exception as e:
                print(f"Error starting ImageGeneration.py: {e}")
        if not TaskExecution or Merged_query:
            if R:
                SetAsssistantStatus("Searching...")
                Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAsssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            else:
                general_queries = [i.replace("general", "").strip() for i in Decision if i.startswith("general")]
                if general_queries:
                    final_chat_query = " ".join(general_queries)
                    if not final_chat_query:
                        final_chat_query = Query
                    SetAsssistantStatus("Thinking...")
                    Answer = ChatBot(QueryModifier(final_chat_query))
                    ShowTextToScreen(f"{Assistantname}: {Answer}")
                    SetAsssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    return True
                elif "exit" in Decision:
                    QueryFinal = "Okay, Bye!"
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname}: {Answer}")
                    SetAsssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    os._exit(1)
                else:
                    SetAsssistantStatus("Available...")
    except Exception as e:
        SetAsssistantStatus("Error!")
        import traceback
        traceback.print_exc()

def FirstThread():
    while True:
        try:
            CurrentStatus = GetMicrophoneStatus()
            if CurrentStatus.lower() == "true":
                MainExecution()
            elif CurrentStatus.lower() == "false":
                AIStatus = GetAssistantStatus()
                if "Available..." in AIStatus:
                    sleep(0.1)
                else:
                    SetAsssistantStatus("Available...")
            else:
                sleep(1)
        except Exception as e:
            sleep(1)

def SecondThread():
    try:
        GraphicalUserInterface()
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    InitialExecution()
    thread1 = threading.Thread(target=FirstThread, daemon=True)
    thread1.start()
    SecondThread()
