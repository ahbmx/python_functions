Below are **streaming-based versions** of both functions:

* `run_command_stream()` → executes **local commands** using `subprocess` and streams output.
* `execute_ssh_cmd_stream()` → executes **SSH commands using Paramiko** and streams output.

Both support:

* `output_file=None`
* `recreate=True | False`
* returning an **iterator (generator)** that yields lines live
* writing to a file *while streaming* (if `output_file` is provided)

---

# ✅ **1. Local command (subprocess) — STREAMING version**

```python
import subprocess as sp
from pathlib import Path

def run_command_stream(cmd, output_file=None, recreate=True):
    """
    Run a local command and stream its output line by line.

    Parameters
    ----------
    cmd : str or list
    output_file : str or Path, optional
    recreate : bool

    Returns
    -------
    generator that yields lines of output (streaming)
    """

    if output_file is not None:
        output_file = Path(output_file)

    # If no file OR recreate=True OR file doesn't exist → run command
    should_run = (output_file is None) or recreate or not output_file.exists()

    if not should_run:
        # Read existing file
        def reader():
            with output_file.open("r") as f:
                for line in f:
                    yield line.rstrip("\n")
        return reader()

    # Otherwise: run command and stream output
    def streamer():
        proc = sp.Popen(
            cmd,
            stdout=sp.PIPE,
            stderr=sp.STDOUT,
            text=True,
            bufsize=1
        )

        file_handle = None
        if output_file is not None:
            file_handle = output_file.open("w")

        try:
            for line in proc.stdout:
                line = line.rstrip("\n")
                if file_handle:
                    file_handle.write(line + "\n")
                yield line
        finally:
            if file_handle:
                file_handle.close()
            proc.wait()

    return streamer()
```

---

# ✅ **2. SSH command (Paramiko) — STREAMING version**

```python
import paramiko
from pathlib import Path
import time

def execute_ssh_cmd_stream(
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
    Execute an SSH command and stream its output line by line.

    Returns a generator that yields lines in real time.
    """

    if output_file is not None:
        output_file = Path(output_file)

    # Determine whether we must run the command or read from file
    should_run = (output_file is None) or recreate or not output_file.exists()

    if not should_run:
        # Read existing file without running command
        def reader():
            with output_file.open("r") as f:
                for line in f:
                    yield line.rstrip("\n")
        return reader()

    # Streaming SSH executor
    def streamer():
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

        channel = stdout.channel

        file_handle = None
        if output_file is not None:
            file_handle = output_file.open("w")

        try:
            buffer = ""
            while not channel.exit_status_ready():
                # Read in small chunks as the command runs
                if channel.recv_ready():
                    chunk = channel.recv(1024).decode()
                    buffer += chunk

                    # Yield lines as soon as they are complete
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        if file_handle:
                            file_handle.write(line + "\n")
                        yield line

                time.sleep(0.1)  # avoid busy-waiting

            # Flush any remaining partial output
            remaining = buffer.strip()
            if remaining:
                if file_handle:
                    file_handle.write(remaining + "\n")
                yield remaining

        finally:
            if file_handle:
                file_handle.close()
            client.close()

    return streamer()
```

---

# ✅ Example Usage

### **Local streaming command**

```python
for line in run_command_stream(["ping", "-c", "4", "google.com"],
                               output_file="local.log",
                               recreate=True):
    print("> ", line)
```

### **SSH streaming command**

```python
for line in execute_ssh_cmd_stream(
        hostname="192.168.1.10",
        command="tail -f /var/log/syslog",
        username="root",
        password="pass",
        output_file="remote.log",
        recreate=True):
    print("> ", line)
```

---

If you want, I can also provide:

* async versions (asyncio + asyncssh)
* support for key-based authentication
* combined stdout/stderr streaming
* timeouts on command execution

Just tell me!
