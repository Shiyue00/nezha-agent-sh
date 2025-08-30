import http.server
import socketserver
import os
import subprocess

# --- 配置 ---
# agent 文件名
AGENT_FILE = "agent"
# agent 命令参数
AGENT_COMMAND = ["./" + AGENT_FILE, "-s", "tzz.shiyue.eu.org:5555", "-p", "6N6q7Zn7AtWfWWxSmW", "-d"]
# HTTP 服务器端口
HTTP_PORT = 8080

def run_agent_in_background():
    """
    使 agent 文件可执行并在后台运行它。
    """
    try:
        # 赋予 agent 文件可执行权限
        os.chmod(AGENT_FILE, 0o755)
        print(f"已为 '{AGENT_FILE}' 文件添加可执行权限。")

        # 在后台运行 agent 命令
        print(f"在后台运行命令: {' '.join(AGENT_COMMAND)}")
        subprocess.Popen(AGENT_COMMAND, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"'{AGENT_FILE}' 正在后台运行。")

    except FileNotFoundError:
        print(f"错误: '{AGENT_FILE}' 文件未在当前目录中找到。")
    except Exception as e:
        print(f"运行 agent 时发生错误: {e}")

def start_http_server():
    """
    启动一个简单的 HTTP 服务器。
    """
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", HTTP_PORT), Handler) as httpd:
        print(f"HTTP 服务器正在监听端口: {HTTP_PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_agent_in_background()
    start_http_server()
