# sleepyTesting

A LLM-driven UI testing framework that utilizes multi-agent systems to plan and execute mobile/web UI tasks.

## Features

### 1. Multi-Agent Architecture
The framework consists of several independently usable agents:
- **Task Decomposer**: Converts natural language task descriptions into specific UI steps using LLM
- **Controller**: Coordinates task execution and agent interactions
- **Supervisor**: Monitors and validates each operation
- **Memory**: Stores and learns from historical task executions
- **Executor**: Interfaces with UI Automator2 for mobile UI automation

### 2. Core Capabilities

#### Self-Supervision
The framework provides comprehensive operation monitoring:
- Real-time validation of each UI operation
- Screenshot-based verification before and after actions
- Step-by-step execution validation
- Immediate error detection and reporting

#### Assertion System
A completely decoupled assertion system supporting:
- **Element Assertions**
  - Element existence checks
  - Visibility verification
  - Clickability validation
- **Page Assertions**
  - Page state verification
  - Feature availability checks
- **Custom Assertions**
  - User-defined validation logic
  - Complex scenario support

#### Self-Evolution
The framework learns from historical executions:
- Task pattern learning and optimization
- Reduced need for user corrections over time
- Success pattern recognition
- Automated step optimization

## Independent Module Usage

Each component can be used independently:

### Task Decomposer
```python
from sleepyTesting.agents.decomposer import TaskDecomposer

# Use task decomposer independently
decomposer = TaskDecomposer()
steps = decomposer.decompose_task("Click the login button and enter username")
```

### Assertions
```python
from sleepyTesting.assertions.element import ElementAssertion
from sleepyTesting.assertions.page import PageAssertion

# Use assertions independently
element_check = ElementAssertion.exists("login_button")
page_check = PageAssertion.has_functionality("user_login")
```

### UI Automation
```python
from sleepyTesting.core.uiautomator import UIAutomator

# Use UI automation independently
ui = UIAutomator()
ui.click(element_id="login_button")
```

## Installation

```bash
pip install sleepyTesting
```

## Requirements
- Python 3.8+
- UI Automator2
- OpenAI API key (for LLM integration)

## Configuration
Set up your environment variables:
```bash
export OPENAI_API_KEY=your_api_key
```

## Full Framework Usage
```python
from sleepyTesting.agents.controller import ControllerAgent
from sleepyTesting.agents.decomposer import TaskDecomposer
from sleepyTesting.core.uiautomator import UIAutomator

# Initialize components
decomposer = TaskDecomposer()
executor = UIAutomator()
controller = ControllerAgent(decomposer, executor)

# Execute a task with full framework capabilities
results = await controller.execute_task(
    "Open the settings and enable dark mode"
)
```

## Contributing
Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
