# Clinical Reproducibility Evaluation Report

## Table 1 - Quality (model-level mean with 95% bootstrap CI)

Each cell is `mean [low, high]`. The point estimate is the mean across questions of the per-question mean metric (equal weight per question); the interval is a percentile bootstrap resampling questions with replacement (1000 resamples). Higher is better.

| Model                    | BERTScore F1         | Token F1             | ROUGE-L              | Judge                |
|:-------------------------|:---------------------|:---------------------|:---------------------|:---------------------|
| gemma3:12b               | 0.844 [0.834, 0.863] | 0.164 [0.112, 0.239] | 0.112 [0.080, 0.168] | 0.311 [0.000, 0.933] |
| gemma3:4b                | 0.837 [0.820, 0.862] | 0.168 [0.097, 0.309] | 0.108 [0.081, 0.133] | 0.333 [0.000, 0.967] |
| gpt-4.1-nano             | 0.853 [0.846, 0.858] | 0.180 [0.107, 0.285] | 0.118 [0.100, 0.145] | 0.622 [0.000, 1.000] |
| llama3.1:8b              | 0.844 [0.822, 0.862] | 0.211 [0.131, 0.314] | 0.130 [0.088, 0.151] | 0.178 [0.000, 0.433] |
| medaibase/medgemma1.5:4b | 0.850 [0.839, 0.863] | 0.184 [0.127, 0.285] | 0.124 [0.100, 0.149] | 0.344 [0.000, 0.933] |

## Table 2 - Reproducibility (model-level mean with 95% bootstrap CI)

Each cell is `mean [low, high]`, bootstrap over questions. Lexical self-agreement = fraction of runs matching the modal normalized output (↑ better); lexical uniqueness = distinct normalized outputs / N (↓ better); semantic self-similarity = mean pairwise BERTScore-F1 across runs (↑ better, robust to paraphrase).

| Model                    | Self-agreement (lexical) ↑   | Uniqueness (lexical) ↓   | Semantic self-similarity ↑   |
|:-------------------------|:-----------------------------|:-------------------------|:-----------------------------|
| gemma3:12b               | 0.333 [0.333, 0.333]         | 1.000 [1.000, 1.000]     | 0.938 [0.902, 0.964]         |
| gemma3:4b                | 0.333 [0.333, 0.333]         | 1.000 [1.000, 1.000]     | 0.959 [0.930, 0.984]         |
| gpt-4.1-nano             | 0.333 [0.333, 0.333]         | 1.000 [1.000, 1.000]     | 0.928 [0.916, 0.947]         |
| llama3.1:8b              | 0.333 [0.333, 0.333]         | 1.000 [1.000, 1.000]     | 0.932 [0.918, 0.956]         |
| medaibase/medgemma1.5:4b | 0.333 [0.333, 0.333]         | 1.000 [1.000, 1.000]     | 0.950 [0.932, 0.976]         |

## Part 1 - Model-vs-Gold Quality (Average and Median)

Higher values indicate better alignment to gold answers.

| model                    |   token_f1_avg |   string_similarity_avg |   exact_match_avg |   bleu_avg |   rouge_l_avg |   bertscore_f1_avg |   judge_score_avg |   token_f1_median |   string_similarity_median |   exact_match_median |   bleu_median |   rouge_l_median |   bertscore_f1_median |   judge_score_median |
|:-------------------------|---------------:|------------------------:|------------------:|-----------:|--------------:|-------------------:|------------------:|------------------:|---------------------------:|---------------------:|--------------:|-----------------:|----------------------:|---------------------:|
| llama3.1:8b              |          0.211 |                   0.144 |             0.000 |      0.008 |         0.130 |              0.844 |             0.178 |             0.186 |                      0.165 |                0.000 |         0.008 |            0.136 |                 0.849 |                0.000 |
| medaibase/medgemma1.5:4b |          0.184 |                   0.114 |             0.000 |      0.005 |         0.124 |              0.850 |             0.344 |             0.156 |                      0.151 |                0.000 |         0.005 |            0.133 |                 0.845 |                0.100 |
| gpt-4.1-nano             |          0.180 |                   0.130 |             0.000 |      0.007 |         0.118 |              0.853 |             0.622 |             0.162 |                      0.173 |                0.000 |         0.006 |            0.111 |                 0.852 |                0.800 |
| gemma3:4b                |          0.168 |                   0.106 |             0.000 |      0.009 |         0.108 |              0.837 |             0.333 |             0.106 |                      0.110 |                0.000 |         0.003 |            0.088 |                 0.829 |                0.000 |
| gemma3:12b               |          0.164 |                   0.126 |             0.000 |      0.008 |         0.112 |              0.844 |             0.311 |             0.133 |                      0.144 |                0.000 |         0.004 |            0.088 |                 0.837 |                0.000 |

## Part 2 - Within-Model Reproducibility (Ignoring Gold)

- `normalized_self_agreement_rate`: higher is better (same normalized answer repeated).
- `normalized_response_uniqueness_rate`: lower is better (less variability).

