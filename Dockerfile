# Use an official Python runtime as a parent image

# note: this doesnt really work yet

# Use an official Python runtime as a parent image
FROM python:3.9-slim

WORKDIR /app

COPY . /app

WORKDIR /app/Code


RUN pip install --no-cache-dir -r ../requirements.txt

EXPOSE 80

ENV NAME World

CMD ["python", "app.py"]
