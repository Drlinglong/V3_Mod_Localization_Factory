# Using ModelScope and SiliconFlow

This guide will walk you through configuring and using ModelScope and SiliconFlow, two services that are compatible with the OpenAI API.

## Core Advantage: Freedom to Choose Your Model

Unlike service providers that call official APIs, the biggest advantage of ModelScope and SiliconFlow is that they offer a massive library of open-source large language models of various sizes and characteristics. You can "order from a menu," freely choosing the model that best suits your needs and budget for translation.

---

## Setup Process

### Step 1: Set Up Your API Key

This is the prerequisite for using any feature. You can easily set up the environment variables by running `setup.bat`.

1.  Run the `setup.bat` file located in the project's root directory.
2.  Follow the menu prompts to select `ModelScope` or `SiliconFlow`.
3.  As guided, paste the API key or Token you obtained from the respective platform.
    - **ModelScope**: The key is on the [AccessKey Management](https://modelscope.cn/my/my-accesstoken) page in your personal center.
    - **SiliconFlow**: The key can be found in your [account information](https://siliconflow.cn/).

`setup.bat` will automatically create and set the required environment variables for you (`MODELSCOPE_API_KEY` or `SILICONFLOW_API_KEY`).

### Step 2: Choose and Configure Your Model (Crucial!)

This is the most important step to leverage the power of these platforms. You need to manually specify which model you want to use.

1.  **Browse and Select a Model**:
    - Visit the [ModelScope Model Library](https://modelscope.cn/models) or the [SiliconFlow Model List](https://siliconflow.cn/pricing).
    - Find a model you like that supports conversation or instruction-following (usually with `Instruct` or `Chat` in its name). Copy its Model ID/Name.

2.  **Modify the Configuration File**:
    - Open the file: `scripts/app_settings.py`.
    - Locate the `modelscope` or `siliconflow` entry within the `API_PROVIDERS` dictionary.
    - Paste the Model ID you just copied as the value for the `default_model` field.

#### ModelScope Example (Modify with your chosen model)
```python
# scripts/app_settings.py
"modelscope": {
    "api_key_env": "MODELSCOPE_API_KEY",
    "base_url": "https://api-inference.modelscope.cn/v1/",
    "default_model": "deepseek-ai/DeepSeek-V3.2-Exp",  # <-- Change this to your chosen Model ID
    "description": "Use AI models via ModelScope"
},
```

#### SiliconFlow Example (Modify with your chosen model)
```python
# scripts/app_settings.py
"siliconflow": {
    "api_key_env": "SILICONFLOW_API_KEY",
    "base_url": "https://api.siliconflow.cn/v1",
    "default_model": "DeepSeek-R1", # <-- Change this to your chosen model name
    "description": "Use AI models via SiliconFlow"
},
```

### Step 3: Launch the Program

After completing all the configurations above, you can now start the translation process.

1.  Run `run.bat`.
2.  When choosing an AI service, select the `ModelScope` or `SiliconFlow` you just configured.
3.  Proceed with the normal workflow. The program will now use the model you specified for translation.

---

## Troubleshooting

- **Authentication Error**: Your API key is incorrect. Please run `setup.bat` again to set the correct key.
- **404 Not Found (Model Not Found)**: The `default_model` name you entered in `app_settings.py` is incorrect or not available on the platform. Please double-check the spelling.