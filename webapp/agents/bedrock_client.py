import logging
import os
import time
from typing import List

import boto3
from botocore.config import Config

logger = logging.getLogger(__name__)

# Bound AWS latency so a slow network never stalls a live negotiation turn:
# fail fast and let the deterministic fallback take over.
_BEDROCK_BOTO_CONFIG = Config(
    connect_timeout=4,
    read_timeout=20,
    retries={"max_attempts": 2, "mode": "standard"},
)

# Defaults: Claude 3.5 Sonnet for the Thai negotiation voice, Nova Lite for the router.
DEFAULT_ROUTER_MODEL = "amazon.nova-lite-v1:0"
DEFAULT_NEGOTIATOR_MODEL = "anthropic.claude-3-5-sonnet-20240620-v1:0"


def _env_any(keys: List[str], default: str) -> str:
    """Return the first non-empty environment value among keys, else default."""
    for key in keys:
        val = os.environ.get(key)
        if val:
            return val
    return default


class BedrockClient:
    def __init__(self):
        # Accept both AWS_REGION and AWS_DEFAULT_REGION for flexibility.
        self.region = _env_any(["AWS_REGION", "AWS_DEFAULT_REGION"], "us-east-1")
        # Optional inline guardrail applied during Converse (filters input+output).
        self.guardrail_id = os.environ.get("BEDROCK_GUARDRAIL_ID", "").strip()
        self.guardrail_version = os.environ.get("BEDROCK_GUARDRAIL_VERSION", "DRAFT").strip()
        # Accept both the _ID suffixed names and the plain names used in .env.example.
        self.router_model = _env_any(
            ["BEDROCK_ROUTER_MODEL_ID", "BEDROCK_ROUTER_MODEL"], DEFAULT_ROUTER_MODEL
        )
        self.negotiator_model = _env_any(
            ["BEDROCK_NEGOTIATOR_MODEL_ID", "BEDROCK_NEGOTIATOR_MODEL"], DEFAULT_NEGOTIATOR_MODEL
        )
        self._client = None
        self._credentials_present = bool(
            os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY")
        ) or bool(os.environ.get("AWS_PROFILE"))

    @property
    def client(self):
        # When no AWS credentials are configured, stay in deterministic fallback mode
        # instead of creating a client that will fail on every call (keeps demo fast + stable).
        if not self._credentials_present:
            return None
        if self._client is None:
            try:
                # boto3 picks up AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_SESSION_TOKEN from env.
                self._client = boto3.client(
                    "bedrock-runtime", region_name=self.region, config=_BEDROCK_BOTO_CONFIG
                )
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
                converse_kwargs = {
                    "modelId": model_id,
                    "system": [{"text": system_text}],
                    "messages": bedrock_messages,
                    "inferenceConfig": {
                        "maxTokens": 1024,
                        "temperature": temperature,
                    },
                }
                # Inline Amazon Bedrock Guardrail: filters both the input and the
                # model output during inference (defense-in-depth with the
                # standalone ApplyGuardrail check in ComplianceGuardrailAgent).
                if self.guardrail_id:
                    converse_kwargs["guardrailConfig"] = {
                        "guardrailIdentifier": self.guardrail_id,
                        "guardrailVersion": self.guardrail_version,
                    }

                response = self.client.converse(**converse_kwargs)
                latency_ms = round((time.time() - start_time) * 1000, 1)
                output_message = response["output"]["message"]["content"][0]["text"]
                usage = response.get("usage", {})

                return {
                    "text": output_message,
                    "latency_ms": latency_ms,
                    "model_id": model_id,
                    "input_tokens": usage.get("inputTokens", 0),
                    "output_tokens": usage.get("outputTokens", 0),
                    "status": "live_aws",
                    "stop_reason": response.get("stopReason"),
                    "guardrail_applied": bool(self.guardrail_id),
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
