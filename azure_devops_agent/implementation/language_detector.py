"""
Language Detector module for Azure DevOps Integration Agent.

This module is responsible for detecting programming languages in the repository
and identifying language-specific patterns to guide code implementation.
"""

import os
import logging
import re
from typing import Dict, List, Set, Optional, Any, Tuple
from collections import Counter

logger = logging.getLogger(__name__)

class LanguageDetector:
    """Detect programming languages and frameworks in the repository."""
    
    # File extension to language mapping
    LANGUAGE_EXTENSIONS = {
        # JavaScript/TypeScript
        'js': 'JavaScript',
        'jsx': 'JavaScript (React)',
        'ts': 'TypeScript',
        'tsx': 'TypeScript (React)',
        'mjs': 'JavaScript (ES Module)',
        'cjs': 'JavaScript (CommonJS)',
        
        # Python
        'py': 'Python',
        'pyx': 'Cython',
        'ipynb': 'Jupyter Notebook',
        
        # Java
        'java': 'Java',
        'scala': 'Scala',
        'kt': 'Kotlin',
        'kts': 'Kotlin Script',
        
        # C#/.NET
        'cs': 'C#',
        'vb': 'Visual Basic .NET',
        'fs': 'F#',
        
        # Ruby
        'rb': 'Ruby',
        'erb': 'Ruby (ERB)',
        
        # PHP
        'php': 'PHP',
        
        # Go
        'go': 'Go',
        
        # Rust
        'rs': 'Rust',
        
        # C/C++
        'c': 'C',
        'cpp': 'C++',
        'cc': 'C++',
        'h': 'C/C++ Header',
        'hpp': 'C++ Header',
        
        # Swift
        'swift': 'Swift',
        
        # Web
        'html': 'HTML',
        'htm': 'HTML',
        'xhtml': 'HTML',
        'css': 'CSS',
        'scss': 'SCSS',
        'sass': 'Sass',
        'less': 'Less',
        
        # Config/Data
        'json': 'JSON',
        'yaml': 'YAML',
        'yml': 'YAML',
        'xml': 'XML',
        'toml': 'TOML',
        'ini': 'INI',
        'conf': 'Config',
        
        # Shell
        'sh': 'Shell',
        'bash': 'Bash',
        'zsh': 'Zsh',
        'fish': 'Fish',
        'ps1': 'PowerShell',
        
        # Other
        'md': 'Markdown',
        'sql': 'SQL',
        'graphql': 'GraphQL',
        'gql': 'GraphQL',
    }
    
    # Framework detection patterns
    FRAMEWORK_PATTERNS = {
        # JavaScript/TypeScript frameworks
        'React': [
            r'import\s+.*?React', 
            r'from\s+[\'"]react[\'"]',
            r'<.*?React\..*?>',
            r'React\.Component'
        ],
        'Angular': [
            r'@angular/core',
            r'@Component\(',
            r'@NgModule\(',
            r'Angular\.',
            r'ngOnInit'
        ],
        'Vue': [
            r'import\s+.*?vue',
            r'from\s+[\'"]vue[\'"]',
            r'createApp\(',
            r'new\s+Vue\(',
            r'<template>',
            r'v-for',
            r'v-if'
        ],
        'Express': [
            r'import\s+.*?express',
            r'require\([\'"]express[\'"]',
            r'express\(\)',
            r'app\.get\(',
            r'app\.post\(',
            r'app\.use\('
        ],
        'Next.js': [
            r'import\s+.*?next',
            r'from\s+[\'"]next',
            r'NextPage',
            r'NextApiRequest',
            r'getStaticProps',
            r'getServerSideProps'
        ],
        
        # Python frameworks
        'Django': [
            r'from\s+django',
            r'import\s+django',
            r'urlpatterns',
            r'ModelForm',
            r'django\.db\.models',
            r'django\.shortcuts',
            r'settings\.py.*?INSTALLED_APPS'
        ],
        'Flask': [
            r'from\s+flask\s+import',
            r'import\s+flask',
            r'Flask\(__name__\)',
            r'@app\.route',
            r'flask\.request'
        ],
        'FastAPI': [
            r'from\s+fastapi\s+import',
            r'import\s+fastapi',
            r'FastAPI\(',
            r'@app\.get',
            r'@app\.post'
        ],
        'Pytest': [
            r'import\s+pytest',
            r'from\s+pytest',
            r'@pytest\.fixture',
            r'pytest\.raises',
            r'def\s+test_'
        ],
        
        # Java frameworks
        'Spring': [
            r'import\s+org\.springframework',
            r'@SpringBootApplication',
            r'@Controller',
            r'@RestController',
            r'@Service',
            r'@Repository',
            r'@Autowired'
        ],
        'JUnit': [
            r'import\s+org\.junit',
            r'@Test',
            r'Assert\.',
            r'assertEquals',
            r'assertTrue'
        ],
        
        # C# frameworks
        'ASP.NET': [
            r'using\s+Microsoft\.AspNetCore',
            r'AddControllers\(',
            r'\[ApiController\]',
            r'\[HttpGet\]',
            r'\[Route\('
        ],
        'Entity Framework': [
            r'using\s+Microsoft\.EntityFrameworkCore',
            r'DbContext',
            r'DbSet<',
            r'OnModelCreating'
        ],
        'NUnit': [
            r'using\s+NUnit\.Framework',
            r'\[Test\]',
            r'\[TestFixture\]',
            r'Assert\.'
        ],
        
        # Ruby frameworks
        'Rails': [
            r'class\s+.*?\s*<\s*ApplicationController',
            r'ActiveRecord::Base',
            r'rails/all',
            r'has_many',
            r'belongs_to'
        ],
        
        # PHP frameworks
        'Laravel': [
            r'Illuminate\\',
            r'use\s+App\\Http\\Controllers',
            r'extends\s+Controller',
            r'Artisan::command'
        ],
        'Symfony': [
            r'Symfony\\Component',
            r'extends\s+AbstractController',
            r'@Route\('
        ],
        
        # Go frameworks
        'Gin': [
            r'github.com/gin-gonic/gin',
            r'gin\.Default\(',
            r'gin\.New\(',
            r'r\.GET\(',
            r'c\.JSON\('
        ],
        
        # Rust frameworks
        'Rocket': [
            r'rocket::\{',
            r'#\[get\]',
            r'#\[post\]',
            r'rocket::build\(',
            r'rocket::launch\('
        ],
        'Actix': [
            r'actix_web::\{',
            r'use actix_web',
            r'HttpServer::new',
            r'App::new\('
        ],
    }
    
    def __init__(self, repo_path: str):
        """
        Initialize the language detector.
        
        Args:
            repo_path: Path to the repository root directory.
        """
        self.repo_path = repo_path
        logger.info(f"Language detector initialized for repository at {repo_path}")
    
    def detect_languages(self) -> Dict[str, int]:
        """
        Detect programming languages used in the repository based on file extensions.
        
        Returns:
            Dictionary mapping language names to their frequency (file count).
        """
        language_counts = Counter()
        
        # Walk through all files in the repository
        for root, _, files in os.walk(self.repo_path):
            # Skip .git directory
            if '.git' in root.split(os.path.sep):
                continue
                
            for file in files:
                # Get file extension
                _, extension = os.path.splitext(file)
                extension = extension[1:].lower() if extension else ''
                
                # Map extension to language
                if extension in self.LANGUAGE_EXTENSIONS:
                    language = self.LANGUAGE_EXTENSIONS[extension]
                    language_counts[language] += 1
        
        logger.info(f"Detected languages: {dict(language_counts)}")
        return dict(language_counts)
    
    def detect_frameworks(self, language: Optional[str] = None) -> Dict[str, int]:
        """
        Detect frameworks used in the repository.
        
        Args:
            language: Optional language filter.
            
        Returns:
            Dictionary mapping framework names to their detection confidence.
        """
        framework_counts = Counter()
        
        # Filter patterns based on language if specified
        framework_patterns = self.FRAMEWORK_PATTERNS
        if language:
            # This is a simplistic approach; in a real implementation,
            # you would have a more sophisticated mapping from language to frameworks
            framework_patterns = {k: v for k, v in framework_patterns.items() 
                                if self._is_framework_for_language(k, language)}
        
        # Limit file extensions to check based on language
        extensions_to_check = self._get_extensions_for_language(language) if language else None
        
        # Walk through appropriate files in the repository
        for root, _, files in os.walk(self.repo_path):
            # Skip .git directory
            if '.git' in root.split(os.path.sep):
                continue
                
            for file in files:
                # Check if the file has an extension we care about
                _, extension = os.path.splitext(file)
                extension = extension[1:].lower() if extension else ''
                
                if extensions_to_check and extension not in extensions_to_check:
                    continue
                    
                # Check file content for framework patterns
                file_path = os.path.join(root, file)
                try:
                    self._check_file_for_frameworks(file_path, framework_patterns, framework_counts)
                except Exception as e:
                    logger.warning(f"Error checking file {file_path}: {str(e)}")
        
        logger.info(f"Detected frameworks: {dict(framework_counts)}")
        return dict(framework_counts)
    
    def _check_file_for_frameworks(self, 
                                  file_path: str, 
                                  patterns: Dict[str, List[str]], 
                                  counts: Counter) -> None:
        """
        Check a single file for framework patterns.
        
        Args:
            file_path: Path to the file to check.
            patterns: Dictionary of framework patterns.
            counts: Counter to update with matches.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Skip binary files
            return
            
        # Check each framework's patterns
        for framework, framework_patterns in patterns.items():
            for pattern in framework_patterns:
                if re.search(pattern, content):
                    counts[framework] += 1
                    break  # Only count each framework once per file
    
    def _is_framework_for_language(self, framework: str, language: str) -> bool:
        """
        Check if a framework is associated with a specific language.
        
        Args:
            framework: Framework name.
            language: Language name.
            
        Returns:
            True if the framework is for the specified language.
        """
        # This is a simplified mapping; a real implementation would be more comprehensive
        language_frameworks = {
            'JavaScript': ['React', 'Angular', 'Vue', 'Express', 'Next.js'],
            'TypeScript': ['React', 'Angular', 'Vue', 'Express', 'Next.js'],
            'Python': ['Django', 'Flask', 'FastAPI', 'Pytest'],
            'Java': ['Spring', 'JUnit'],
            'C#': ['ASP.NET', 'Entity Framework', 'NUnit'],
            'Ruby': ['Rails'],
            'PHP': ['Laravel', 'Symfony'],
            'Go': ['Gin'],
            'Rust': ['Rocket', 'Actix'],
        }
        
        # Handle language variations
        normalized_language = language.split(' ')[0]  # e.g., "TypeScript (React)" -> "TypeScript"
        
        return framework in language_frameworks.get(normalized_language, [])
    
    def _get_extensions_for_language(self, language: str) -> Set[str]:
        """
        Get file extensions associated with a language.
        
        Args:
            language: Language name.
            
        Returns:
            Set of file extensions.
        """
        # Normalize language name
        normalized_language = language.split(' ')[0]  # e.g., "TypeScript (React)" -> "TypeScript"
        
        # Get extensions that map to this language
        extensions = {ext for ext, lang in self.LANGUAGE_EXTENSIONS.items() 
                     if lang.split(' ')[0] == normalized_language}
        
        return extensions
    
    def analyze_code_style(self, language: str, file_paths: List[str]) -> Dict[str, Any]:
        """
        Analyze code style in the given files for a specific language.
        
        Args:
            language: Language to analyze.
            file_paths: List of file paths to analyze.
            
        Returns:
            Dictionary with code style information.
        """
        style_info = {
            'indentation': None,
            'line_length': 0,
            'naming_conventions': {},
            'comment_style': [],
            'bracing_style': None,
        }
        
        if language in ['JavaScript', 'TypeScript']:
            style_info = self._analyze_js_ts_style(file_paths)
        elif language == 'Python':
            style_info = self._analyze_python_style(file_paths)
        elif language == 'Java':
            style_info = self._analyze_java_style(file_paths)
        elif language in ['C#', 'C++', 'C']:
            style_info = self._analyze_c_style(file_paths)
        
        logger.info(f"Analyzed code style for {language}: {style_info}")
        return style_info
    
    def _analyze_js_ts_style(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Analyze JavaScript/TypeScript code style.
        
        Args:
            file_paths: List of file paths to analyze.
            
        Returns:
            Dictionary with style information.
        """
        # Initialize counters
        space_indent_count = 0
        tab_indent_count = 0
        indent_sizes = Counter()
        line_lengths = []
        
        # Function naming conventions
        camel_case_count = 0
        snake_case_count = 0
        
        # Bracing styles
        same_line_braces = 0
        new_line_braces = 0
        
        # Semicolon usage
        semicolon_count = 0
        no_semicolon_count = 0
        
        for file_path in file_paths[:10]:  # Limit to 10 files for performance
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line in lines:
                    # Check indentation
                    if line.strip():
                        indent = len(line) - len(line.lstrip())
                        if indent > 0:
                            if line[0] == '\t':
                                tab_indent_count += 1
                            else:
                                space_indent_count += 1
                                indent_sizes[indent] += 1
                        
                        # Check line length
                        line_lengths.append(len(line.rstrip()))
                        
                        # Check semicolon usage
                        stripped = line.strip()
                        if stripped and not stripped.startswith('//') and not stripped.startswith('/*'):
                            if stripped.endswith(';'):
                                semicolon_count += 1
                            elif re.match(r'^[^;]+$', stripped) and not stripped.endswith('{') and not stripped.endswith('}'):
                                no_semicolon_count += 1
                    
                # Check function naming conventions
                content = ''.join(lines)
                camel_case_funcs = len(re.findall(r'function\s+([a-z][a-zA-Z0-9]*)', content))
                snake_case_funcs = len(re.findall(r'function\s+([a-z][a-z0-9_]*)', content))
                camel_case_count += camel_case_funcs
                snake_case_count += snake_case_funcs
                
                # Check bracing style
                same_line_braces += len(re.findall(r'\)\s*{', content))
                new_line_braces += len(re.findall(r'\)\s*\n\s*{', content))
                    
            except Exception as e:
                logger.warning(f"Error analyzing file {file_path}: {str(e)}")
        
        # Determine most common style
        style_info = {
            'indentation': 'tabs' if tab_indent_count > space_indent_count else 'spaces',
            'indent_size': indent_sizes.most_common(1)[0][0] if indent_sizes else 2,
            'line_length': int(sum(line_lengths) / len(line_lengths)) if line_lengths else 80,
            'naming_conventions': {
                'functions': 'camelCase' if camel_case_count > snake_case_count else 'snake_case'
            },
            'bracing_style': 'same_line' if same_line_braces > new_line_braces else 'new_line',
            'semicolons': True if semicolon_count > no_semicolon_count else False
        }
        
        return style_info
    
    def _analyze_python_style(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Analyze Python code style.
        
        Args:
            file_paths: List of file paths to analyze.
            
        Returns:
            Dictionary with style information.
        """
        # Initialize counters
        space_indent_count = 0
        tab_indent_count = 0
        indent_sizes = Counter()
        line_lengths = []
        
        # Naming conventions
        snake_case_count = 0
        camel_case_count = 0
        
        # String style
        single_quotes = 0
        double_quotes = 0
        
        for file_path in file_paths[:10]:  # Limit to 10 files for performance
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line in lines:
                    # Check indentation
                    if line.strip():
                        indent = len(line) - len(line.lstrip())
                        if indent > 0:
                            if line[0] == '\t':
                                tab_indent_count += 1
                            else:
                                space_indent_count += 1
                                indent_sizes[indent] += 1
                        
                        # Check line length
                        line_lengths.append(len(line.rstrip()))
                    
                # Check naming conventions
                content = ''.join(lines)
                snake_case_funcs = len(re.findall(r'def\s+([a-z][a-z0-9_]*)', content))
                camel_case_funcs = len(re.findall(r'def\s+([a-z][a-zA-Z0-9]*)', content))
                snake_case_count += snake_case_funcs
                camel_case_count += camel_case_funcs
                
                # Check string quotes
                single_quotes += len(re.findall(r'\'[^\']*\'', content))
                double_quotes += len(re.findall(r'\"[^\"]*\"', content))
                    
            except Exception as e:
                logger.warning(f"Error analyzing file {file_path}: {str(e)}")
        
        # Determine most common style
        style_info = {
            'indentation': 'tabs' if tab_indent_count > space_indent_count else 'spaces',
            'indent_size': indent_sizes.most_common(1)[0][0] if indent_sizes else 4,
            'line_length': int(sum(line_lengths) / len(line_lengths)) if line_lengths else 79,
            'naming_conventions': {
                'functions': 'snake_case' if snake_case_count > camel_case_count else 'camelCase'
            },
            'string_quotes': 'single' if single_quotes > double_quotes else 'double'
        }
        
        return style_info
    
    def _analyze_java_style(self, file_paths: List[str]) -> Dict[str, Any]:
        """Analyze Java code style."""
        # Simplified placeholder implementation
        return {
            'indentation': 'spaces',
            'indent_size': 4,
            'line_length': 100,
            'naming_conventions': {
                'classes': 'PascalCase',
                'methods': 'camelCase',
                'variables': 'camelCase'
            },
            'bracing_style': 'same_line'
        }
    
    def _analyze_c_style(self, file_paths: List[str]) -> Dict[str, Any]:
        """Analyze C/C#/C++ code style."""
        # Simplified placeholder implementation
        return {
            'indentation': 'spaces',
            'indent_size': 4,
            'line_length': 100,
            'naming_conventions': {
                'classes': 'PascalCase',
                'methods': 'PascalCase',
                'variables': 'camelCase'
            },
            'bracing_style': 'new_line'
        }