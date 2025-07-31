import argparse
from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    HumanMessage,
    AIMessage,
)
from langchain_openai import ChatOpenAI, OpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
import os
import asyncio
import openai

rules_path = "rules/rules.md"
style_path = "rules/style.md"

load_dotenv()
custom_tools = []

async def get_all_tools():
    """Получение всех инструментов: ваших + MCP"""
    # Настройка MCP клиента
    mcp_client = MultiServerMCPClient(
        {
            "filesystem": {
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
            },
            "context7": {
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@upstash/context7-mcp"],
            },
            "ebook-mcp": {
                "transport": "stdio",
                "command": "uv",
                "args": [
                    "--directory",
                    "C:\\Users\\AKazlou\\mcp\\ebook-mcp\\src\\ebook_mcp\\",
                    "run",
                    "main.py"
                ]
            },
        }
    )

    # Получаем MCP инструменты
    mcp_tools = await mcp_client.get_tools()

    # Объединяем ваши инструменты с MCP инструментами
    return custom_tools + mcp_tools

async def run_query(agent, query: str):
    """Выполняет один запрос к агенту с читаемым выводом"""
    print(f"🎯 Запрос: {query}")
    
    step_counter = 0
    processed_messages = set()  # Для избежания дублирования
    
    try:
        async for event in agent.astream(
            {"messages": [{"role": "user", "content": query}]},
            config={"recursion_limit": 50},
            stream_mode="values",
        ):
            if "messages" in event and event["messages"]:
                messages = event["messages"]
                
                # Обрабатываем только новые сообщения
                for msg in messages:
                    msg_id = getattr(msg, 'id', str(id(msg)))
                    if msg_id in processed_messages:
                        continue
                    processed_messages.add(msg_id)
                    
                    # Получаем тип сообщения
                    msg_type = getattr(msg, 'type', 'unknown')
                    content = getattr(msg, 'content', '')
                    
                    # 1. Сообщения от пользователя
                    if msg_type == 'human':
                        print(f"👤 Пользователь: {content}")
                        print("-" * 40)
                    
                    # 2. Сообщения от ИИ
                    elif msg_type == 'ai':
                        # Проверяем наличие вызовов инструментов
                        tool_calls = getattr(msg, 'tool_calls', [])
                        
                        if tool_calls:
                            step_counter += 1
                            print(f"🤖 Шаг {step_counter}: Агент использует инструменты")
                            
                            # Размышления агента (если есть)
                            if content and content.strip():
                                print(f"💭 Размышления: {content}")
                            
                            # Детали каждого вызова инструмента
                            for i, tool_call in enumerate(tool_calls, 1):
                                # Парсим tool_call в зависимости от формата
                                if isinstance(tool_call, dict):
                                    tool_name = tool_call.get('name', 'unknown')
                                    tool_args = tool_call.get('args', {})
                                    tool_id = tool_call.get('id', 'unknown')
                                else:
                                    # Если это объект с атрибутами
                                    tool_name = getattr(tool_call, 'name', 'unknown')
                                    tool_args = getattr(tool_call, 'args', {})
                                    tool_id = getattr(tool_call, 'id', 'unknown')
                                
                                print(f"🔧 Инструмент {i}: {tool_name}")
                                print(f"   📥 Параметры: {tool_args}")
                                print(f"   🆔 ID: {tool_id}")
                            print("-" * 40)
                        
                        # Финальный ответ (без tool_calls)
                        elif content and content.strip():
                            print(f"🎉 Финальный ответ:")
                            print(f"💬 {content}")
                            print("-" * 40)
                    
                    # 3. Результаты выполнения инструментов
                    elif msg_type == 'tool':
                        tool_name = getattr(msg, 'name', 'unknown')
                        tool_call_id = getattr(msg, 'tool_call_id', 'unknown')
                        print(f"📤 Результат инструмента: {tool_name}")
                        print(f"   🆔 Call ID: {tool_call_id}")
                        
                        # Форматируем результат
                        if content:
                            # Пытаемся распарсить JSON для красивого вывода
                            try:
                                import json
                                if content.strip().startswith(('{', '[')):
                                    parsed = json.loads(content)
                                    formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
                                    print(f"   📊 Результат:")
                                    for line in formatted.split('\n'):
                                        print(f"     {line}")
                                else:
                                    print(f"   📊 Результат: {content}")
                            except:
                                print(f"   📊 Результат: {content}")
                        print("-" * 40)
                    
                    # 4. Другие типы сообщений (для отладки)
                    else:
                        if content:
                            print(f"❓ Неизвестный тип ({msg_type}): {content[:100]}...")
                            print("-" * 40)
    
    except Exception as e:
        print(f"❌ Ошибка при выполнении запроса: {e}")
        print(f"📊 Выполнено шагов: {step_counter}")
        raise
    
    print("=" * 80)
    print("✅ Запрос обработан")
    print()

async def main():
    all_tools = await get_all_tools()

    parser = argparse.ArgumentParser(description="Summarize PDF chapter to Obsidian.")
    # parser.add_argument("--file", required=True, help="Path to the PDF file.")
    # parser.add_argument("--pages", required=True, help="Page range to process (e.g., 43-58).")
    # parser.add_argument("--out", required=True, help="Output directory for Obsidian.")
    parser.add_argument("--query", required=True, help="Output directory for Obsidian.")

    args = parser.parse_args()
    # start_page, end_page = map(int, args.pages.split('-'))
    userQuery = args.query

    print(f"[1] Reading summarization rules from {rules_path}...")
    with open(rules_path, "r", encoding="utf-8") as f:
        rules_text = f.read()
    
    print(f"[2] Reading summarization rules from {style_path}...")
    with open(style_path, "r", encoding="utf-8") as f:
        style_text = f.read()

    prompt = f"""
        You are a professional technical specialist and technical writer helping a developer study new technologies and write summaries in Markdown format.
        
        IMPORTANT INSTRUCTIONS:
        1. When asked to summarize PDF content, use the ebook-mcp tools to read the PDF pages
        2. Extract text from the specified page range
        3. Create a well-structured summary following the rules below
        4. Write the summary to a file in the output directory
        5. Provide a final response confirming completion
        
        Follow these summarization rules strictly:
        <rules>
        {rules_text}
        </rules>

        Summarize the content in a clear, structured Markdown format.
        Use the following style guidelines:
        <style_guidelines>
        {style_text}
        </style_guidelines>
        
        Always provide a clear, final response when your task is complete.
        """

    # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    # client = openai.OpenAI(api_key=OPENAI_API_KEY)

    gpt4_model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.4,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # gpt4_model=OpenAI(
    #         model="gpt-4o-mini",
    #         temperature=0.4,
    #         api_key=os.getenv("OPENAI_API_KEY")
    # )

    # Создаем агента с инструментами и промптом
    print("[3] Creating agent with tools and prompt...")

    agent = create_react_agent(
        model=gpt4_model,
        tools=all_tools,
        prompt=prompt
    )

    print("[4] Summarizing content via LLM...")
    # await run_query(agent, f"Summarize the content of the PDF file {args.file} from pages {start_page} to {end_page}.")
    await run_query(agent, userQuery)

if __name__ == "__main__":
    asyncio.run(main())