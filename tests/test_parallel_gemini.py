import os
import concurrent.futures
from scripts.app_settings import load_api_keys_to_env
from scripts.core.gemini_handler import GeminiHandler

def test_parallel_calls():
    load_api_keys_to_env()
    handler = GeminiHandler(provider_name="gemini")
    
    # Manually patch model to preview
    original_get_config = handler.get_provider_config
    def mocked_get_config():
        conf = original_get_config()
        conf["default_model"] = "gemini-3-flash-preview"
        return conf
    handler.get_provider_config = mocked_get_config

    prompts = ["Hello 1", "Hello 2", "Hello 3", "Hello 4", "Hello 5"]
    
    print(f"🚀 Starting {len(prompts)} parallel calls...")
    
    def call_one(p):
        print(f"  -> Calling for: {p}")
        res = handler._call_api(handler.client, p)
        print(f"  <- Finished: {p}")
        return res

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(call_one, p): p for p in prompts}
        for future in concurrent.futures.as_completed(futures):
            p = futures[future]
            try:
                res = future.result()
                print(f"✅ Result for {p}: {res[:20]}...")
            except Exception as e:
                print(f"❌ Failed for {p}: {e}")

if __name__ == "__main__":
    test_parallel_calls()
