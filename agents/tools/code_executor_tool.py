from pathlib import Path
from autogen.coding import CodeBlock
from autogen.coding.jupyter import JupyterCodeExecutor, LocalJupyterServer
import subprocess

class CodeExecutor:
    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.server = LocalJupyterServer()

    def get_executor(self):
        return JupyterCodeExecutor(self.server, output_dir=self.output_dir)

    def execute_code(self, code: str) -> str:
        with self.server as server:
            executor = self.get_executor()
            result = executor.execute_code_blocks(
                code_blocks=[
                    CodeBlock(language="python", code=code),
                ]
            )
        return result
        # Save execution logs
        log_file = self.output_dir / "execution_log.txt"
        with open(log_file, 'w') as f:
            f.write(result)
        return result

    def export_notebook(self, format: str = "pdf") -> str:
        notebook_path = self.output_dir / "output.ipynb"
        output_file = notebook_path.with_suffix(f".{format}")
        subprocess.run(
            ["jupyter", "nbconvert", str(notebook_path), f"--to={format}"],
            check=True
        )
        return str(output_file)
