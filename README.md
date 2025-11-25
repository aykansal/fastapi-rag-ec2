# fastapi-rag-ec2

# Regular Start
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

# Start Local Runtime

## Jupyter

```bash
source venv/Scripts/activate
```

```bash
jupyter notebook \
  --NotebookApp.allow_origin='https://colab.research.google.com' \
  --port=8888 \
  --NotebookApp.port_retries=0 \
  --NotebookApp.allow_credentials=True
```

## Docker

### 1\. The Corrected `docker run` Command

**If using Git Bash (or a similar environment where the initial path failed):**

```bash
docker run -it -d \
  -p 127.0.0.1:9000:8080 \
  --name my_fastapi_app \
  --mount type=bind,source="/c/Users/ayver/Desktop/fastapi",target=/content \
  us-docker.pkg.dev/colab-images/public/runtime
```

*(Note: I added the `-d` flag to run the container in the background, which is generally better practice for running services.)*

-----

### 2\. Access the Container Shell

Execute this command to jump into the running container to start your service:

```bash
docker exec -it my_fastapi_app /bin/bash
```

-----

### 3\. Start the FastAPI Application

Once inside the container shell, use these commands to navigate to your mounted code and start the server:

```bash
cd /content

# Run Uvicorn, listening on all interfaces (0.0.0.0) and internal port 8080
uvicorn main:app --host 0.0.0.0 --port 8080
```

*(Replace `main:app` if your entry point is different.)*

Your application will then be accessible on your host machine at `http://127.0.0.1:9000`.

-----
