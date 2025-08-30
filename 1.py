import http.server
import socketserver
from http import HTTPStatus
import subprocess
import os
import stat

PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        self.wfile.write(b'Hello World!')

if __name__ == '__main__':
    # 从环境变量中获取域名和密钥
    # 使用 os.getenv 是 os.environ.get 的一个常见替代方法
    domain = os.getenv("domain")
    secret = os.getenv("secret")

    # 必须提供环境变量
    if not domain or not secret:
        print("错误：请先设置 'domain' 和 'secret' 环境变量。")
        exit(1)

    # --- nezha-agent 启动逻辑 ---
    agent_path = "./agent"
    
    # 确保 agent 文件存在且有执行权限
    if not os.path.exists(agent_path):
        print(f"错误: Agent 文件 '{agent_path}' 不存在。")
        exit(1)

    os.chmod(agent_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)

    nezha_command = [
        agent_path,
        "-s", f"{domain}:5555",
        "-p", secret,
        "-d"
    ]
    
    # 启动 nezha-agent 并让它在一个新的会话中运行，从而与当前脚本完全分离
    # preexec_fn=os.setsid 是解决此类问题的关键
    try:
        subprocess.Popen(nezha_command, preexec_fn=os.setsid)
        print("nezha-agent 进程已启动。")
    except Exception as e:
        print(f"启动 nezha-agent 失败: {e}")
        exit(1)

    # --- HTTP 服务器启动逻辑 ---
    with socketserver.TCPServer(("", PORT), Handler, False) as httpd:
        print(f"HTTP 服务器已在端口 {PORT} 启动。")
        httpd.allow_reuse_address = True
        httpd.server_bind()
        httpd.server_activate()
        httpd.serve_forever()
