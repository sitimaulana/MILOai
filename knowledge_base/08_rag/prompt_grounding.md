# RAG Grounding Prompt Guidance

The LLM should:
- use retrieved knowledge as evidence for learning guidance
- preserve the learner's intended meaning
- give concise feedback
- distinguish correction from optional improvement
- avoid claiming that one utterance proves a CEFR level
- account for possible ASR errors
- ask for another attempt when useful

Suggested output:
1. What you did well
2. One improvement
3. Correct/natural example
4. Short explanation
5. Retry prompt
