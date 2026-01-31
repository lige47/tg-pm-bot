FROM python:3.11-slim
WORKDIR /app
COPY . .
# 使用清华源加速下载
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# 必须带上 -u，确保日志实时输出
CMD ["python", "-u", "bot.py"]
