# Contributing to JARVIS AI Assistant

First off, thank you for considering contributing to JARVIS! It's people like you that make JARVIS such a great tool.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code snippets, screenshots)
- **Describe the behavior you observed and expected**
- **Include your environment details** (OS, Python version, Node.js version)

**Bug Report Template:**
```markdown
**Description:**
A clear description of the bug

**Steps to Reproduce:**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior:**
What you expected to happen

**Actual Behavior:**
What actually happened

**Environment:**
- OS: macOS 14.0
- Python: 3.11.5
- Node.js: 18.17.0
- JARVIS Version: 2.0

**Screenshots/Logs:**
If applicable, add screenshots or log files
```

### 💡 Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List some examples** of how it would be used

### 🔧 Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Follow the coding style** of the project
3. **Write clear commit messages**
4. **Include tests** for new features
5. **Update documentation** as needed
6. **Ensure all tests pass**

#### Pull Request Process

1. **Fork and Clone**
```bash
git clone https://github.com/your-username/jarvis-ai-assistant-.git
cd jarvis-ai-assistant-
```

2. **Create a Branch**
```bash
git checkout -b feature/amazing-feature
# or
git checkout -b fix/bug-description
```

3. **Make Your Changes**
- Write clean, readable code
- Follow existing patterns
- Add comments where needed

4. **Test Your Changes**
```bash
cd jarvis_v2
source .venv/bin/activate
pytest tests/
```

5. **Commit Your Changes**
```bash
git add .
git commit -m "feat: add amazing feature"
```

**Commit Message Convention:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

6. **Push and Create PR**
```bash
git push origin feature/amazing-feature
```
Then open a Pull Request on GitHub.

## Development Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### Setup Development Environment

1. **Clone your fork**
```bash
git clone https://github.com/your-username/jarvis-ai-assistant-.git
cd jarvis-ai-assistant-/jarvis_v2
```

2. **Install dependencies**
```bash
# Python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Development tools
pip install pytest black flake8 mypy

# Frontend
cd frontend
npm install
cd ..
```

3. **Configure environment**
```bash
cp .env.example .env
# Add your API keys
```

4. **Run tests**
```bash
pytest tests/
```

## Coding Style

### Python
- Follow [PEP 8](https://pep8.org/) style guide
- Use `black` for formatting: `black .`
- Use `flake8` for linting: `flake8 .`
- Use type hints where possible
- Maximum line length: 100 characters

**Example:**
```python
from typing import Dict, List, Optional

def process_command(
    command: str,
    context: Optional[Dict[str, str]] = None
) -> Dict[str, any]:
    """
    Process a user command and return the result.
    
    Args:
        command: The user's command string
        context: Optional context dictionary
        
    Returns:
        Dict containing the processing result
    """
    # Implementation
    pass
```

### TypeScript/React
- Follow the existing component structure
- Use functional components with hooks
- Use TypeScript types (avoid `any`)
- Format with Prettier

**Example:**
```typescript
interface CommandInputProps {
  onSubmit: (command: string) => void;
  disabled?: boolean;
}

export const CommandInput: React.FC<CommandInputProps> = ({ 
  onSubmit, 
  disabled = false 
}) => {
  // Implementation
};
```

## Testing

### Python Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_brain_service.py

# Run with coverage
pytest --cov=core tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Documentation

- Update README.md if you change functionality
- Add docstrings to new functions/classes
- Update type hints
- Add comments for complex logic

### Documentation Style

```python
def complex_function(param1: str, param2: int) -> bool:
    """
    Brief one-line description.
    
    Detailed explanation of what the function does,
    including any important details about behavior.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param2 is negative
        
    Example:
        >>> complex_function("test", 42)
        True
    """
    pass
```

## Project Structure Guidelines

- **`core/`** - Core AI components (brain, memory, etc.)
- **`api/`** - API and WebSocket servers
- **`frontend/`** - React UI components
- **`tools/`** - Node.js tool servers
- **`tests/`** - Test files

When adding new files:
- Place them in the appropriate directory
- Follow existing naming conventions
- Update `__init__.py` if needed

## Getting Help

- 💬 **Discussions**: Use GitHub Discussions for questions
- 🐛 **Issues**: Use GitHub Issues for bugs
- 📧 **Email**: Contact maintainers for sensitive topics

## Recognition

Contributors will be:
- Added to CONTRIBUTORS.md
- Mentioned in release notes
- Credited in the project

Thank you for contributing! 🎉
