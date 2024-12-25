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

### Environment Variables

#### Required Configuration
```bash
# Required: OpenAI API key for LLM integration
export OPENAI_API_KEY=your_api_key
```

#### LLM Configuration
```bash
# Optional: LLM model settings (defaults shown)
export SLEEPYTESTING_LLM_MODEL=gpt-4           # Model to use
export SLEEPYTESTING_LLM_TEMPERATURE=0.7       # Sampling temperature (0.0-1.0)
export SLEEPYTESTING_LLM_MAX_TOKENS=2000       # Maximum tokens per request

# Rate Limiting Configuration
export SLEEPYTESTING_LLM_MAX_RETRIES=3         # Maximum retry attempts
export SLEEPYTESTING_LLM_MIN_RETRY_WAIT=1.0    # Minimum retry wait time (seconds)
export SLEEPYTESTING_LLM_MAX_RETRY_WAIT=60.0   # Maximum retry wait time (seconds)
export SLEEPYTESTING_LLM_MAX_CONCURRENT=5      # Maximum concurrent requests
export SLEEPYTESTING_LLM_RATE_LIMIT=50         # Maximum requests per period
export SLEEPYTESTING_LLM_RATE_PERIOD=60        # Rate limit period (seconds)
```

#### Platform Configuration
```bash
# Platform and Framework Selection
export SLEEPYTESTING_PLATFORM=android          # android/ios/web
export SLEEPYTESTING_FRAMEWORK=uiautomator2    # uiautomator2/appium/selenium

# Device Configuration
export SLEEPYTESTING_ANDROID_DEVICE=device_id  # Android device ID
export SLEEPYTESTING_IOS_DEVICE=device_id      # iOS device ID

# Optional: Device Whitelisting
export SLEEPYTESTING_ALLOWED_ANDROID_DEVICES=device1,device2
export SLEEPYTESTING_ALLOWED_IOS_DEVICES=device3,device4
```

### Configuration Examples

#### Basic Setup
```bash
# Minimal configuration for Android testing
export OPENAI_API_KEY=your_api_key
export SLEEPYTESTING_PLATFORM=android
export SLEEPYTESTING_ANDROID_DEVICE=your_device_id
```

#### Multi-Device Testing
```bash
# Configure for both Android and iOS testing
export OPENAI_API_KEY=your_api_key
export SLEEPYTESTING_ANDROID_DEVICE=android_device_id
export SLEEPYTESTING_IOS_DEVICE=ios_device_id
```

#### Advanced LLM Configuration
```bash
# Fine-tune LLM behavior
export OPENAI_API_KEY=your_api_key
export SLEEPYTESTING_LLM_MODEL=gpt-4
export SLEEPYTESTING_LLM_TEMPERATURE=0.5  # Lower temperature for more focused outputs
export SLEEPYTESTING_LLM_MAX_TOKENS=4000  # Increase token limit for complex tasks
```

#### Rate Limiting for Production
```bash
# Configure rate limiting for production environment
export SLEEPYTESTING_LLM_MAX_CONCURRENT=3     # Limit concurrent requests
export SLEEPYTESTING_LLM_RATE_LIMIT=30        # Reduce requests per minute
export SLEEPYTESTING_LLM_MIN_RETRY_WAIT=2.0   # Increase minimum retry wait time
```

### Troubleshooting

1. **API Key Issues**
   - Ensure OPENAI_API_KEY is set and valid
   - Check API key permissions and quotas

2. **Rate Limiting**
   - Adjust SLEEPYTESTING_LLM_RATE_LIMIT if hitting API limits
   - Increase retry wait times for busy environments

3. **Model Selection**
   - Use GPT-4 for complex tasks requiring better understanding
   - GPT-3.5-turbo suitable for simpler tasks with faster response

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
