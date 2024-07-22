import json

# 假设你的 JSON 数据是存储在一个变量中
message = '{"readme_content":"# CVE-2023-44487\\nBasic vulnerability scanning to see if web servers may be vulnerable to CVE-2023-44487\\n\\nThis tool checks to see if a website is vulnerable to CVE-2023-44487 completely non-invasively.\\n\\n1. The tool checks if a web server accepts HTTP/2 requests without downgrading them\\n2. If the web server accepts and does not downgrade HTTP/2 requests the tool attempts to open a connection stream and subsequently reset it\\n3. If the web server accepts the creation and resetting of a connection stream then the server is definitely vulnerable, if it only accepts HTTP/2 requests but the stream connection fails it may be vulnerable if the server-side capabilities are enabled.\\n\\nTo run,\\n\\n    $ python3 -m pip install -r requirements.txt\\n\\n    $ python3 cve202344487.py -i input_urls.txt -o output_results.csv\\n\\nYou can also specify an HTTP proxy to proxy all the requests through with the `--proxy` flag\\n\\n    $ python3 cve202344487.py -i input_urls.txt -o output_results.csv --proxy http://proxysite.com:1234\\n\\nThe script outputs a CSV file with the following columns\\n\\n- Timestamp: a timestamp of the request\\n- Source Internal IP: The internal IP address of the host sending the HTTP requests\\n- Source External IP: The external IP address of the host sending the HTTP requests\\n- URL: The URL being scanned\\n- Vulnerability Status: \\"VULNERABLE\\"/\\"LIKELY\\"/\\"POSSIBLE\\"/\\"SAFE\\"/\\"ERROR\\"\\n- Error/Downgrade Version: The error or the version the HTTP server downgrades the request to\\n\\n*Note: \\"Vulnerable\\" in this context means that it is confirmed that an attacker can reset the a stream connection without issue, it does not take into account implementation-specific or volume-based detections*","repository_sketch":"{\\"parsed_response\\": \\".\\\\n├── cve202344487.py # import utils; import scanner\\\\n├── utils.py # import csv; import os\\\\n├── scanner.py # import requests; import utils\\\\n├── requirements.txt\\\\n└── README.md\\\\n\\", \\"repo_sketch_paths\\": [\\"cve202344487.py\\", \\"utils.py\\", \\"scanner.py\\", \\"requirements.txt\\", \\"README.md\\"]}","file_path":"cve202344487.py"}'

# 解析 JSON 数据
data = json.loads(message)

# 访问解析后的数据
readme_content = data.get("readme_content")
repository_sketch = data.get("repository_sketch")
file_path = data.get("file_path")

# 打印信息
print("Readme Content:")
print(readme_content)
print("\nRepository Sketch:")
print(repository_sketch)
print("\nFile Path:")
print(file_path)