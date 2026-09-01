from __future__ import annotations

import sys

from api.bootstrap import clear_demo_modules, prepare_demo_import


def test_prepare_demo_import_clears_sibling_agents_workflow():
    prepare_demo_import("Connoisseur Companion", chdir=False)
    from agents.workflow import AGENT_PROMPTS  # noqa: WPS433

    assert AGENT_PROMPTS
    connoisseur_file = sys.modules["agents.workflow"].__file__
    assert connoisseur_file is not None
    assert "Connoisseur Companion" in connoisseur_file

    prepare_demo_import("DocChat", chdir=False)
    from agents.workflow import AgentWorkflow  # noqa: WPS433

    docchat_file = sys.modules["agents.workflow"].__file__
    assert docchat_file is not None
    assert "DocChat" in docchat_file
    assert AgentWorkflow is not None


def test_prepare_demo_import_promotes_path_after_switch_back():
    prepare_demo_import("DocChat", chdir=False)
    from agents.workflow import AgentWorkflow  # noqa: WPS433

    assert AgentWorkflow is not None

    prepare_demo_import("Connoisseur Companion", chdir=False)
    from agents.workflow import AGENT_PROMPTS  # noqa: WPS433

    assert AGENT_PROMPTS

    prepare_demo_import("DocChat", chdir=False)
    from agents.workflow import AgentWorkflow as AgentWorkflowAgain  # noqa: WPS433

    assert "DocChat" in sys.modules["agents.workflow"].__file__
    assert AgentWorkflowAgain is not None


def test_prepare_demo_import_removes_other_demo_paths():
    prepare_demo_import("Connoisseur Companion", chdir=False)
    assert any("Connoisseur Companion" in entry for entry in sys.path)

    prepare_demo_import("DocChat", chdir=False)
    assert any("DocChat" in entry for entry in sys.path)
    assert not any("Connoisseur Companion" in entry for entry in sys.path)


def test_clear_demo_modules_keeps_shared():
    prepare_demo_import("DocChat", chdir=False)
    import shared.llm  # noqa: WPS433

    shared_name = shared.llm.__name__
    assert shared_name in sys.modules

    clear_demo_modules()
    assert shared_name in sys.modules
