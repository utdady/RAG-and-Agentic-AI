"""LangGraph: relevance → research → verify (± re-research)."""

from __future__ import annotations

from typing import Dict, List, TypedDict

from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from langgraph.graph import END, StateGraph

from agents.relevance_checker import RelevanceChecker
from agents.research_agent import ResearchAgent
from agents.verification_agent import VerificationAgent
from config import settings
from utils.logging import logger


class AgentState(TypedDict):
    question: str
    documents: List[Document]
    draft_answer: str
    verification_report: str
    is_relevant: bool
    retriever: EnsembleRetriever
    research_loops: int


class AgentWorkflow:
    def __init__(self):
        self.researcher = ResearchAgent()
        self.verifier = VerificationAgent()
        self.relevance_checker = RelevanceChecker()
        self.compiled_workflow = self.build_workflow()

    def build_workflow(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("check_relevance", self._check_relevance_step)
        workflow.add_node("research", self._research_step)
        workflow.add_node("verify", self._verification_step)
        workflow.set_entry_point("check_relevance")
        workflow.add_conditional_edges(
            "check_relevance",
            self._decide_after_relevance_check,
            {"relevant": "research", "irrelevant": END},
        )
        workflow.add_edge("research", "verify")
        workflow.add_conditional_edges(
            "verify",
            self._decide_next_step,
            {"re_research": "research", "end": END},
        )
        return workflow.compile()

    def _check_relevance_step(self, state: AgentState) -> Dict:
        classification = self.relevance_checker.check(
            question=state["question"], retriever=state["retriever"], k=20
        )
        if classification in {"CAN_ANSWER", "PARTIAL"}:
            return {"is_relevant": True}
        return {
            "is_relevant": False,
            "draft_answer": (
                "This question isn't related (or there's no data) for your query. "
                "Please ask another question relevant to the uploaded document(s)."
            ),
            "verification_report": "Skipped (NO_MATCH)",
        }

    def _decide_after_relevance_check(self, state: AgentState) -> str:
        return "relevant" if state["is_relevant"] else "irrelevant"

    def _research_step(self, state: AgentState) -> Dict:
        docs = state["documents"] or state["retriever"].invoke(state["question"])
        result = self.researcher.generate(state["question"], docs)
        return {
            "draft_answer": result["draft_answer"],
            "documents": docs,
            "research_loops": int(state.get("research_loops") or 0) + 1,
        }

    def _verification_step(self, state: AgentState) -> Dict:
        result = self.verifier.check(state["draft_answer"], state["documents"])
        return {"verification_report": result["verification_report"]}

    def _decide_next_step(self, state: AgentState) -> str:
        report = state.get("verification_report") or ""
        loops = int(state.get("research_loops") or 0)
        if loops >= settings.MAX_RESEARCH_LOOPS:
            logger.info("Max research loops reached; ending.")
            return "end"
        if "Supported: NO" in report or "Relevant: NO" in report:
            logger.info("Verification failed; re-research.")
            return "re_research"
        return "end"

    def full_pipeline(self, question: str, retriever: EnsembleRetriever):
        documents = retriever.invoke(question)
        logger.info("Retrieved %s docs", len(documents))
        initial: AgentState = {
            "question": question,
            "documents": documents,
            "draft_answer": "",
            "verification_report": "",
            "is_relevant": False,
            "retriever": retriever,
            "research_loops": 0,
        }
        final = self.compiled_workflow.invoke(initial)
        return {
            "draft_answer": final.get("draft_answer") or "",
            "verification_report": final.get("verification_report") or "",
        }
