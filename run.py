from app.app import app

# If this is the main program, run the FastAPI application
if __name__ == "__main__":
    import uvicorn

    # Run the application on host "0.0.0.0" and port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)

    # test commit
