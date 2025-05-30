import os
import re
import math
from typing import Dict, List

class CodeAnalyzer:
    def __init__(self):
        self.supported_languages = ['python', 'javascript', 'java', 'go', 'typescript']
    
    def detect_language(self, filename: str) -> str:
        """Detect programming language from filename"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go'
        }
        ext = os.path.splitext(filename.lower())[1]
        return ext_map.get(ext, 'unknown')
    
    def analyze_code(self, filename: str, code_content: str) -> Dict:
        """Main analysis function"""
        try:
            language = self.detect_language(filename)
            
            
            stats = self._get_basic_stats(code_content, language)
            
            
            structure = self._extract_structure(code_content, language)
            
            
            stats['functions_count'] = len(structure['functions'])
            stats['classes_count'] = len(structure['classes'])
            
            
            complexity = self._calculate_complexity(code_content, language)
            
            return {
                'filename': filename,
                'language': language,
                'stats': stats,
                'structure': structure,
                'complexity': complexity,
                'success': True,
                'error_message': ''
            }
            
        except Exception as e:
            print(f"Analysis error: {e}")
            return {
                'filename': filename,
                'language': 'unknown',
                'stats': self._empty_stats(),
                'structure': {'functions': [], 'classes': [], 'imports': []},
                'complexity': {'cyclomatic_complexity': 0, 'nesting_depth': 0, 'maintainability_index': 0.0},
                'success': False,
                'error_message': str(e)
            }
    
    def _get_basic_stats(self, code: str, language: str) -> Dict:
        """Calculate basic code statistics"""
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        
        comment_patterns = {
            'python': r'^\s*#',
            'javascript': r'^\s*(//)|(^\s*/\*)',
            'typescript': r'^\s*(//)|(^\s*/\*)',
            'java': r'^\s*(//)|(^\s*/\*)',
            'go': r'^\s*(//)|(^\s*/\*)'
        }
        
        pattern = comment_patterns.get(language, r'^\s*#')
        comment_lines = [line for line in lines if re.match(pattern, line)]
        
        return {
            'total_lines': len(lines),
            'non_empty_lines': len(non_empty_lines),
            'comment_lines': len(comment_lines),
            'characters': len(code),
            'functions_count': 0,  
            'classes_count': 0     
        }
    
    def _extract_structure(self, code: str, language: str) -> Dict:
        """Extract code structure based on language"""
        if language == 'python':
            return self._extract_python_structure(code)
        elif language in ['javascript', 'typescript']:
            return self._extract_js_structure(code)
        elif language == 'java':
            return self._extract_java_structure(code)
        elif language == 'go':
            return self._extract_go_structure(code)
        else:
            return {'functions': [], 'classes': [], 'imports': []}
    
    def _extract_python_structure(self, code: str) -> Dict:
        """Extract Python code structure"""
        functions = []
        classes = []
        imports = []
        
        lines = code.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            
           
            func_match = re.match(r'def\s+(\w+)\s*\((.*?)\):', stripped)
            if func_match:
                functions.append({
                    'name': func_match.group(1),
                    'parameters': func_match.group(2),
                    'line_number': i + 1,
                    'docstring': '',
                    'type': 'function'
                })
            
            
            class_match = re.match(r'class\s+(\w+)(?:\([^)]*\))?:', stripped)
            if class_match:
                classes.append({
                    'name': class_match.group(1),
                    'line_number': i + 1,
                    'methods': [],
                    'docstring': ''
                })
            
           
            import_match = re.match(r'(?:from\s+(\S+)\s+)?import\s+(.+)', stripped)
            if import_match:
                if import_match.group(1): 
                    module = f"{import_match.group(1)}.{import_match.group(2).split(',')[0].strip()}"
                else:  
                    module = import_match.group(2).split(',')[0].strip()
                
                imports.append({
                    'module': module,
                    'line_number': i + 1,
                    'alias': ''
                })
        
        return {'functions': functions, 'classes': classes, 'imports': imports}
    
    def _extract_js_structure(self, code: str) -> Dict:
        """Extract JavaScript/TypeScript structure"""
        functions = []
        classes = []
        imports = []
        
        lines = code.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            
          
            patterns = [
                r'function\s+(\w+)\s*\((.*?)\)',
                r'(?:const|let|var)\s+(\w+)\s*=\s*\((.*?)\)\s*=>',
                r'(?:const|let|var)\s+(\w+)\s*=\s*function\s*\((.*?)\)',
                r'(\w+)\s*:\s*\((.*?)\)\s*=>'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, stripped)
                if match:
                    functions.append({
                        'name': match.group(1),
                        'parameters': match.group(2),
                        'line_number': i + 1,
                        'docstring': '',
                        'type': 'function'
                    })
                    break
            
            
            class_match = re.match(r'class\s+(\w+)', stripped)
            if class_match:
                classes.append({
                    'name': class_match.group(1),
                    'line_number': i + 1,
                    'methods': [],
                    'docstring': ''
                })
            
            
            import_patterns = [
                r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
                r'import\s+[\'"]([^\'"]+)[\'"]'
            ]
            
            for pattern in import_patterns:
                match = re.search(pattern, stripped)
                if match:
                    imports.append({
                        'module': match.group(1),
                        'line_number': i + 1,
                        'alias': ''
                    })
                    break
        
        return {'functions': functions, 'classes': classes, 'imports': imports}
    
    def _extract_java_structure(self, code: str) -> Dict:
        """Extract Java structure"""
        functions = []
        classes = []
        imports = []
        
        lines = code.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            
            method_match = re.search(r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\((.*?)\)', stripped)
            if method_match and not 'class' in stripped and not 'interface' in stripped:
                functions.append({
                    'name': method_match.group(1),
                    'parameters': method_match.group(2),
                    'line_number': i + 1,
                    'docstring': '',
                    'type': 'method'
                })
            
           
            class_match = re.match(r'(?:public|private)?\s*class\s+(\w+)', stripped)
            if class_match:
                classes.append({
                    'name': class_match.group(1),
                    'line_number': i + 1,
                    'methods': [],
                    'docstring': ''
                })
            
       
            import_match = re.match(r'import\s+([^;]+);', stripped)
            if import_match:
                imports.append({
                    'module': import_match.group(1),
                    'line_number': i + 1,
                    'alias': ''
                })
        
        return {'functions': functions, 'classes': classes, 'imports': imports}
    
    def _extract_go_structure(self, code: str) -> Dict:
        """Extract Go structure"""
        functions = []
        classes = []
        imports = []
        
        lines = code.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            
            func_match = re.match(r'func\s+(?:\([^)]*\)\s*)?(\w+)\s*\((.*?)\)', stripped)
            if func_match:
                functions.append({
                    'name': func_match.group(1),
                    'parameters': func_match.group(2),
                    'line_number': i + 1,
                    'docstring': '',
                    'type': 'function'
                })
            
          
            struct_match = re.match(r'type\s+(\w+)\s+struct', stripped)
            if struct_match:
                classes.append({
                    'name': struct_match.group(1),
                    'line_number': i + 1,
                    'methods': [],
                    'docstring': ''
                })
            
          
            import_match = re.match(r'import\s+(?:"([^"]+)"|(\w+)\s+"([^"]+)")', stripped)
            if import_match:
                module = import_match.group(1) or import_match.group(3)
                alias = import_match.group(2) or ''
                imports.append({
                    'module': module,
                    'line_number': i + 1,
                    'alias': alias
                })
        
        return {'functions': functions, 'classes': classes, 'imports': imports}
    
    def _calculate_complexity(self, code: str, language: str) -> Dict:
        """Calculate complexity metrics"""
        lines = code.split('\n')
        
       
        complexity_keywords = {
            'python': ['if', 'elif', 'for', 'while', 'try', 'except', 'with'],
            'javascript': ['if', 'for', 'while', 'try', 'catch', 'switch'],
            'typescript': ['if', 'for', 'while', 'try', 'catch', 'switch'],
            'java': ['if', 'for', 'while', 'try', 'catch', 'switch'],
            'go': ['if', 'for', 'switch', 'select']
        }
        
        keywords = complexity_keywords.get(language, ['if', 'for', 'while'])
        cyclomatic = 1 
        
        for line in lines:
            for keyword in keywords:
                if f' {keyword} ' in f' {line} ' or line.strip().startswith(keyword + ' '):
                    cyclomatic += 1
        
       
        max_depth = self._calculate_nesting_depth(code, language)
        
       
        loc = len([line for line in lines if line.strip()])
        maintainability = max(0, 100 - cyclomatic * 2 - max_depth * 5)
        
        return {
            'cyclomatic_complexity': min(cyclomatic, 50),
            'nesting_depth': max_depth,
            'maintainability_index': float(maintainability)
        }
    
    def _calculate_nesting_depth(self, code: str, language: str) -> int:
        """Calculate maximum nesting depth"""
        lines = code.split('\n')
        max_depth = 0
        
        if language == 'python':
            for line in lines:
                if line.strip():
                    indent_level = (len(line) - len(line.lstrip())) // 4
                    max_depth = max(max_depth, indent_level)
        else:
            current_depth = 0
            for line in lines:
                current_depth += line.count('{') - line.count('}')
                max_depth = max(max_depth, current_depth)
        
        return max_depth
    
    def _empty_stats(self) -> Dict:
        """Return empty stats structure"""
        return {
            'total_lines': 0,
            'non_empty_lines': 0,
            'comment_lines': 0,
            'characters': 0,
            'functions_count': 0,
            'classes_count': 0
        }