| model                    |   normalized_self_agreement_rate |   normalized_response_uniqueness_rate |
|:-------------------------|---------------------------------:|--------------------------------------:|
| gemma3:12b               |                            0.333 |                                 1.000 |
| gemma3:4b                |                            0.333 |                                 1.000 |
| gpt-4.1-nano             |                            0.333 |                                 1.000 |
| llama3.1:8b              |                            0.333 |                                 1.000 |
| medaibase/medgemma1.5:4b |                            0.333 |                                 1.000 |

## Part 3 - Reproducibility by Model and Question

Rows at the top are least reproducible and should be inspected first.

| model                    | question_id   |   n_runs |   normalized_self_agreement_rate |   normalized_response_uniqueness_rate |
|:-------------------------|:--------------|---------:|---------------------------------:|--------------------------------------:|
| gemma3:12b               | q258          |        3 |                            0.333 |                                 1.000 |
| gemma3:12b               | q287          |        3 |                            0.333 |                                 1.000 |
| gemma3:12b               | q656          |        3 |                            0.333 |                                 1.000 |
| gemma3:4b                | q258          |        3 |                            0.333 |                                 1.000 |
| gemma3:4b                | q287          |        3 |                            0.333 |                                 1.000 |
| gemma3:4b                | q656          |        3 |                            0.333 |                                 1.000 |
| gpt-4.1-nano             | q258          |        3 |                            0.333 |                                 1.000 |
| gpt-4.1-nano             | q287          |        3 |                            0.333 |                                 1.000 |
| gpt-4.1-nano             | q656          |        3 |                            0.333 |                                 1.000 |
| llama3.1:8b              | q258          |        3 |                            0.333 |                                 1.000 |
| llama3.1:8b              | q287          |        3 |                            0.333 |                                 1.000 |
| llama3.1:8b              | q656          |        3 |                            0.333 |                                 1.000 |
| medaibase/medgemma1.5:4b | q258          |        3 |                            0.333 |                                 1.000 |
| medaibase/medgemma1.5:4b | q287          |        3 |                            0.333 |                                 1.000 |
| medaibase/medgemma1.5:4b | q656          |        3 |                            0.333 |                                 1.000 |

## Part 4 - Global Model Comparison (Ignoring Question ID)

This section compares model output variability across all runs/questions together.

| model                    |   total_outputs |   unique_outputs |   unique_normalized_outputs |   global_response_uniqueness_rate |   global_normalized_uniqueness_rate |
|:-------------------------|----------------:|-----------------:|----------------------------:|----------------------------------:|------------------------------------:|
| gemma3:12b               |               9 |                9 |                           9 |                             1.000 |                               1.000 |
| gemma3:4b                |               9 |                9 |                           9 |                             1.000 |                               1.000 |
| gpt-4.1-nano             |               9 |                9 |                           9 |                             1.000 |                               1.000 |
| llama3.1:8b              |               9 |                9 |                           9 |                             1.000 |                               1.000 |
| medaibase/medgemma1.5:4b |               9 |                9 |                           9 |                             1.000 |                               1.000 |

## Part 5 - Pairwise Model Similarity Matrix

Cell value = fraction of aligned `(question_id, run_index)` pairs where two models produced the exact same normalized output.

|                          |   gemma3:12b |   gemma3:4b |   gpt-4.1-nano |   llama3.1:8b |   medaibase/medgemma1.5:4b |
|:-------------------------|-------------:|------------:|---------------:|--------------:|---------------------------:|
| gemma3:12b               |        1.000 |       0.000 |          0.000 |         0.000 |                      0.000 |
| gemma3:4b                |        0.000 |       1.000 |          0.000 |         0.000 |                      0.000 |
| gpt-4.1-nano             |        0.000 |       0.000 |          1.000 |         0.000 |                      0.000 |
| llama3.1:8b              |        0.000 |       0.000 |          0.000 |         1.000 |                      0.000 |
| medaibase/medgemma1.5:4b |        0.000 |       0.000 |          0.000 |         0.000 |                      1.000 |

## Part 6 - Performance (Model Level)

Per-run latency and output token throughput, aggregated at model level.

| model                    |   latency_ms_avg |   output_tokens_avg |   tokens_per_second_avg |   latency_ms_median |   output_tokens_median |   tokens_per_second_median |
|:-------------------------|-----------------:|--------------------:|------------------------:|--------------------:|-----------------------:|---------------------------:|
| gpt-4.1-nano             |         1069.427 |              92.889 |                  91.579 |             937.532 |                 98.000 |                     98.130 |
| gemma3:4b                |         2058.469 |             115.111 |                  59.319 |            1914.048 |                122.000 |                     62.874 |
| llama3.1:8b              |         3031.006 |             113.333 |                  39.669 |            2947.487 |                118.000 |                     41.957 |
| medaibase/medgemma1.5:4b |         3248.186 |              84.111 |                  27.158 |            2737.346 |                 79.000 |                     28.831 |
| gemma3:12b               |         4265.402 |             100.333 |                  24.553 |            3973.705 |                104.000 |                     25.964 |

## Reading Guide
- Use Part 1 to compare clinical answer quality versus gold.
- Use Part 2 to compare model stability across repeated runs.
- Use Part 3 to find specific unstable model/question pairs.
- Use Part 4 to compare overall model variability without question-level grouping.
- Use Part 5 to compare direct model-to-model behavioral overlap.
- Use Part 6 to compare speed and token output characteristics across models.