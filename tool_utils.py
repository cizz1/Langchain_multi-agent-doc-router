from tools_custom import file_parser,get_dummy_files_list,get_file_info, find_file_in_dummy_dir
from langchain_core.tools import tool
import redis
import json
from typing import Any
from pydantic import BaseModel
from datetime import datetime

#file parsing tool used by all agents
@tool
def file_parser_tool(filename: str) -> dict:
    """
    Parses and extracts content from the given file.
    
    Args:
        filename (str): The full name of the file to parse, including its extension (e.g., 'invoice_123.json', 'email_456.eml', 'complaint_789.pdf').
    
    Returns:
        dict: A dictionary containing the parsed content of the file.
    
    Example:
        file_parser_tool('sample_email.eml')
    """
    print("file tool using")
    file_path = find_file_in_dummy_dir(filename)
    return file_parser(file_path)



#logging tool for classifier agent
@tool
def write_memory_log_classifier(data: Any, filename: str) -> str:
    """
    Writes memory logs to long-term Redis store.
    
    Args:
        data: The data to log
        filename: The filename for the log
    """
    REDIS_URI = "redis://localhost:6379"
    redis_client = redis.Redis.from_url(REDIS_URI)
    print("writing into memory")
    time = datetime.now()
    try:
        data_type = str(type(data))
        
        redis_key = f"logs:{filename}:classifier"
        redis_value = json.dumps({
            "timestamp": f'{time.strftime("%H-%M-%S")}',
            "data": data
        })
        
        redis_client.set(redis_key, redis_value)
        
        return f"Memory logged successfully at key: {redis_key}, type: {data_type}"
    except Exception as e:
        return f"Error logging memory: {str(e)}"


# for the email_agent
@tool
def write_memory_log_email(data: Any, filename: str) -> str:
    """
    Writes memory logs to long-term Redis store.
    
    Args:
        data: The data to log
        filename: The filename for the log
    """
    REDIS_URI = "redis://localhost:6379"
    redis_client = redis.Redis.from_url(REDIS_URI)
    print("writing into memory")
    time = datetime.now()
    try:
        data_type = str(type(data))
        
        redis_key = f"logs:{filename}:email_agent"
        redis_value = json.dumps({
            "timestamp": f'{time.strftime("%H-%M-%S")}',
            "data": data
        })
        
        redis_client.set(redis_key, redis_value)
        
        return f"Memory logged successfully at key: {redis_key}, type: {data_type}"
    except Exception as e:
        return f"Error logging memory: {str(e)}"



# for the email_agent
@tool
def write_memory_log_json(data: Any, filename: str) -> str:
    """
    Writes memory logs to long-term Redis store.
    
    Args:
        data: The data to log
        filename: The filename for the log
    """
    REDIS_URI = "redis://localhost:6379"
    redis_client = redis.Redis.from_url(REDIS_URI)
    print("writing into memory")
    time = datetime.now()
    
    try:
        data_type = str(type(data))
        
        redis_key = f"logs:{filename}:json_agent"
        redis_value = json.dumps({
            "timestamp": f'{time.strftime("%H-%M-%S")}',
            "data": data
        })
        
        redis_client.set(redis_key, redis_value)
        
        return f"Memory logged successfully at key: {redis_key}, type: {data_type}"
    except Exception as e:
        return f"Error logging memory: {str(e)}"
