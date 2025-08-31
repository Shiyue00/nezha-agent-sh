import http.server
import socketserver
from http import HTTPStatus
import subprocess
import os
import stat

# --- 配置区 ---
# 设置起始端口，脚本将从这个端口开始尝试
DEFAULT_PORT = 8080
# 设置最大尝试次数，以防无限循环
MAX_PORT_TRIES = 100

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        self.wfile.write(b'Hello World!')

def start_http_server(start_port):
    """
    尝试从 start_port 开始启动 HTTP 服务器，如果端口被占用则自动尝试下一个。
    """
    port = start_port
    for i in range(MAX_PORT_TRIES):
        current_port = port + i
        try:
            # 尝试创建并绑定服务器
            # 我们将 with 语句放在循环外，所以这里先手动创建对象
            httpd = socketserver.TCPServer(("", current_port), Handler, False)
            httpd.allow_reuse_address = True
            httpd.server_bind()
            
            # 如果绑定成功，打印信息并返回服务器实例
            print(f"成功在可用端口 {current_port} 上启动服务器。")
            return httpd
            
        except OSError:
            # 如果是 "Address already in use" 错误，则静默处理并尝试下一个
            print(f"端口 {current_port} 已被占用，正在尝试下一个...")
            continue # 继续循环，尝试下一个端口
            
    # 如果循环结束仍未找到可用端口
    return None


if __name__ == '__main__':
    # --- nezha-agent 启动逻辑 (保持不变) ---
    domain = os.environ.get("domain")
    secret = os.environ.get("secret")

    if not domain or not secret:
        print("错误：请设置 'domain' 和 'secret' 环境变量。")
        exit(1)

    agent_path = "./agent"
    if os.path.exists(agent_path):
        os.chmod(agent_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
        nezha_command = [
            agent_path,
            "-s", f"{domain}:5555",
            "-p", secret
            # "-d"
        ]
        subprocess.Popen(nezha_command)
    else:
        print(f"警告: '{agent_path}' 文件不存在，跳过启动 agent。")

    # --- HTTP 服务器启动逻辑 (使用新的函数) ---
    http_server = start_http_server(DEFAULT_PORT)

    if http_server:
        # 使用 with 语句来确保服务器资源被正确关闭
        with http_server:
            http_server.server_activate()
            http_server.serve_forever()
    else:
        print(f"错误：在尝试了 {MAX_PORT_TRIES} 次后，未能找到可用的端口。")
        exit(1)

