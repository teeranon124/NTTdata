"""
Dynamic Model Gateway.

Routes each LLM task to the most cost/latency-appropriate model based on task
complexity, then invokes it through the shared Bedrock Converse client.

Routing policy (Mentor spec — Cost & Latency Optimization):
  - LIGHT tasks (intent parsing, classification, validation) -> fast tier
    (Amazon Nova Lite / Claude 3.5 Haiku)
  - HEAVY tasks (strategic negotiation, persuasion, game theory) -> strong tier
    (Claude 3.5 Sonnet / Nova Pro)

The gateway is the single choke point for model selection, so swapping models
or tuning the routing heuristic never touches agent business logic. It always
returns a normalized result dict (text, model_id, latency_ms, tokens, status,
task_type, tier) and degrades to a deterministic fallback when AWS is absent.
"""
import logging
import os
from enum import Enum
from typing import List, Optional

from .bedrock_client import bedrock_client

logger = logging.getLogger(__name__)


class TaskComplexity(str, Enum):
    LIGHT = "light"
    HEAVY = "heavy"


def _env_any(keys: List[str], default: str) -> str:
    for key in keys:
        val = os.environ.get(key)
        if val:
            return val
    return default


class ModelGateway:
    """Selects and invokes the right model tier for a given task."""

    def __init__(self):
        # Fast tier: default to the configured router model (Nova Lite), allow override.
        self.fast_model = _env_any(
            ["BEDROCK_FAST_MODEL_ID", "BEDROCK_ROUTER_MODEL_ID", "BEDROCK_ROUTER_MODEL"],
            bedrock_client.router_model,
        )
        # Strong tier: default to the configured negotiator model (Claude 3.5 Sonnet).
        self.strong_model = _env_any(
            ["BEDROCK_STRONG_MODEL_ID", "BEDROCK_NEGOTIATOR_MODEL_ID", "BEDROCK_NEGOTIATOR_MODEL"],
            bedrock_client.negotiator_model,
        )

    # -- Routing heuristic -------------------------------------------------
    def classify(self, task_type: str, text: str = "", hint: Optional[TaskComplexity] = None) -> TaskComplexity:
        """
        Decide the complexity tier for a task.
        An explicit hint always wins; otherwise use task type + message length.
        """
        if hint is not None:
            return hint

        light_tasks = {"intent", "parse", "classify", "validate", "extract", "route"}
        heavy_tasks = {"negotiate", "strategy", "persuasion", "synthesis", "arbitrate"}

        t = (task_type or "").lower()
        if t in light_tasks:
            return TaskComplexity.LIGHT
        if t in heavy_tasks:
            return TaskComplexity.HEAVY

        # Fallback heuristic: short, structured messages are light; long/complex are heavy.
        return TaskComplexity.HEAVY if len(text or "") > 160 else TaskComplexity.LIGHT

    def model_for(self, complexity: TaskComplexity) -> str:
        return self.fast_model if complexity == TaskComplexity.LIGHT else self.strong_model

    # -- Invocation --------------------------------------------------------
    def invoke(
        self,
        task_type: str,
        system_text: str,
        messages: List[dict],
        temperature: float = 0.2,
        complexity: Optional[TaskComplexity] = None,
        probe_text: str = "",
        max_tokens: int = 1024,
    ) -> dict:
        """
        Route by complexity and call Bedrock. Returns the bedrock result dict
        enriched with routing metadata (task_type, tier, model_id).
        """
        tier = self.classify(task_type, probe_text, complexity)
        model_id = self.model_for(tier)

        result = bedrock_client.invoke_converse(
            model_id=model_id,
            system_text=system_text,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        # Enrich with routing metadata for the audit trail (Pillar 4).
        result.setdefault("model_id", model_id)
        result["task_type"] = task_type
        result["tier"] = tier.value
        return result


model_gateway = ModelGateway()
