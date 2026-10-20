import json
import logging
import os
import time
from typing import Dict, List, Optional
import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)

class BedrockClient:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "ap-southeast-1")
        self.router_model = os.environ.get("BEDROCK_ROUTER_MODEL_ID", "amazon.nova-lite-v1:0")
        self.negotiator_model = os.environ.get("BEDROCK_NEGOTIATOR_MODEL_ID", "amazon.nova-pro-v1:0")
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                # boto3 automatically picks up AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN from env
                self._client = boto3.client("bedrock-runtime", region_name=self.region)
            except Exception as e:
                logger.warning(f"Bedrock client initialization warning: {e}")
        return self._client

    def invoke_converse(self, model_id: str, system_text: str, messages: List[dict], temperature: float = 0.2) -> dict:
        """
        Calls AWS Bedrock using the unified Converse API.
        Works seamlessly with Amazon Nova and Anthropic Claude models.
        """
        start_time = time.time()
        
        # Bedrock messages format
        bedrock_messages = []
        for m in messages:
            role = "assistant" if m.get("sender") == "agent" else "user"
            content = m.get("text", "")
            if content:
                bedrock_messages.append({
                    "role": role,
                    "content": [{"text": content}]
                })

        if not bedrock_messages:
            bedrock_messages = [{"role": "user", "content": [{"text": "สวัสดีครับ"}]}]

        if self.client:
            try:
                response = self.client.converse(
                    modelId=model_id,
                    system=[{"text": system_text}],
                    messages=bedrock_messages,
                    inferenceConfig={
                        "maxTokens": 1024,
                        "temperature": temperature
                    }
                )
                latency_ms = round((time.time() - start_time) * 1000, 1)
                output_message = response["output"]["message"]["content"][0]["text"]
                usage = response.get("usage", {})
                
                return {
                    "text": output_message,
                    "latency_ms": latency_ms,
                    "model_id": model_id,
                    "input_tokens": usage.get("inputTokens", 0),
                    "output_tokens": usage.get("outputTokens", 0),
                    "status": "live_aws"
                }
            except Exception as e:
                logger.warning(f"AWS Bedrock converse call failed ({e}). Falling back to deterministic local agent.")

        # Fallback return when AWS keys are not yet provided
        latency_ms = round((time.time() - start_time) * 1000, 1)
        return {
            "text": None,
            "latency_ms": latency_ms,
            "model_id": model_id,
            "status": "fallback"
        }

bedrock_client = BedrockClient()
