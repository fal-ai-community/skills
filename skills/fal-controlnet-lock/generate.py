import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv
import fal_client

load_dotenv()

# --- Configuration ---
FAL_KEY = os.getenv("FAL_KEY")
IP_ADAPTER_PATH = os.getenv("IP_ADAPTER_PATH")
IP_ENCODER_PATH = os.getenv("IP_ENCODER_PATH")
IP_ADAPTER_SCALE = float(os.getenv("IP_ADAPTER_SCALE", "0.7"))
CONTROLNET_SCALE = float(os.getenv("CONTROLNET_SCALE", "0.7"))
CONTROL_MODE = os.getenv("CONTROL_MODE", "depth")


def validate_config():
    missing = []
    if not FAL_KEY:
        missing.append("FAL_KEY")
    if not IP_ADAPTER_PATH:
        missing.append("IP_ADAPTER_PATH")
    if not IP_ENCODER_PATH:
        missing.append("IP_ENCODER_PATH")
    if missing:
        raise ValueError(f"Missing required .env variables: {', '.join(missing)}")


def upload(path: str) -> str:
    print(f"Uploading {path} ...")
    url = fal_client.upload_file(path)
    print(f"  → {url}")
    return url


def save_image(image_url: str, output_path: str):
    response = requests.get(image_url, timeout=60)
    response.raise_for_status()
    Path(output_path).write_bytes(response.content)
    print(f"Saved → {output_path}")


def generate(comp_ref: str, char_ref: str, prompt: str, output: str = "output.png"):
    validate_config()

    os.environ["FAL_KEY"] = FAL_KEY

    comp_ref_url = upload(comp_ref)
    char_ref_url = upload(char_ref)

    arguments = {
        "prompt": prompt,
        "controlnet_unions": [
            {
                "path": "Shakker-Labs/FLUX.1-dev-ControlNet-Union-Pro",
                "controls": [
                    {
                        "control_image_url": comp_ref_url,
                        "control_mode": CONTROL_MODE,  # string enum: "depth", "canny", etc.
                        "conditioning_scale": CONTROLNET_SCALE,
                    }
                ],
            }
        ],
        "ip_adapters": [
            {
                "path": IP_ADAPTER_PATH,
                "image_encoder_path": IP_ENCODER_PATH,
                "image_url": char_ref_url,
                "scale": IP_ADAPTER_SCALE,
            }
        ],
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
        "image_size": {"width": 1024, "height": 1024},
    }

    print("Calling fal-ai/flux-general ...")
    result = fal_client.subscribe("fal-ai/flux-general", arguments=arguments)

    image_url = result["images"][0]["url"]
    save_image(image_url, output)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python generate.py <comp_ref> <char_ref> <prompt> [output.png]")
        sys.exit(1)

    comp_ref_arg = sys.argv[1]
    char_ref_arg = sys.argv[2]
    prompt_arg = sys.argv[3]
    output_arg = sys.argv[4] if len(sys.argv) > 4 else "output.png"

    generate(comp_ref_arg, char_ref_arg, prompt_arg, output_arg)
