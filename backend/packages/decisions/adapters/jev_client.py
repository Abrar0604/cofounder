import os
import logging
from typing import Dict, Any, Optional
from packages.decisions.ports import DecisionModel, Question, Decision
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class JevClient(DecisionModel):
    def __init__(self):
        # Primary model (fast, cheaper)
        self.primary_llm = ChatGoogleGenerativeAI(
            model="gemini-3.8-flash",
            temperature=0.0
        ).with_structured_output(Decision)
        
        # Fallback model (more capable, slower)
        self.fallback_llm = ChatGoogleGenerativeAI(
            model="gemini-3.8-pro",
            temperature=0.0
        ).with_structured_output(Decision)

    async def evaluate(self, question: Question) -> Decision:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a highly accurate decision-making engine. Evaluate the given context and metadata against the question ID '{question_id}' to produce a structured decision."),
            ("human", "Context: {context}\nMetadata: {metadata}")
        ])
        
        chain = prompt | self.primary_llm
        fallback_chain = prompt | self.fallback_llm
        
        try:
            decision = await chain.ainvoke({
                "question_id": question.id,
                "context": question.context,
                "metadata": question.metadata
            })
            if not decision:
                raise ValueError("Model returned None or failed to parse")
            return decision
        except Exception as e:
            logger.warning(f"Primary decision model failed for {question.id}: {e}. Falling back to Pro model.")
            try:
                decision = await fallback_chain.ainvoke({
                    "question_id": question.id,
                    "context": question.context,
                    "metadata": question.metadata
                })
                if not decision:
                    raise ValueError("Fallback model returned None or failed to parse")
                return decision
            except Exception as fallback_e:
                logger.error(f"Fallback decision model failed for {question.id}: {fallback_e}.")
                # Ultimate fallback to avoid crashing the system
                return Decision(
                    question_id=question.id,
                    confidence=0.0,
                    reasoning=f"Error evaluating decision: {fallback_e}",
                    action="ESCALATE"
                )
