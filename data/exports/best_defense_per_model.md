# Best Defense Mechanism Per Model

This report shows the most effective defense for each model.

## claude-haiku-4-5-20251001

| Defense | Total Tests | Successful Attacks | ASR | DER |
|---------|-------------|-------------------|-----|-----|
| DualLLM | 40 | 1 | 2.5% | 97.5% |
| none | 40 | 1 | 2.5% | 97.5% |
| PerplexityFilter | 40 | 2 | 5.0% | 95.0% |
| InstructionHierarchy | 40 | 4 | 10.0% | 90.0% |
| OutputFilter | 40 | 4 | 10.0% | 90.0% |
| ContextIsolation | 40 | 5 | 12.5% | 87.5% |
| SemanticSimilarity | 40 | 6 | 15.0% | 85.0% |
| InputSanitizer | 40 | 6 | 15.0% | 85.0% |
| PromptTemplate | 40 | 8 | 20.0% | 80.0% |

**Best Defense:** DualLLM with 97.5% effectiveness

---

## gpt-5-nano

| Defense | Total Tests | Successful Attacks | ASR | DER |
|---------|-------------|-------------------|-----|-----|
| DualLLM | 40 | 0 | 0.0% | 100.0% |
| SemanticSimilarity | 40 | 0 | 0.0% | 100.0% |
| PerplexityFilter | 40 | 0 | 0.0% | 100.0% |
| InstructionHierarchy | 40 | 0 | 0.0% | 100.0% |
| ContextIsolation | 40 | 0 | 0.0% | 100.0% |
| OutputFilter | 40 | 0 | 0.0% | 100.0% |
| PromptTemplate | 40 | 0 | 0.0% | 100.0% |
| none | 40 | 0 | 0.0% | 100.0% |
| InputSanitizer | 40 | 1 | 2.5% | 97.5% |

**Best Defense:** DualLLM with 100.0% effectiveness

---

## llama3.2

| Defense | Total Tests | Successful Attacks | ASR | DER |
|---------|-------------|-------------------|-----|-----|
| DualLLM | 40 | 1 | 2.5% | 97.5% |
| ContextIsolation | 40 | 1 | 2.5% | 97.5% |
| InstructionHierarchy | 40 | 5 | 12.5% | 87.5% |
| PerplexityFilter | 40 | 9 | 22.5% | 77.5% |
| InputSanitizer | 40 | 9 | 22.5% | 77.5% |
| none | 40 | 9 | 22.5% | 77.5% |
| OutputFilter | 40 | 11 | 27.5% | 72.5% |
| SemanticSimilarity | 40 | 12 | 30.0% | 70.0% |
| PromptTemplate | 40 | 12 | 30.0% | 70.0% |

**Best Defense:** DualLLM with 97.5% effectiveness

---

