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

### 2. Download a Language Model

After installing Ollama, you need to download a language model for translation. We recommend using a versatile and high-performance model, such as `llama3` or `qwen`.

Open your terminal (Command Prompt or PowerShell on Windows) and run the following command:

```bash
ollama pull llama3
```

Alternatively, if you wish to use another model like Qwen:

```bash
ollama pull qwen
```

The model download may take some time, depending on your network speed and the model's size. You can see a list of all your downloaded models by running the `ollama list` command.

### 3. Configure Ollama in the Application

The application is pre-configured to connect to a local Ollama service.

- **Default Address**: The program defaults to connecting to `http://localhost:11434`. For most standard Ollama installations, no extra configuration is needed.
- **Model Selection**: In the translation settings of the application, select **Ollama** from the "Translation Provider" dropdown menu. The program will automatically load the list of models you have downloaded, allowing you to choose one for translation.

### 4. (Advanced) Custom Ollama Service Address

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