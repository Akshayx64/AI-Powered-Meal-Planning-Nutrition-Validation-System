"""
Callback functions for task monitoring and logging.
Implements comprehensive tracking of agent execution flow.
"""

from typing import Dict, Any, List
from datetime import datetime
import json
import os
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama for colored console output
init(autoreset=True)


class ExecutionLogger:
    """
    Centralized logger for tracking agent execution, task progress, and errors.
    Provides both console and file logging with structured output.
    """
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize the execution logger."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.execution_log_file = self.log_dir / "agent_execution.log"
        self.task_log_file = self.log_dir / "task_execution.json"
        
        self.execution_history: List[Dict[str, Any]] = []
        self.current_task: Dict[str, Any] = {}
        
    def log_task_start(self, task_name: str, agent_name: str, description: str = ""):
        """Log the start of a task execution."""
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "task_name": task_name,
            "agent_name": agent_name,
            "description": description,
            "start_time": timestamp,
            "status": "running"
        }
        
        self.current_task = log_entry
        
        # Console output
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}🚀 TASK STARTED: {task_name}")
        print(f"{Fore.CYAN}   Agent: {agent_name}")
        print(f"{Fore.CYAN}   Time: {timestamp}")
        if description:
            print(f"{Fore.CYAN}   Description: {description}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        # File output
        self._write_to_log(f"\n[{timestamp}] TASK START: {task_name} (Agent: {agent_name})")
        if description:
            self._write_to_log(f"  Description: {description}")
    
    def log_task_step(self, step_name: str, details: str = "", data: Dict[str, Any] = None):
        """Log an intermediate step during task execution."""
        timestamp = datetime.now().isoformat()
        
        # Console output
        print(f"{Fore.GREEN}  ✓ {step_name}")
        if details:
            print(f"{Fore.WHITE}    {details}")
        if data:
            print(f"{Fore.YELLOW}    Data: {json.dumps(data, indent=2)[:200]}...")
        
        # File output
        self._write_to_log(f"[{timestamp}]   STEP: {step_name}")
        if details:
            self._write_to_log(f"    {details}")
        if data:
            self._write_to_log(f"    Data: {json.dumps(data)}")
    
    def log_task_complete(self, output_summary: str = "", metadata: Dict[str, Any] = None):
        """Log the successful completion of a task."""
        timestamp = datetime.now().isoformat()
        
        if self.current_task:
            self.current_task["end_time"] = timestamp
            self.current_task["status"] = "completed"
            self.current_task["output_summary"] = output_summary
            self.current_task["metadata"] = metadata or {}
            
            self.execution_history.append(self.current_task.copy())
        
        # Console output
        print(f"\n{Fore.GREEN}{'='*80}")
        print(f"{Fore.GREEN}✅ TASK COMPLETED: {self.current_task.get('task_name', 'Unknown')}")
        print(f"{Fore.GREEN}   Duration: {self._calculate_duration()}")
        if output_summary:
            print(f"{Fore.GREEN}   Output: {output_summary[:100]}...")
        print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}\n")
        
        # File output
        self._write_to_log(f"[{timestamp}] TASK COMPLETE: {self.current_task.get('task_name', 'Unknown')}")
        self._write_to_log(f"  Duration: {self._calculate_duration()}")
        if output_summary:
            self._write_to_log(f"  Output: {output_summary}")
        
        # Save to JSON
        self._save_json_log()
    
    def log_task_error(self, error_message: str, error_details: Dict[str, Any] = None):
        """Log a task execution error."""
        timestamp = datetime.now().isoformat()
        
        if self.current_task:
            self.current_task["end_time"] = timestamp
            self.current_task["status"] = "failed"
            self.current_task["error_message"] = error_message
            self.current_task["error_details"] = error_details or {}
            
            self.execution_history.append(self.current_task.copy())
        
        # Console output
        print(f"\n{Fore.RED}{'='*80}")
        print(f"{Fore.RED}❌ TASK FAILED: {self.current_task.get('task_name', 'Unknown')}")
        print(f"{Fore.RED}   Error: {error_message}")
        if error_details:
            print(f"{Fore.RED}   Details: {json.dumps(error_details, indent=2)}")
        print(f"{Fore.RED}{'='*80}{Style.RESET_ALL}\n")
        
        # File output
        self._write_to_log(f"[{timestamp}] TASK FAILED: {self.current_task.get('task_name', 'Unknown')}")
        self._write_to_log(f"  Error: {error_message}")
        if error_details:
            self._write_to_log(f"  Details: {json.dumps(error_details)}")
        
        # Save to JSON
        self._save_json_log()
    
    def log_agent_action(self, action: str, details: str = ""):
        """Log a specific agent action."""
        timestamp = datetime.now().isoformat()
        
        print(f"{Fore.BLUE}  → {action}")
        if details:
            print(f"{Fore.WHITE}    {details}")
        
        self._write_to_log(f"[{timestamp}]   ACTION: {action}")
        if details:
            self._write_to_log(f"    {details}")
    
    def log_tool_usage(self, tool_name: str, input_data: Dict[str, Any], output_data: Any):
        """Log tool usage by agents."""
        timestamp = datetime.now().isoformat()
        
        print(f"{Fore.MAGENTA}  🔧 Tool Used: {tool_name}")
        print(f"{Fore.WHITE}     Input: {str(input_data)[:100]}...")
        print(f"{Fore.WHITE}     Output: {str(output_data)[:100]}...")
        
        self._write_to_log(f"[{timestamp}]   TOOL: {tool_name}")
        self._write_to_log(f"    Input: {json.dumps(input_data)}")
        self._write_to_log(f"    Output: {str(output_data)[:500]}")
    
    def log_state_update(self, state_key: str, state_value: Any):
        """Log updates to shared state."""
        timestamp = datetime.now().isoformat()
        
        print(f"{Fore.YELLOW}  📝 State Update: {state_key}")
        
        self._write_to_log(f"[{timestamp}]   STATE UPDATE: {state_key}")
        self._write_to_log(f"    Value: {str(state_value)[:500]}")
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a summary of the entire execution."""
        total_tasks = len(self.execution_history)
        completed_tasks = sum(1 for task in self.execution_history if task["status"] == "completed")
        failed_tasks = sum(1 for task in self.execution_history if task["status"] == "failed")
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "execution_history": self.execution_history
        }
    
    def print_execution_summary(self):
        """Print a formatted execution summary."""
        summary = self.get_execution_summary()
        
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}📊 EXECUTION SUMMARY")
        print(f"{Fore.CYAN}{'='*80}")
        print(f"{Fore.WHITE}  Total Tasks: {summary['total_tasks']}")
        print(f"{Fore.GREEN}  Completed: {summary['completed_tasks']}")
        print(f"{Fore.RED}  Failed: {summary['failed_tasks']}")
        print(f"{Fore.YELLOW}  Success Rate: {summary['success_rate']:.1f}%")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    def _calculate_duration(self) -> str:
        """Calculate the duration of the current task."""
        if not self.current_task or "start_time" not in self.current_task:
            return "Unknown"
        
        start = datetime.fromisoformat(self.current_task["start_time"])
        end = datetime.now()
        duration = end - start
        
        minutes, seconds = divmod(duration.total_seconds(), 60)
        return f"{int(minutes)}m {int(seconds)}s"
    
    def _write_to_log(self, message: str):
        """Write a message to the log file."""
        with open(self.execution_log_file, "a", encoding="utf-8") as f:
            f.write(f"{message}\n")
    
    def _save_json_log(self):
        """Save execution history to JSON file."""
        with open(self.task_log_file, "w", encoding="utf-8") as f:
            json.dump(self.execution_history, f, indent=2)


# Create a global logger instance
execution_logger = ExecutionLogger()


def create_task_callback(task_name: str):
    """
    Create a callback function for a specific task.
    This follows CrewAI's callback pattern.
    """
    def callback(output):
        """Callback function to be executed after task completion."""
        try:
            # Extract output information
            output_text = output.raw if hasattr(output, 'raw') else str(output)
            description = output.description if hasattr(output, 'description') else ""
            agent = output.agent if hasattr(output, 'agent') else "Unknown"
            
            # Log the task completion
            execution_logger.log_task_complete(
                output_summary=output_text[:200],
                metadata={
                    "agent": agent,
                    "description": description,
                    "full_output_length": len(output_text)
                }
            )
            
        except Exception as e:
            execution_logger.log_task_error(
                error_message=f"Error in task callback: {str(e)}",
                error_details={"exception_type": type(e).__name__}
            )
    
    return callback


def create_step_callback():
    """
    Create a step callback to monitor individual agent steps.
    This provides more granular monitoring than task callbacks.
    """
    def step_callback(step_output):
        """Callback for individual agent steps."""
        try:
            # Log the step
            action = step_output.action if hasattr(step_output, 'action') else "Unknown action"
            result = step_output.result if hasattr(step_output, 'result') else "No result"
            
            execution_logger.log_agent_action(
                action=action,
                details=str(result)[:200]
            )
            
        except Exception as e:
            print(f"{Fore.RED}Error in step callback: {e}{Style.RESET_ALL}")
    
    return step_callback
