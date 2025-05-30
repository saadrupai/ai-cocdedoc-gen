import grpc
from concurrent import futures
import time
import os
from dotenv import load_dotenv
from analyzer import CodeAnalyzer


load_dotenv()


class AnalyzeRequest:
    def __init__(self, filename="", code_content="", language=""):
        self.filename = filename
        self.code_content = code_content
        self.language = language

class AnalyzeResponse:
    def __init__(self, **kwargs):
        self.filename = kwargs.get('filename', '')
        self.language = kwargs.get('language', '')
        self.stats = kwargs.get('stats', {})
        self.structure = kwargs.get('structure', {})
        self.complexity = kwargs.get('complexity', {})
        self.success = kwargs.get('success', True)
        self.error_message = kwargs.get('error_message', '')

class CodeAnalyzerService:
    def __init__(self):
        self.analyzer = CodeAnalyzer()
        print("🔍 Code Analyzer Service initialized")
    
    def AnalyzeCode(self, request, context):
        """Handle code analysis requests"""
        try:
            print(f"📝 Analyzing {request.filename} ({self.analyzer.detect_language(request.filename)})")
            
    
            result = self.analyzer.analyze_code(request.filename, request.code_content)
            
            print(f"✅ Analysis complete: {len(result['structure']['functions'])} functions, {len(result['structure']['classes'])} classes found")
            

            return AnalyzeResponse(**result)
            
        except Exception as e:
            print(f"❌ Error analyzing code: {str(e)}")
            return AnalyzeResponse(
                filename=request.filename,
                success=False,
                error_message=str(e)
            )
    
    def GetSupportedLanguages(self, request, context):
        """Return supported languages"""
        return {
            'languages': self.analyzer.supported_languages
        }

def serve():
    """Start the gRPC server"""
    port = os.getenv('GRPC_PORT', '50051')
    

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    

    servicer = CodeAnalyzerService()
    
    print(f"🚀 Code Analysis Service starting on port {port}...")
    print("📊 Supported languages:", servicer.analyzer.supported_languages)
    

    server.add_insecure_port(f'[::]:{port}')
    

    server.start()
    print(f"✅ Code Analysis Service is running on port {port}!")
    print("🔧 Ready to analyze code files...")
    
    try:
        while True:
            time.sleep(86400) 
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Code Analysis Service...")
        server.stop(0)

if __name__ == '__main__':
    serve()