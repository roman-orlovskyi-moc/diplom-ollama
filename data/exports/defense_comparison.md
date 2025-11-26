# Defense Mechanism Comparison

| Defense | Total Tests | Successful Attacks | Attack Success Rate | Defense Effectiveness |
|---------|-------------|-------------------|---------------------|----------------------|
| DualLLM | 120 | 2 | 1.7% | 98.3% |
| ContextIsolation | 120 | 6 | 5.0% | 95.0% |
| InstructionHierarchy | 120 | 9 | 7.5% | 92.5% |
| none | 120 | 10 | 8.3% | 91.7% |
| PerplexityFilter | 120 | 11 | 9.2% | 90.8% |
| OutputFilter | 120 | 15 | 12.5% | 87.5% |
| InputSanitizer | 120 | 16 | 13.3% | 86.7% |
| SemanticSimilarity | 120 | 18 | 15.0% | 85.0% |
| PromptTemplate | 120 | 20 | 16.7% | 83.3% |
