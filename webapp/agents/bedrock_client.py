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

# Defaults: Claude 3.5 Sonnet for the Thai negotiation voice, Nova Micro for the router.
DEFAULT_ROUTER_MODEL = "amazon.nova-micro-v1:0"
DEFAULT_NEGOTIATOR_MODEL = "amazon.nova-pro-v1:0"


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

    @property
    def client(self):
        if self._client is None:
            try:
                session = boto3.Session(region_name=self.region)
                if session.get_credentials() is not None:
                    self._client = session.client(
                        "bedrock-runtime", region_name=self.region, config=_BEDROCK_BOTO_CONFIG
                    )
            except Exception as e:
                logger.warning(f"Bedrock client initialization warning: {e}")
        return self._client

    def invoke_converse(self, model_id: str, system_text: str, messages: List[dict],
                        temperature: float = 0.2, max_tokens: int = 1024) -> dict:
        """
        Calls AWS Bedrock using the unified Converse API.
        Works seamlessly with Amazon Nova and Anthropic Claude models.
        """
        start_time = time.time()
        
        # Bedrock Converse API compliance:
        # 1. The first message MUST have role 'user'
        # 2. Roles must strictly alternate (user -> assistant -> user ...)
        raw_entries = []
        for m in messages:
            role = "assistant" if m.get("sender") in ("agent", "ai") else "user"
            content = (m.get("text") or "").strip()
            if content:
                raw_entries.append((role, content))

        if not raw_entries:
            raw_entries = [("user", "สวัสดีครับ ขอเปิดการเจรจาเงื่อนไขจัดซื้อ")]
        elif raw_entries[0][0] != "user":
            # Prepend an initial RFQ trigger prompt so Bedrock's first turn is 'user'
            raw_entries.insert(0, ("user", "ขอเปิดการเจรจาจัดซื้อสัญญารายปี LTA"))

        # Strictly alternate roles by concatenating consecutive turns from the same sender
        consolidated = []
        for role, content_text in raw_entries:
            if consolidated and consolidated[-1]["role"] == role:
                consolidated[-1]["content"][0]["text"] += f"\n\n{content_text}"
            else:
                consolidated.append({"role": role, "content": [{"text": content_text}]})

        bedrock_messages = consolidated

        if self.client:
            try:
                converse_kwargs = {
                    "modelId": model_id,
                    "system": [{"text": system_text}],
                    "messages": bedrock_messages,
                    "inferenceConfig": {
                        "maxTokens": max_tokens,
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
