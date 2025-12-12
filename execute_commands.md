
```python
import subprocess as sp
from pathlib import Path

def run_command(cmd, output_file=None, recreate=True):
    """
    Execute a shell command and return an iterable over its output lines.

    Parameters
    ----------
    cmd : str or list
        Command to execute (string or list for subprocess).
    output_file : str or Path, optional
        Path to a file where output should be written/read.
    recreate : bool
        If True: run command and overwrite output_file (if provided).
        If False: read from output_file if it exists.

    Returns
    -------
    iterable of str
        Lines of output (generator ready for looping).
    """
    # Convert to Path if needed
    if output_file is not None:
        output_file = Path(output_file)

    # Case 1: no output file → directly return command output
    if output_file is None:
        proc = sp.run(cmd, stdout=sp.PIPE, stderr=sp.STDOUT, text=True)
        return proc.stdout.splitlines()

    # Case 2: output file is provided
    if recreate or not output_file.exists():
        # Run command and write to file
        proc = sp.run(cmd, stdout=sp.PIPE, stderr=sp.STDOUT, text=True)
        output_file.write_text(proc.stdout)
        return output_file.read_text().splitlines()
    else:
        # Read existing file without running command
        return output_file.read_text().splitlines()
```

### Example usage

```python
for line in run_command(["echo", "hello"], output_file="out.txt", recreate=True):
    print(line)
```

Let me know if you want it to stream output instead of waiting for completion, or if you want asynchronous support!


Here is the **Paramiko-based SSH version**, matching the logic and parameters of your previous function.

```python
import paramiko
from pathlib import Path

def execute_ssh_cmd(
    hostname,
    command,
    username,
    password,
    output_file=None,
    recreate=True,
    port=22,
    timeout=10
):
    """
    Execute an SSH command and return an iterable of output lines.

    Parameters
    ----------
    hostname : str
        SSH server hostname or IP.
    command : str
        Command to run on the remote server.
    username : str
        SSH username.
    password : str
        SSH password.
    output_file : str or Path, optional
        File to store/read output.
    recreate : bool
        If True, run command and overwrite output_file.
        If False, read from existing file instead.

    Constants
    ---------
    port : int
        SSH port (always 22).
    timeout : int
        SSH connect timeout (10 seconds).

    Returns
    -------
    iterable of str
        Lines of command output ready for looping.
    """

    # Convert to Path if provided
    if output_file is not None:
        output_file = Path(output_file)

    # Helper: run SSH command and return stdout string
    def _run_ssh():
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=hostname,
            username=username,
            password=password,
            port=port,
            timeout=timeout
        )

        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()

        client.close()

        # Combine stdout + stderr (optional)
        return output + error

    # Case 1: no output file → run command and return lines
    if output_file is None:
        text = _run_ssh()
        return text.splitlines()

    # Case 2: output file exists but recreate=False
    if not recreate and output_file.exists():
        return output_file.read_text().splitlines()

    # Case 3: recreate=True OR file doesn't exist → run SSH and write
    text = _run_ssh()
    output_file.write_text(text)
    return text.splitlines()
```

### Example usage

```python
for line in execute_ssh_cmd(
        hostname="192.168.1.50",
        command="ls -l /var/log",
        username="user",
        password="pass",
        output_file="ssh_output.txt",
        recreate=True):
    print(line)
```

If you want SFTP support, key-based auth, or streaming output instead of waiting for completion, I can extend it!
