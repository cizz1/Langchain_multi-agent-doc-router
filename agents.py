from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_ollama import ChatOllama   ##uncomment if using ollama models
from prompts import classifier_prompt, json_prompt, email_prompt
from langgraph.checkpoint.redis import RedisSaver
from tools_custom import get_dummy_files_list,get_file_info
# from langchain
import os
from dotenv import load_dotenv
load_dotenv()
import time
from datetime import datetime
import redis
from tool_utils import (
    write_memory_log_classifier, 
    write_memory_log_email, 
    file_parser_tool, 
    write_memory_log_json
    )

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", api_key=os.getenv("GOOGLE_API_KEY"),temperature=0.1)

# Optional and doesnt perform as well unless bgger models are used
# llm = ChatOllama(model="llama3.1:8b",base_url="http://localhost:11434",temperature=0.0)

REDIS_URI = "redis://localhost:6379"
redis_client = redis.Redis.from_url(REDIS_URI)




def run_test():
    all_files = get_dummy_files_list()
    if not all_files:
        print("No supported files found in dummy_files directory")
        return
    
    print(f"Found {len(all_files)} files to process:")
    for file_path in all_files:
        file_info = get_file_info(file_path)
        print(f"  - {file_info.get('relative_path', file_path)} ({file_info.get('size_bytes', 0)} bytes)")

    
    # Using RedisSaver as context manager
    with RedisSaver.from_conn_string(REDIS_URI) as checkpointer:
        checkpointer.setup()
        
        
        # Sub agents 
        json_agent = create_react_agent(
            llm,
            prompt=json_prompt,
            tools=[write_memory_log_json,file_parser_tool],
            name="json_agent"
        )
        
        email_agent = create_react_agent(
            llm,
            prompt=email_prompt,
            tools=[write_memory_log_email,file_parser_tool],
            name="email_agent"
        )
        
        # Create and compile classifier agent
        classifier_agent = create_supervisor(
            [json_agent, email_agent],
            model=llm,
            prompt=classifier_prompt,
            tools=[file_parser_tool,write_memory_log_classifier],
            add_handoff_messages=True,
            output_mode="full_history"
    
        ).compile(checkpointer=checkpointer)

        # Process each file in its own thread
        # Each file is treated as a new thread id
        for file_path in all_files:
            file_info = get_file_info(file_path)
            filename = file_info.get('filename', os.path.basename(file_path))
            thread_id = f"file_{filename.replace('.', '_')}_{time.strftime('%H-%M-%S')}"
        
            print(f"\n🔄 Processing: {file_info.get('relative_path', filename)}")
            print(f"   Thread ID: {thread_id}")
            
            user_input = {
                "messages": [
                    {
                        "role": "user", 
                        "content": f"Please process the file: {file_info.get('relative_path', filename)}"
                    }
                ]
            }
            
            config = {"configurable": {"thread_id": thread_id}}
            
            
                # Process the file
            for chunk in classifier_agent.stream(user_input, stream_mode="values", config=config):
                chunk["messages"][-1].pretty_print()
                

if __name__ == "__main__":
    run_test()