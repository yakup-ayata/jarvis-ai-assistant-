#!/usr/bin/env python3
"""
JARVIS Developer Brain - Code & Project Management
Handles project scaffolding, code analysis, and developer tasks
"""

import os
import json
import re
from typing import Dict, List, Optional
from pathlib import Path

class DeveloperBrain:
    """
    Developer-focused AI brain for code and project management
    """
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent / 'templates'
        print("💻 Developer Brain initialized")
    
    def process_command(self, command: str, context: Dict = None) -> Dict:
        """
        Process developer commands
        
        Args:
            command: User command
            context: Additional context (file paths, options, etc.)
        
        Returns:
            Dict with action plan and steps
        """
        command_lower = command.lower()
        
        # Classify intent
        if any(word in command_lower for word in ['create react', 'scaffold react', 'new react']):
            return self.scaffold_react_project(command, context or {})
        
        elif any(word in command_lower for word in ['create fastapi', 'scaffold fastapi', 'new fastapi']):
            return self.scaffold_fastapi_project(command, context or {})
        
        elif any(word in command_lower for word in ['create dockerfile', 'generate dockerfile', 'docker']):
            return self.create_dockerfile(command, context or {})
        
        elif any(word in command_lower for word in ['analyze error', 'check error', 'debug']):
            return self.analyze_error_log(command, context or {})
        
        elif any(word in command_lower for word in ['optimize code', 'improve code', 'refactor']):
            return self.optimize_code(command, context or {})
        
        elif any(word in command_lower for word in ['check dependencies', 'analyze dependencies', 'dependency']):
            return self.analyze_dependencies(command, context or {})
        
        else:
            return {
                'success': False,
                'error': 'Unknown developer command',
                'suggestions': [
                    'create react project',
                    'scaffold fastapi app',
                    'create dockerfile',
                    'analyze error log',
                    'optimize code',
                    'check dependencies'
                ]
            }
    
    def scaffold_react_project(self, command: str, options: Dict) -> Dict:
        """
        Create React project with best practices
        """
        # Extract project name
        project_name = options.get('name', 'my-react-app')
        
        # Parse options
        use_typescript = 'typescript' in command.lower() or options.get('typescript', True)
        use_tailwind = 'tailwind' in command.lower() or options.get('tailwind', True)
        use_router = 'router' in command.lower() or options.get('router', False)
        
        steps = []
        files_to_create = {}
        
        # Step 1: Create React app
        if use_typescript:
            steps.append({
                'step': 1,
                'action': 'create_react_app',
                'command': f'npx create-react-app {project_name} --template typescript',
                'description': 'Creating React app with TypeScript'
            })
        else:
            steps.append({
                'step': 1,
                'action': 'create_react_app',
                'command': f'npx create-react-app {project_name}',
                'description': 'Creating React app'
            })
        
        # Step 2: Install Tailwind
        if use_tailwind:
            steps.append({
                'step': 2,
                'action': 'install_tailwind',
                'command': f'cd {project_name} && npm install -D tailwindcss postcss autoprefixer',
                'description': 'Installing Tailwind CSS'
            })
            
            steps.append({
                'step': 3,
                'action': 'init_tailwind',
                'command': f'cd {project_name} && npx tailwindcss init -p',
                'description': 'Initializing Tailwind config'
            })
            
            # Tailwind config
            files_to_create[f'{project_name}/tailwind.config.js'] = self._get_tailwind_config()
            files_to_create[f'{project_name}/src/index.css'] = self._get_tailwind_css()
        
        # Step 3: Install Router
        if use_router:
            steps.append({
                'step': len(steps) + 1,
                'action': 'install_router',
                'command': f'cd {project_name} && npm install react-router-dom',
                'description': 'Installing React Router'
            })
        
        # Step 4: Create boilerplate files
        steps.append({
            'step': len(steps) + 1,
            'action': 'create_files',
            'description': 'Creating boilerplate files',
            'files': list(files_to_create.keys())
        })
        
        return {
            'success': True,
            'intent': 'scaffold_react',
            'project_name': project_name,
            'options': {
                'typescript': use_typescript,
                'tailwind': use_tailwind,
                'router': use_router
            },
            'steps': steps,
            'files_to_create': files_to_create,
            'next_steps': [
                f'cd {project_name}',
                'npm start'
            ]
        }
    
    def scaffold_fastapi_project(self, command: str, options: Dict) -> Dict:
        """
        Create FastAPI project structure
        """
        project_name = options.get('name', 'my-fastapi-app')
        
        # Parse options
        use_database = 'database' in command.lower() or 'db' in command.lower()
        use_auth = 'auth' in command.lower() or options.get('auth', False)
        use_docker = 'docker' in command.lower() or options.get('docker', True)
        
        structure = {
            f'{project_name}/': {
                'app/': {
                    '__init__.py': '',
                    'main.py': self._get_fastapi_main(),
                    'models.py': self._get_fastapi_models() if use_database else '',
                    'schemas.py': self._get_fastapi_schemas(),
                    'routers/': {
                        '__init__.py': '',
                        'users.py': self._get_user_router() if use_auth else ''
                    },
                    'database.py': self._get_database_config() if use_database else '',
                },
                'requirements.txt': self._get_fastapi_requirements(use_database, use_auth),
                'Dockerfile': self._get_dockerfile_python() if use_docker else '',
                '.env.example': self._get_env_template(),
                'README.md': f'# {project_name}\n\nFastAPI project\n\n## Setup\n```bash\npython -m venv venv\nsource venv/bin/activate\npip install -r requirements.txt\nuvicorn app.main:app --reload\n```'
            }
        }
        
        steps = [
            {
                'step': 1,
                'action': 'create_structure',
                'description': f'Creating project structure for {project_name}'
            },
            {
                'step': 2,
                'action': 'create_venv',
                'command': f'cd {project_name} && python -m venv venv',
                'description': 'Creating virtual environment'
            },
            {
                'step': 3,
                'action': 'install_deps',
                'command': f'cd {project_name} && source venv/bin/activate && pip install -r requirements.txt',
                'description': 'Installing dependencies'
            }
        ]
        
        return {
            'success': True,
            'intent': 'scaffold_fastapi',
            'project_name': project_name,
            'options': {
                'database': use_database,
                'auth': use_auth,
                'docker': use_docker
            },
            'structure': structure,
            'steps': steps,
            'next_steps': [
                f'cd {project_name}',
                'source venv/bin/activate',
                'uvicorn app.main:app --reload'
            ]
        }
    
    def create_dockerfile(self, command: str, options: Dict) -> Dict:
        """
        Create Dockerfile for project
        """
        project_type = options.get('type', 'python')
        
        if 'python' in command.lower() or project_type == 'python':
            dockerfile_content = self._get_dockerfile_python()
            project_type = 'python'
        elif 'node' in command.lower() or project_type == 'node':
            dockerfile_content = self._get_dockerfile_node()
            project_type = 'node'
        else:
            dockerfile_content = self._get_dockerfile_python()
        
        return {
            'success': True,
            'intent': 'create_dockerfile',
            'project_type': project_type,
            'dockerfile': dockerfile_content,
            'docker_compose': self._get_docker_compose(project_type),
            'next_steps': [
                'docker build -t myapp .',
                'docker run -p 8000:8000 myapp'
            ]
        }
    
    def analyze_error_log(self, command: str, options: Dict) -> Dict:
        """
        Analyze error logs and suggest solutions
        """
        log_path = options.get('log_path', 'error.log')
        
        if not os.path.exists(log_path):
            return {
                'success': False,
                'error': f'Log file not found: {log_path}'
            }
        
        with open(log_path, 'r') as f:
            log_content = f.read()
        
        # Extract errors
        errors = self._extract_errors(log_content)
        
        # Analyze each error
        analysis = []
        for error in errors:
            solution = self._get_error_solution(error)
            analysis.append({
                'error': error['message'],
                'type': error['type'],
                'line': error.get('line'),
                'file': error.get('file'),
                'solution': solution
            })
        
        return {
            'success': True,
            'intent': 'analyze_error',
            'log_path': log_path,
            'total_errors': len(errors),
            'analysis': analysis,
            'summary': f'Found {len(errors)} errors. Most common: {errors[0]["type"] if errors else "None"}'
        }
    
    def optimize_code(self, command: str, options: Dict) -> Dict:
        """
        Analyze code and suggest optimizations
        """
        file_path = options.get('file_path', 'app.py')
        
        if not os.path.exists(file_path):
            return {
                'success': False,
                'error': f'File not found: {file_path}'
            }
        
        with open(file_path, 'r') as f:
            code = f.read()
        
        issues = []
        
        # Check for common issues
        if len(code.split('\n')) > 500:
            issues.append({
                'type': 'file_size',
                'severity': 'medium',
                'message': 'File is very large (>500 lines)',
                'suggestion': 'Consider splitting into multiple files'
            })
        
        # Check for nested loops
        if re.search(r'for.*:\s*for.*:', code):
            issues.append({
                'type': 'performance',
                'severity': 'high',
                'message': 'Nested loops detected (O(n²))',
                'suggestion': 'Consider using dictionary lookup or set operations'
            })
        
        # Check for unused imports
        imports = re.findall(r'^import\s+(\w+)', code, re.MULTILINE)
        for imp in imports:
            if code.count(imp) == 1:  # Only appears in import statement
                issues.append({
                    'type': 'unused_import',
                    'severity': 'low',
                    'message': f'Unused import: {imp}',
                    'suggestion': f'Remove unused import: {imp}'
                })
        
        score = max(0, 10 - len(issues))
        
        return {
            'success': True,
            'intent': 'optimize_code',
            'file_path': file_path,
            'issues': issues,
            'score': score,
            'summary': f'Code score: {score}/10. Found {len(issues)} optimization opportunities.'
        }
    
    def analyze_dependencies(self, command: str, options: Dict) -> Dict:
        """
        Analyze project dependencies
        """
        project_path = options.get('project_path', '.')
        
        # Check for package.json (Node.js)
        package_json_path = os.path.join(project_path, 'package.json')
        requirements_path = os.path.join(project_path, 'requirements.txt')
        
        if os.path.exists(package_json_path):
            return self._analyze_npm_dependencies(package_json_path)
        elif os.path.exists(requirements_path):
            return self._analyze_python_dependencies(requirements_path)
        else:
            return {
                'success': False,
                'error': 'No dependency file found (package.json or requirements.txt)'
            }
    
    # Helper methods for templates
    
    def _get_tailwind_config(self) -> str:
        return """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}"""
    
    def _get_tailwind_css(self) -> str:
        return """@tailwind base;
@tailwind components;
@tailwind utilities;"""
    
    def _get_fastapi_main(self) -> str:
        return """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="My API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the API"}

@app.get("/health")
async def health():
    return {"status": "ok"}
"""
    
    def _get_fastapi_models(self) -> str:
        return """from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
"""
    
    def _get_fastapi_schemas(self) -> str:
        return """from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    
    class Config:
        orm_mode = True
"""
    
    def _get_user_router(self) -> str:
        return """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Add user creation logic
    pass

@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    # Add user retrieval logic
    pass
"""
    
    def _get_database_config(self) -> str:
        return """from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""
    
    def _get_fastapi_requirements(self, use_database: bool, use_auth: bool) -> str:
        reqs = ["fastapi==0.104.1", "uvicorn[standard]==0.24.0", "pydantic==2.5.0"]
        
        if use_database:
            reqs.extend(["sqlalchemy==2.0.23", "alembic==1.12.1"])
        
        if use_auth:
            reqs.extend(["python-jose[cryptography]==3.3.0", "passlib[bcrypt]==1.7.4", "python-multipart==0.0.6"])
        
        return "\n".join(reqs)
    
    def _get_dockerfile_python(self) -> str:
        return """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    def _get_dockerfile_node(self) -> str:
        return """FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
"""
    
    def _get_docker_compose(self, project_type: str) -> str:
        if project_type == 'python':
            return """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/dbname
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=dbname
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
"""
        else:
            return """version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
"""
    
    def _get_env_template(self) -> str:
        return """# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Security
SECRET_KEY=your-secret-key-here

# API
API_HOST=0.0.0.0
API_PORT=8000
"""
    
    def _extract_errors(self, log_content: str) -> List[Dict]:
        """Extract errors from log content"""
        errors = []
        
        # Common error patterns
        patterns = [
            (r'ModuleNotFoundError: No module named \'(\w+)\'', 'ModuleNotFoundError'),
            (r'TypeError: (.+)', 'TypeError'),
            (r'ValueError: (.+)', 'ValueError'),
            (r'ConnectionError: (.+)', 'ConnectionError'),
            (r'FileNotFoundError: (.+)', 'FileNotFoundError'),
        ]
        
        for pattern, error_type in patterns:
            matches = re.finditer(pattern, log_content)
            for match in matches:
                errors.append({
                    'type': error_type,
                    'message': match.group(0),
                    'details': match.group(1) if match.lastindex >= 1 else ''
                })
        
        return errors[:10]  # Limit to 10 errors
    
    def _get_error_solution(self, error: Dict) -> str:
        """Get solution for common errors"""
        error_type = error['type']
        
        solutions = {
            'ModuleNotFoundError': f"Install missing package: pip install {error.get('details', 'package-name')}",
            'TypeError': "Check type compatibility. Add type conversion if needed.",
            'ValueError': "Validate input values before processing.",
            'ConnectionError': "Check network connection and service availability.",
            'FileNotFoundError': "Verify file path exists. Use os.path.exists() to check."
        }
        
        return solutions.get(error_type, "Review error message and stack trace for details.")
    
    def _analyze_npm_dependencies(self, package_json_path: str) -> Dict:
        """Analyze npm dependencies"""
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)
        
        dependencies = package_data.get('dependencies', {})
        dev_dependencies = package_data.get('devDependencies', {})
        
        total = len(dependencies) + len(dev_dependencies)
        
        return {
            'success': True,
            'intent': 'analyze_dependencies',
            'type': 'npm',
            'total_packages': total,
            'dependencies': len(dependencies),
            'dev_dependencies': len(dev_dependencies),
            'recommendations': [
                'Run npm audit to check for security vulnerabilities',
                'Run npm outdated to check for updates',
                'Consider using npm-check-updates for bulk updates'
            ]
        }
    
    def _analyze_python_dependencies(self, requirements_path: str) -> Dict:
        """Analyze Python dependencies"""
        with open(requirements_path, 'r') as f:
            requirements = f.readlines()
        
        packages = [line.strip() for line in requirements if line.strip() and not line.startswith('#')]
        
        return {
            'success': True,
            'intent': 'analyze_dependencies',
            'type': 'python',
            'total_packages': len(packages),
            'packages': packages,
            'recommendations': [
                'Run pip list --outdated to check for updates',
                'Use pip-audit to check for security vulnerabilities',
                'Consider using poetry or pipenv for better dependency management'
            ]
        }

