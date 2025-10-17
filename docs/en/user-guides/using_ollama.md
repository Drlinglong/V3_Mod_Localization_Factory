# Using Ollama for Localization

This guide will walk you through setting up and using [Ollama](https://ollama.com/) to run a local Large Language Model (LLM) for translation within the "Paradox Mod Localization Factory."

## Why Choose Ollama?

- **Privacy & Security**: All translations are processed on your local machine, ensuring the privacy of your source code and content.
- **Offline Capability**: Once a model is downloaded, you can perform translations without an internet connection.
- **Cost-Effective**: There are no API call fees when using local models.
- **Highly Customizable**: You can select and run a wide variety of open-source models optimized for specific tasks.

## Setup Steps

### 1. Install Ollama

First, you need to install Ollama on your computer.

- Visit the [official Ollama website](https://ollama.com/).
- Download and install the appropriate application for your operating system (Windows, macOS, or Linux).
- The installer will automatically set up Ollama as a background service.

### 2. Download a Capable Language Model

After installing Ollama, you need to download a language model. The model's ability to follow complex instructions is **critical**. This application requires the model to return translations in a strict JSON format. Many smaller or chat-focused models may fail to do this, resulting in errors.

- **Recommended Model**: We strongly recommend starting with a powerful, instruction-following model like `llama3`.
  ```bash
  ollama pull llama3
  ```
- **Warning About Model Choice**: If you choose another model family (e.g., `qwen`), ensure you use a larger, more capable version (e.g., `qwen:7b`, not `qwen:4b`). Using a model that is not powerful enough is the most common cause of errors.

You can see a list of all your downloaded models by running `ollama list`.

### 3. Configure the Model in the Application

The application needs to be told exactly which Ollama model to use. You must configure this manually in the settings file.

1.  Open the file: `scripts/app_settings.py`.
2.  Find the `API_PROVIDERS` dictionary.
3.  Inside the `ollama` section, change the `default_model` value to the exact name of the model you downloaded.

**Example:**
```python
# scripts/app_settings.py

API_PROVIDERS = {
    # ... other providers
    "ollama": {
        "base_url_env": "OLLAMA_BASE_URL",
        "default_model": "llama3:latest",  # <-- Change this value
        "enable_thinking": False,
        "description": "Local Ollama models, no API key required"
    },
}
```

### 4. Troubleshooting

#### Error: Connection Failed or `404 Not Found`

This error means the application cannot reach your Ollama service.
- **Is Ollama running?** Make sure the Ollama application is running on your machine.
- **Is the address correct?** The application defaults to `http://localhost:11434`. If you run Ollama on a different address, you must set the `OLLAMA_BASE_URL` environment variable as described in the "Advanced" section below.
- **Is a firewall or proxy interfering?** Check your system's firewall or proxy settings to ensure they are not blocking the connection from the Python application.

#### Error: `Pydantic validation failed` or `Invalid JSON`

This is the most common issue and almost always means **your chosen model is not capable enough.**

- **Explanation**: The application sends a complex prompt that instructs the model to return a perfectly formatted JSON array. This error means the model failed to follow these instructions and returned plain text or malformed data instead.
- **Solution**: You **must** switch to a more powerful model.
    - Edit `scripts/app_settings.py` and change `default_model` to a more capable model you have downloaded, such as `llama3`.
    - If you are using a model family like `qwen` or `mistral`, try a version with more parameters (e.g., `7b` instead of `1b` or `4b`).

### 5. (Advanced) Custom Ollama Service Address

If your Ollama service is running on a different IP address or port (e.g., on another machine in your local network), you can specify the connection address by setting an environment variable.

- Set an environment variable named `OLLAMA_BASE_URL`.
- Set its value to the full URL of your Ollama service.

**Examples:**

- On Windows:
  ```cmd
  set OLLAMA_BASE_URL=http://192.168.1.100:11434
  ```
- On macOS or Linux:
  ```bash
  export OLLAMA_BASE_URL=http://192.168.1.100:11434
  ```

After setting the variable, restart the application, and it will automatically use the new address you specified.

---

You are now ready to use Ollama for secure and efficient local Mod localization!