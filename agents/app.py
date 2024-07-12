import autogen
import tools
import tempfile
from autogen import register_function
import os
import logging
from autogen import ConversableAgent



import datetime




# Set the DOCKER_HOST environment variable
#os.environ['DOCKER_HOST'] = 'tcp://localhost:2375'

#logging.basicConfig(level=logging.DEBUG)

# Create a temporary directory
#create a temporary directory to store the code files.
temp_dir = tempfile.TemporaryDirectory()
logging.info(f"Temporary directory: {temp_dir.name}")


config_list = [
    {
    'model': 'gpt-4',
    'api_key': 'sk-proj-3KjBmqhJ4po9bDhzgLAfT3BlbkFJqwGC46bCwnMZmwRNAxN0'
    }

]


llm_config={
    "seed": 42,
    "config_list": config_list,
    "temperature": 0
}



executor = autogen.coding.LocalCommandLineCodeExecutor(
    timeout=10,  # Timeout for each code execution in seconds.
    work_dir=temp_dir.name,  # Use the temporary directory to store the code files.
)

# Set up the Jupyter server
#jupyter_server = jupyter.LocalJupyterServer(image_name=autogen_full_img, token='UNSET')

# Initialize the Jupyter Code Executor
#executor = jupyter.JupyterCodeExecutor(jupyter_server=jupyter_server)



# Initialize the DockerCommandLineCodeExecutor
#executor = DockerCommandLineCodeExecutor(
 #   image="hashicorp/terraform",
  #  timeout=10,
   # work_dir=temp_dir.name
#)


code_writer_system_message = """You are a helpful AI assistant.
Solve tasks using your coding and language skills.
In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute.
1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time, check the operating system. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself.
2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly.
Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill.
When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user.
If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.
Reply 'TERMINATE' in the end when everything is done.

Please consider that, the generated code is being mounted with the docker image which is in linux en
"""

code_writer_agent = autogen.ConversableAgent(
    "code_writer_agent",
    system_message=code_writer_system_message,
    llm_config={"config_list": [{"model": "gpt-4", "api_key": "sk-proj-3KjBmqhJ4po9bDhzgLAfT3BlbkFJqwGC46bCwnMZmwRNAxN0"}]},
    code_execution_config=False,  # Turn off code execution for this agent.
)



# Create an agent with code executor configuration.
code_executor_agent = autogen.ConversableAgent(
    "code_executor_agent_docker",
    llm_config=False,  # Turn off LLM for this agent.
    code_execution_config={"executor": executor},  # Use the local command line code executor.
    human_input_mode="ALWAYS",  # Always take human input for this agent for safety.
)

today = datetime.datetime.now().strftime("%Y-%m-%d")

# Generate a reply for the given code.
chat_result = code_executor_agent.initiate_chat(
    code_writer_agent,
    #message="Write Python code to calculate the 14th Fibonacci number.",
    message=f"Today is {today}. Write Python code to plot TSLA's and META's "
    "stock price gains YTD, and save the plot to a file named 'stock_gains.png'.",
)



# Register the API call tool to both agents
register_function(
    api_call_tool._run,
    caller=assistant,  # The assistant agent can suggest calls to the API tool.
    executor=user_proxy,  # The user proxy agent can execute the API tool calls.
    name="api_call_tool",  # The tool name.
    description="A tool to make API calls to third-party services.",  # A description of the tool.
)


#print(os.listdir(temp_dir.name))
# We can see the output scatter.png and the code file generated by the agent.



agentgenai = autogen.ConversableAgent(
    "Infrastructure",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": "sk-proj-3KjBmqhJ4po9bDhzgLAfT3BlbkFJqwGC46bCwnMZmwRNAxN0"}]},
    #llm_config={"config_list": [{"model": "gpt-4", "api_key": os.environ.get("OPENAI_API_KEY")}]},
    code_execution_config=False,  # Turn off code execution, by default it is off.
    function_map=None,  # No registered functions, by default it is None.
    human_input_mode="TERMINATE",  # Never ask for human input.
    #is_termination_msg=lambda msg: "good bye" in msg["content"].lower(),
    system_message="""You are an Infrastructure Expert with a broad understanding of various technologies and platforms within an organization. You possess complete knowledge of the entire infrastructure, including on-premises servers and cloud-based services. You have access to different data sources and can provide guidance on configuration changes across the organization.
    In addition to your expertise, you also have the ability to keep track of previous configuration changes made by other agents. This allows you to provide accurate information and ensure continuity in the infrastructure's configuration.
    Whether it's troubleshooting issues, suggesting improvements, or providing guidance on best practices, you are equipped with the necessary knowledge and historical context to assist users effectively. Feel free to ask any questions or request assistance with any aspect of the infrastructure."""

)


agentaws = autogen.ConversableAgent(
    "AWS",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": "sk-proj-3KjBmqhJ4po9bDhzgLAfT3BlbkFJqwGC46bCwnMZmwRNAxN0"}]},
    #llm_config={"config_list": [{"model": "gpt-4", "api_key": os.environ.get("OPENAI_API_KEY")}]},
    code_execution_config=False,  # Turn off code execution, by default it is off.
    function_map=None,  # No registered functions, by default it is None.
    human_input_mode="TERMINATE",  # Never ask for human input.
    #max_consecutive_auto_reply=1,  # Limit the number of consecutive auto-replies.
    system_message="""You are an Infrastructure Expert and your role is to guide users on what can be done with specific infrastructure setups. You specialize in cloud platforms like AWS and can provide Terraform code for various services upon request. You will ask for additional input from the user if needed. You should only provide known information about the infrastructure when the user specifically asks for it. Additionally, when requested for execution, you should provide the executable code.
    For example, if a user asks for the Terraform code to provision an EC2 instance in AWS, you should provide the appropriate code and ask for any necessary input from the user."""

)

agentms = autogen.ConversableAgent(
    "Microsoft",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": "sk-proj-3KjBmqhJ4po9bDhzgLAfT3BlbkFJqwGC46bCwnMZmwRNAxN0"}]},
    #llm_config={"config_list": [{"model": "gpt-4", "api_key": os.environ.get("OPENAI_API_KEY")}]},
    code_execution_config=False,  # Turn off code execution, by default it is off.
    function_map=None,  # No registered functions, by default it is None.
    human_input_mode="TERMINATE",  # Never ask for human input.
    system_message="""You are an Infrastructure Expert specializing in Microsoft environments. Your role is to guide users on what can be done within the specific infrastructure setup. You have expertise in PowerShell scripting and can provide code snippets to execute configuration changes in the environment. For example, you can assist with tasks such as checking Active Directory (AD) health, finding unused security groups, removing redundant Box users, checking for mailbox users without licenses, and adding licenses when necessary.
    If a user requests assistance with any of these tasks, you will provide the PowerShell code required to perform the action and guide them through the process."""

)

assistant = autogen.AssistantAgent(
    name="Cloud Engineer",
    llm_config=llm_config,
    system_message="Cloud Specialist to provision and configure cloud environemnt"
)


user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"work_dir": "web",
                           "use_docker": False},
    llm_config=llm_config,
    
    system_message="""Reply TERMINATE if the task has been solved at full satisfaction, Otherwise, reply CONTINUE, or the reason why the task is not solved yet."""

)

task ="""
write me a terraform code template to provision ec2 instance in AWS and store the terraform code in a '.tf' file.
"""

#reply = agentgenai.generate_reply(messages=[{"content": "Create a terraform code for ec2 instance in AWS", "role": "assistant"}])

#user_proxy.initiate_chat(
    #assistant,
    #message=task
#)



