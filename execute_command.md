```python
import subprocess
import os

def execute_command(command, output_file=None, recreate=False):
    if output_file and os.path.exists(output_file) and not recreate:
        with open(output_file, 'r') as f:
            return [line.rstrip('\n') for line in f]

    shell_flag = isinstance(command, str)
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=shell_flag,
        universal_newlines=True
    )

    output_lines = []
    for line in process.stdout:
        line = line.rstrip('\n')
        output_lines.append(line)

    if output_file:
        with open(output_file, 'w') as f:
            f.write('\n'.join(output_lines))
   
    process.wait()
    return output_lines
```
