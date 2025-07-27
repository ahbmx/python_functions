# Python Script for Scheduled and Immediate Function Execution

Here's a Python script that allows you to run functions on different schedules (every N minutes, hourly, daily) and also provides an option to run functions immediately:

```python
import schedule
import time
import threading
from datetime import datetime, time as dt_time

class FunctionScheduler:
    def __init__(self):
        self.scheduled_jobs = []
        self.immediate_execution_queue = []
        self.lock = threading.Lock()
        self.running = True
        
    def run_every_n_minutes(self, func, minutes, *args, **kwargs):
        """Schedule a function to run every N minutes"""
        job = schedule.every(minutes).minutes.do(self._wrapper, func, *args, **kwargs)
        self.scheduled_jobs.append(job)
        return job
    
    def run_hourly(self, func, minute=0, *args, **kwargs):
        """Schedule a function to run hourly at a specific minute"""
        job = schedule.every().hour.at(f":{minute:02d}").do(self._wrapper, func, *args, **kwargs)
        self.scheduled_jobs.append(job)
        return job
    
    def run_daily(self, func, hour=0, minute=0, *args, **kwargs):
        """Schedule a function to run daily at a specific time"""
        job = schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self._wrapper, func, *args, **kwargs)
        self.scheduled_jobs.append(job)
        return job
    
    def run_immediately(self, func, *args, **kwargs):
        """Add a function to the immediate execution queue"""
        with self.lock:
            self.immediate_execution_queue.append((func, args, kwargs))
    
    def _wrapper(self, func, *args, **kwargs):
        """Wrapper function to log execution times"""
        print(f"[{datetime.now()}] Running {func.__name__}")
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {str(e)}")
    
    def _process_immediate_queue(self):
        """Process all functions in the immediate execution queue"""
        while True:
            with self.lock:
                if not self.immediate_exec_queue:
                    break
                func, args, kwargs = self.immediate_exec_queue.pop(0)
            
            print(f"[{datetime.now()}] Immediate execution of {func.__name__}")
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"Error in immediate {func.__name__}: {str(e)}")
    
    def start(self):
        """Start the scheduler in a separate thread"""
        def scheduler_loop():
            while self.running:
                self._process_immediate_queue()
                schedule.run_pending()
                time.sleep(1)
        
        self.thread = threading.Thread(target=scheduler_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        schedule.clear()
        self.thread.join()

# Example usage
if __name__ == "__main__":
    # Example functions to schedule
    def every_5_min_task():
        print("This task runs every 5 minutes")
    
    def hourly_task():
        print("This task runs at :15 every hour")
    
    def daily_task():
        print("This task runs at 8:30 AM daily")
    
    def immediate_task(message):
        print(f"IMMEDIATE TASK: {message}")
    
    # Create and start the scheduler
    scheduler = FunctionScheduler()
    
    # Schedule some functions
    scheduler.run_every_n_minutes(every_5_min_task, 5)
    scheduler.run_hourly(hourly_task, minute=15)
    scheduler.run_daily(daily_task, hour=8, minute=30)
    
    # Start the scheduler
    scheduler.start()
    
    try:
        # Main thread can do other things
        # Here we'll just wait and occasionally add immediate tasks
        print("Scheduler started. Press Ctrl+C to stop.")
        print("Adding some immediate tasks...")
        
        scheduler.run_immediately(immediate_task, "First immediate task")
        time.sleep(10)
        scheduler.run_immediately(immediate_task, "Second immediate task")
        
        # Keep the program running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping scheduler...")
        scheduler.stop()
        print("Scheduler stopped.")
```

## Features of this Script:

1. **Multiple Scheduling Options**:
   - Run every N minutes
   - Run hourly at a specific minute
   - Run daily at a specific time

2. **Immediate Execution**:
   - Functions can be added to an immediate execution queue
   - These are executed as soon as possible, prioritized over scheduled tasks

3. **Thread Safety**:
   - Uses threading.Lock for the immediate execution queue
   - Runs the scheduler in a separate thread

4. **Error Handling**:
   - Catches and logs exceptions from scheduled functions

5. **Logging**:
   - Prints timestamps and function names when tasks are executed

6. **Clean Shutdown**:
   - Properly stops the scheduler on KeyboardInterrupt

## How to Use:

1. Create your functions that you want to schedule
2. Create a FunctionScheduler instance
3. Schedule your functions using the appropriate methods
4. Call `start()` to begin the scheduler
5. Use `run_immediately()` to queue functions for immediate execution
6. Call `stop()` when you want to shut down the scheduler

You can easily extend this by adding more scheduling options or modifying the execution behavior as needed.
