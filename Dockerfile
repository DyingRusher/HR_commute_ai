# Dockerfile

# --- Base Image ---
# Use an official Python runtime as a parent image.
# Using a specific version is good practice for reproducibility.
FROM python:3.11-slim

# --- Set up the Working Directory ---
# Create a directory inside the container for our app code.
WORKDIR /app

# --- Install Dependencies ---
# First, copy only the requirements file to leverage Docker's layer caching.
# This step will only be re-run if requirements.txt changes.
COPY requirements.txt .
RUN pip install -r requirements.txt

# --- Copy Application Code ---
# Copy the rest of the application files into the working directory.
COPY . .

# --- Expose Port ---
# Inform Docker that the container will listen on port 8501 (the default Streamlit port).
EXPOSE 8501

# --- Healthcheck (Optional but Recommended) ---
# This tells Docker how to check if your application is still running correctly.
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# --- Command to Run the Application ---
# The command that will be executed when the container starts.
# We use an array form for best practices.
CMD ["streamlit", "run", "main.py"]