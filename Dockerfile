# Step 1: Use a Python base image
FROM python:3.12-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create the productionfiles directory
RUN mkdir -p /app/productionfiles

# Step 4: Copy the rest of the Django project files
COPY . .

# Step 5: Run the collectstatic command to gather static files
RUN python manage.py collectstatic --noinput

# Step 6: Set environment variables for static files
ENV STATIC_URL='/static/'
ENV STATIC_ROOT='/app/staticfiles'

# Step 7: Expose the port Django will run on
EXPOSE 80

# Step 8: Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
