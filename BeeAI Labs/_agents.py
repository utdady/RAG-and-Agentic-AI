"""Import RequirementAgent + requirements across BeeAI 0.1.x layouts."""

from __future__ import annotations

try:
    from beeai_framework.agents.requirement import RequirementAgent
except ImportError:
    from beeai_framework.agents.experimental import RequirementAgent  # type: ignore

try:
    from beeai_framework.agents.requirement.requirements.conditional import (
        ConditionalRequirement,
    )
except ImportError:
    from beeai_framework.agents.experimental.requirements.conditional import (  # type: ignore
        ConditionalRequirement,
    )

try:
    from beeai_framework.agents.requirement.requirements.ask_permission import (
        AskPermissionRequirement,
    )
except ImportError:
    try:
        from beeai_framework.agents.experimental.requirements.ask_permission import (  # type: ignore
            AskPermissionRequirement,
        )
    except ImportError:
        AskPermissionRequirement = None  # type: ignore

__all__ = [
    "AskPermissionRequirement",
    "ConditionalRequirement",
    "RequirementAgent",
]
