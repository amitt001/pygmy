FROM python:3.13-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN groupadd --gid 10001 pygmy && useradd --uid 10001 --gid pygmy --no-create-home pygmy
WORKDIR /pygmy
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=10001:10001 . .
RUN mkdir -p /var/log/pygmy /pygmy/pygmy/data && chown -R 10001:10001 /var/log/pygmy /pygmy/pygmy/data
USER 10001:10001
EXPOSE 8000
CMD ["python3", "run.py"]
