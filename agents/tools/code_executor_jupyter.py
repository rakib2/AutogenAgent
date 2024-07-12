from autogen.coding import CodeBlock
from autogen.coding.jupyter import DockerJupyterServer, JupyterCodeExecutor

class CodeExecutor:
    def __init__(self):
        self.server = DockerJupyterServer()

    def execute_code(self, code: str) -> str:
        with self.server as server:
            executor = JupyterCodeExecutor(server)
            result = executor.execute_code_blocks(
                code_blocks=[
                    CodeBlock(language="python", code=code),
                ]
            )
        return result
