import http.server
import socketserver
from http import HTTPStatus
import subprocess
import os
import stat

# 优先从环境变量'port'中获取端口号，如果不存在，则默认使用8080
# os.environ.get返回的是字符串，需要用int()转换为整数
PORT = int(os.environ.get('port', 8080))

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        self.wfile.write(b'Hello World!')

if __name__ == '__main__':
    # 从环境变量中获取域名和密钥
    domain = os.environ.get("domain")
    secret = os.environ.get("secret")

    # 检查环境变量是否存在
    if not domain or not secret:
        print("错误：请设置 'domain' 和 'secret' 环境变量。")
        exit(1)

    # 添加可执行权限
    agent_path = "./agent"
    # 检查 agent 文件是否存在
    if os.path.exists(agent_path):
        os.chmod(agent_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |  # 用户可读写执行
                   stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP |  # 组可读写执行
                   stat.S_IROTH | stat.S_IXOTH)  # 其他可读执行

        # 启动 nezha-agent 并让它在后台运行
        nezha_command = [
            agent_path,
            "-s", f"{domain}:5555",  # 使用环境变量构建参数
            "-p", secret,             # 使用环境变量
            "-d"
        ]
        subprocess.Popen(nezha_command)
    else:
        print(f"警告: '{agent_path}' 文件不存在，跳过启动 agent。")

    # 启动 HTTP 服务器
    with socketserver.TCPServer(("", PORT), Handler, False) as httpd:
        print(f"Server started at port {PORT}") # 使用 f-string 输出当前使用的端口
        httpd.allow_reuse_address = True
        httpd.server_bind()
        httpd.server_activate()
        httpd.serve_forever()
