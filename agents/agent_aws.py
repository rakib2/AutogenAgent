import os
import sys
from datetime import datetime
from pathlib import Path
from autogen import ConversableAgent, register_function, GroupChat, GroupChatManager
from tools import api_call, APIInput, CodeExecutor, StorageTool
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

# Add the current directory to the Python path
sys.path.append(os.path.dirname(__file__))

# Initialize tools
output_dir = "output"
code_executor = CodeExecutor(output_dir=output_dir)
storage_tool = StorageTool()

# Define agents
llm_config = {"config_list": [{"model": "gpt-4", "api_key": "sk-proj-3KjBmqhJ4po9bDhzgLAfT3BlbkFJqwGC46bCwnMZmwRNAxN0"}]}

assistant = RetrieveAssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant.",
    llm_config=llm_config,
)

ragproxyagent = RetrieveUserProxyAgent(
    name="ragproxyagent",
    retrieve_config={
        "task": "qa",
        "docs_path": "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam/client/delete_user.html#",
    },
)


# The code writer agent's system message is to instruct the LLM on how to
code_writer_system_message = """
You have been given coding capability to solve tasks using Python code in a stateful IPython kernel.
You are responsible for writing the code, and the code executor agent will execute the code. Code executor agent has necessary packages to execute code using AWS CLI.

When you write Python code, include 'import boto3' if needed as required package
and put the code in a markdown code block with the language set to Python.
For example:
```python
x = 3
```
You can use the variable `x` in subsequent code blocks.
```python
print(x)
```

Write code incrementally and leverage the statefulness of the kernel to avoid repeating code.
Import libraries in a separate code block.
Define a function or a class in a separate code block.
Run code that produces output in a separate code block.
Run code that involves expensive operations like download, upload, and call external APIs in a separate code block.

When your code produces an output, the output will be returned to you.
Because you have limited conversation memory, if your code creates an image,
the output will be a path to the image instead of the image itself."""



code_writer_agent = ConversableAgent(
    name="code_writer_agent",
    llm_config=llm_config,
    system_message=code_writer_system_message,
    code_execution_config=False,
)

executor_agent = ConversableAgent(
    name="executor_agent",
    llm_config=False,
    code_execution_config={"executor": code_executor.get_executor()},
    human_input_mode="ALWAYS",
)

# Register the tool functions with the agents
register_function(
    api_call,
    caller=assistant,
    executor=ragproxyagent,
    name="api_call",
    description="Makes an API call to the specified endpoint.",
)

def request_aws_credentials():
    aws_access_key_id = input("Please provide your AWS Access Key ID: ")
    aws_secret_access_key = input("Please provide your AWS Secret Access Key: ")
    aws_region = input("Please provide your AWS region (default is 'us-east-1'): ") or 'us-east-1'
    storage_tool.save("aws_access_key_id", aws_access_key_id)
    storage_tool.save("aws_secret_access_key", aws_secret_access_key)
    storage_tool.save("aws_region", aws_region)
    return aws_access_key_id, aws_secret_access_key, aws_region

def create_aws_credentials_file(aws_access_key_id, aws_secret_access_key, aws_region):
    credentials_content = f"""
[default]
aws_access_key_id = {aws_access_key_id}
aws_secret_access_key = {aws_secret_access_key}
region = {aws_region}
"""
    credentials_path = Path.home() / ".aws" / "credentials"
    credentials_path.parent.mkdir(parents=True, exist_ok=True)
    with open(credentials_path, 'w') as f:
        f.write(credentials_content)

# Define custom speaker selection function
def custom_speaker_selection_func(last_speaker, groupchat):
    if last_speaker.name == "IT_Admin":
        return ragproxyagent
    elif last_speaker.name == "ragproxyagent":
        return code_writer_agent
    elif last_speaker.name == "code_writer_agent":
        return executor_agent
    elif last_speaker.name == "executor_agent":
        return None

# Initialize agents for group chat
it_admin = ConversableAgent(
    name="IT_Admin",
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
    human_input_mode="ALWAYS",
    system_message="You are an IT Admin. You can raise infrastructure-related concerns.",
)

groupchat = GroupChat(
    agents=[it_admin, ragproxyagent, code_writer_agent, executor_agent],
    messages=[],
    max_round=12,
    speaker_selection_method=custom_speaker_selection_func,
)

manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

def process_message(message):
    it_admin.initiate_chat(manager, message=message)
    groupchat.run()
    generated_code = code_writer_agent._last_msg_as_summary
    return generated_code

def handle_alert(alert):
    # Implement your alert handling logic here
    return "Alert handled for AWS"

# Request AWS credentials from the user and create the AWS credentials file
if __name__ == "__main__":
    aws_access_key_id, aws_secret_access_key, aws_region = request_aws_credentials()
    create_aws_credentials_file(aws_access_key_id, aws_secret_access_key, aws_region)
    message = "I need to create an IAM user RH20"
    response = process_message(message)
    print(f"Generated Code:\n{response}")