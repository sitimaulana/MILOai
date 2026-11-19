# RAG Retrieval Policy

## Query signals
- learner_level
- speaking_skill
- topic
- learner_utterance
- detected_error
- feedback_type
- task_type

## Recommended retrieval order
1. metadata filter by level
2. filter to speaking-relevant knowledge
3. filter by error/topic where available
4. semantic similarity
5. retrieve 3–5 chunks
6. remove duplicate/contradictory chunks
7. send grounded context to LLM

## Example query
level=B1, skill=speaking, topic=travel, error=present_perfect

## Guardrail
If no relevant knowledge is retrieved, the LLM should not invent a CEFR-specific claim.
