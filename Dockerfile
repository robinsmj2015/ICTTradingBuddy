# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all files into the container
COPY . .

# Install dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Expose port for Render
ENV PORT=8080
EXPOSE 8080

# Run your Streamlit app
CMD ["streamlit", "run", "StreamlitApp.py", "--server.port=8080", "--server.headless=true"]
