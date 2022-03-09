FROM python:3

# Install Python dependencies
WORKDIR /usr/app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy in Python source
COPY . ./

# Set runtime environment configuration
ENV RABBITMQ_EXCHANGE=""
ENV RABBITMQ_URI="amqp://guest:guest@localhost:5672/%2f"

CMD ["python", "./main.py"]