# Singleton instance
_developer_brain = None

def get_developer_brain() -> DeveloperBrain:
    """Get singleton Developer Brain instance"""
    global _developer_brain
    if _developer_brain is None:
        _developer_brain = DeveloperBrain()
    return _developer_brain

if __name__ == "__main__":
    # Test Developer Brain
    print("🧪 Testing Developer Brain...")
    
    brain = get_developer_brain()
    
    # Test 1: React project
    print("\n1. Testing React project scaffolding...")
    result = brain.process_command("create react project with typescript and tailwind", {'name': 'my-app'})
    print(f"   Intent: {result.get('intent')}")
    print(f"   Steps: {len(result.get('steps', []))}")
    
    # Test 2: FastAPI project
    print("\n2. Testing FastAPI project scaffolding...")
    result = brain.process_command("scaffold fastapi with database and auth", {'name': 'my-api'})
    print(f"   Intent: {result.get('intent')}")
    print(f"   Steps: {len(result.get('steps', []))}")
    
    # Test 3: Dockerfile
    print("\n3. Testing Dockerfile creation...")
    result = brain.process_command("create dockerfile for python", {})
    print(f"   Intent: {result.get('intent')}")
    print(f"   Type: {result.get('project_type')}")
    
    print("\n✓ Developer Brain test complete")
