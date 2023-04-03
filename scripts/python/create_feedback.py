import sys
import requests
import os

issue_id = sys.argv[1]

org = "he3-app"
repo = "he3-feedback"
token = os.environ["GITHUB_TOKEN"]

github_headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github+json",
}

issue_url = f"https://api.github.com/repos/{org}/{repo}/issues/{issue_id}"
response = requests.get(issue_url, headers=github_headers)
issue_data = response.json()

title = issue_data["title"]
des = issue_data["body"]
labels = issue_data["labels"][0]["name"]

comments_url = issue_data["comments_url"]
response = requests.get(comments_url, headers=github_headers)
comments_data = response.json()

priority = ""
for comment in reversed(comments_data):
    if comment["user"]["login"] == "lyzhang1999":
        priority = comment["body"]
        break

priority = priority.upper()

if priority not in ["P0", "P1", "P2"]:
    print("忽略")
    sys.exit(0)

url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
json_body = {
    "app_id": os.environ["APP_ID"],
    "app_secret": os.environ["APP_SECRET"],
}
response = requests.post(url, json=json_body)
tenant_access_token = response.json()["tenant_access_token"]

url = "https://open.feishu.cn/open-apis/bitable/v1/apps/X7PcbzIWWaiD5csO5GUcTfpdnff/tables/tbl4KTElmyyThrMM/records"
headers = {
    "Authorization": f"Bearer {tenant_access_token}",
    "Content-Type": "application/json",
}
json_body = {
    "fields": {
        "标题": title,
        "内容": des,
        "优先级": priority,
        "状态": "待评估",
        "反馈类型": labels,
        "GitHub": f"https://github.com/{org}/{repo}/issues/{issue_id}",
        "Owner": [{"id": "ou_a22d5123cbfad181fd14e7d467e2c0f6"}],
    },
}
response = requests.post(url, headers=headers, json=json_body)

if response.status_code == 200:
    comment_url = f"https://api.github.com/repos/{org}/{repo}/issues/{issue_id}/comments"
    comment_body = f"感谢您的反馈，产品部门正在加紧处理，优先级为{priority}，请留意 issues 进度。"
    response = requests.post(comment_url, headers=github_headers, json={
                             "body": comment_body})
    if response.status_code == 201:
        print("创建任务成功，已添加评论")
    else:
        print("创建任务成功，添加评论失败")
else:
    print("创建任务失败")
