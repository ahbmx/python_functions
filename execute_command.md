```python
import subprocess
import os

def execute_command(command, output_file=None, recreate=False):
    file_handle = None
    if output_file:
        if recreate and os.path.exists(output_file):
            os.remove(output_file)
        file_handle = open(output_file, 'w')
    
    shell_flag = isinstance(command, str)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell_flag, universal_newlines=True
    )
    
    output_lines = []
    for line in process.stdout:
        line = line.rstrip('\n')
        output_lines.append(line)
        if file_handle:
            print(line, file=file_handle)
    
    if file_handle:
        file_handle.close()
    
    process.wait()
    return output_lines
```
