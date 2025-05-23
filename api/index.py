import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel需要这个handler函数
def handler(request):
    return app(request.environ, start_response)

# 也可以直接导出app
if __name__ == "__main__":
    app.run() 