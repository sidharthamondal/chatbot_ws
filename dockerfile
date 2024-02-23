# Use the official Python image
FROM python:3.10.12

# Set the working directory to /app
WORKDIR /app

# Copy only the dependency files to leverage Docker cache
COPY requirements.txt  /app/

# Install project dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install 'uvicorn[standard]'
# Copy the rest of the application code
COPY . /app

# Remove packages specified in remove.txt
# RUN cat remove.txt | xargs pip uninstall -y

EXPOSE 5000
# Install cron
RUN apt-get update && apt-get install -y cron

# Add cron job to run redisbackup.py every 30 minutes
RUN echo "*/30 * * * * /usr/local/bin/python /app/redisbackup.py" >> /etc/crontab

# Run main.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]