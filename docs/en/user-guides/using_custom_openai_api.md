# (Advanced) Connecting to a Custom OpenAI-Compatible API

This guide is for users with basic technical knowledge and aims to instruct you on how to use the application's generic interface to connect to **any AI service that is compatible with the OpenAI API standard**.

## Core Feature

We provide a generic interface named `your_favourite_api`. You can configure it to connect to any OAI-compatible service you wish to use, such as a new emerging AI platform, a friend's local server, or any other service not officially preset in the application.

**This feature relies entirely on you performing the configuration manually and correctly.**

---

## Configuration Process

### Step 1: Manually Set the API Key

You must manually set the API key for your service. The application will not guide you through this via `setup.bat`.

1.  Obtain the API key for the service you intend to use.
2.  **Manually in your operating system**, create an environment variable named `YOUR_FAVOURITE_API_KEY` and set your key as its value.

> **Warning**: If you do not know how to set an environment variable, please search for "How to set environment variables on Windows/macOS". This is a prerequisite for using this feature.

### Step 2: Configure the API URL and Model Name (Crucial!)

You must explicitly tell the application your service's API address (Base URL) and the name of the model you want to use in the configuration file.

1.  Open the file: `scripts/app_settings.py`.
2.  Find the `your_favourite_api` entry within the `API_PROVIDERS` dictionary.
3.  **Modify the values of the following two placeholders**:
    - `base_url`: Replace with your service's API address (e.g., `https://api.example.com/v1`).
    - `default_model`: Replace with the name of the model you want to use (e.g., `some-model-name-v1`).

**Example Modification:**
```python
# scripts/app_settings.py

"your_favourite_api": {
    "api_key_env": "YOUR_FAVOURITE_API_KEY",
    "base_url": "https://api.example.com/v1",  # <-- Replace with your API URL
    "default_model": "some-model-name-v1", # <-- Replace with your model name
    "description": "(Technical knowledge required) Connect to any custom OpenAI-compatible API service"
},
```

> **Warning**: If you do not modify these placeholders, the application will fail at runtime because it cannot find a valid address and model.

### Step 3: Launch the Program

After completing all the above configurations, you can now start the translation process.

1.  Run `run.bat`.
2.  When choosing an AI service, select `your_favourite_api`.
3.  Proceed with the normal workflow. The program will now use your custom service for translation.

---

## Troubleshooting

- **Authentication Error**: Your API key is incorrect. Check if the `YOUR_FAVOURITE_API_KEY` environment variable is set correctly.
- **Connection Error**: The `base_url` you entered in `app_settings.py` is incorrect, or the address is not accessible from your network.
- **404 Not Found (Model Not Found)**: The `default_model` name you entered in `app_settings.py` is incorrect or not available on your service. Please check the spelling and availability.
