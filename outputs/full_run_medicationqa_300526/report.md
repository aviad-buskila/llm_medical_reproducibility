# Clinical Reproducibility Evaluation Report

## Table 1 - Quality (model-level mean with 95% bootstrap CI)

Each cell is `mean [low, high]`. The point estimate is the mean across questions of the per-question mean metric (equal weight per question); the interval is a percentile bootstrap resampling questions with replacement (1000 resamples). Higher is better.

| Model                    | BERTScore F1         | Token F1             | ROUGE-L              | Judge                |
|:-------------------------|:---------------------|:---------------------|:---------------------|:---------------------|
| gemma3:12b               | 0.848 [0.841, 0.855] | 0.185 [0.160, 0.209] | 0.121 [0.106, 0.137] | 0.735 [0.646, 0.816] |
| gemma3:4b                | 0.842 [0.834, 0.848] | 0.175 [0.148, 0.202] | 0.110 [0.095, 0.123] | 0.680 [0.573, 0.781] |
| gpt-4.1-nano             | 0.852 [0.844, 0.859] | 0.209 [0.182, 0.238] | 0.133 [0.116, 0.150] | 0.760 [0.662, 0.847] |
| llama3.1:8b              | 0.849 [0.841, 0.855] | 0.209 [0.184, 0.233] | 0.134 [0.118, 0.149] | 0.600 [0.507, 0.696] |
| medaibase/medgemma1.5:4b | 0.851 [0.843, 0.858] | 0.200 [0.174, 0.226] | 0.127 [0.112, 0.143] | 0.640 [0.539, 0.731] |

## Table 2 - Reproducibility (model-level mean with 95% bootstrap CI)

Each cell is `mean [low, high]`, bootstrap over questions. Lexical self-agreement = fraction of runs matching the modal normalized output (↑ better); lexical uniqueness = distinct normalized outputs / N (↓ better); semantic self-similarity = mean pairwise BERTScore-F1 across runs (↑ better, robust to paraphrase).

| Model                    | Self-agreement (lexical) ↑   | Uniqueness (lexical) ↓   | Semantic self-similarity ↑   |
|:-------------------------|:-----------------------------|:-------------------------|:-----------------------------|
| gemma3:12b               | 0.260 [0.222, 0.302]         | 0.764 [0.700, 0.820]     | 0.965 [0.959, 0.970]         |
| gemma3:4b                | 0.176 [0.152, 0.204]         | 0.892 [0.848, 0.928]     | 0.965 [0.960, 0.969]         |
| gpt-4.1-nano             | 0.190 [0.156, 0.226]         | 0.884 [0.826, 0.932]     | 0.959 [0.955, 0.964]         |
| llama3.1:8b              | 0.162 [0.126, 0.208]         | 0.930 [0.882, 0.972]     | 0.939 [0.934, 0.944]         |
| medaibase/medgemma1.5:4b | 0.200 [0.160, 0.246]         | 0.868 [0.814, 0.916]     | 0.952 [0.946, 0.957]         |

## Part 1 - Model-vs-Gold Quality (Average and Median)

Higher values indicate better alignment to gold answers.

| model                    |   token_f1_avg |   string_similarity_avg |   exact_match_avg |   bleu_avg |   rouge_l_avg |   bertscore_f1_avg |   judge_score_avg |   token_f1_median |   string_similarity_median |   exact_match_median |   bleu_median |   rouge_l_median |   bertscore_f1_median |   judge_score_median |
|:-------------------------|---------------:|------------------------:|------------------:|-----------:|--------------:|-------------------:|------------------:|------------------:|---------------------------:|---------------------:|--------------:|-----------------:|----------------------:|---------------------:|
| llama3.1:8b              |          0.209 |                   0.125 |             0.000 |      0.015 |         0.134 |              0.849 |             0.598 |             0.218 |                      0.097 |                0.000 |         0.009 |            0.129 |                 0.852 |                0.650 |
| gpt-4.1-nano             |          0.209 |                   0.122 |             0.000 |      0.016 |         0.133 |              0.852 |             0.759 |             0.225 |                      0.085 |                0.000 |         0.009 |            0.134 |                 0.856 |                0.950 |
| medaibase/medgemma1.5:4b |          0.200 |                   0.122 |             0.000 |      0.012 |         0.127 |              0.851 |             0.641 |             0.211 |                      0.094 |                0.000 |         0.007 |            0.128 |                 0.854 |                0.800 |
| gemma3:12b               |          0.185 |                   0.115 |             0.000 |      0.016 |         0.121 |              0.848 |             0.737 |             0.183 |                      0.090 |                0.000 |         0.008 |            0.118 |                 0.851 |                0.950 |
| gemma3:4b                |          0.175 |                   0.094 |             0.000 |      0.008 |         0.110 |              0.842 |             0.678 |             0.182 |                      0.056 |                0.000 |         0.006 |            0.112 |                 0.847 |                0.900 |

## Part 2 - Within-Model Reproducibility (Ignoring Gold)

- `normalized_self_agreement_rate`: higher is better (same normalized answer repeated).
- `normalized_response_uniqueness_rate`: lower is better (less variability).

| model                    |   normalized_self_agreement_rate |   normalized_response_uniqueness_rate |
|:-------------------------|---------------------------------:|--------------------------------------:|
| gemma3:12b               |                            0.260 |                                 0.764 |
| medaibase/medgemma1.5:4b |                            0.200 |                                 0.868 |
| gpt-4.1-nano             |                            0.190 |                                 0.884 |
| gemma3:4b                |                            0.176 |                                 0.892 |
| llama3.1:8b              |                            0.162 |                                 0.930 |

## Part 3 - Reproducibility by Model and Question

Rows at the top are least reproducible and should be inspected first.

| model      | question_id   |   n_runs |   normalized_self_agreement_rate |   normalized_response_uniqueness_rate |
|:-----------|:--------------|---------:|---------------------------------:|--------------------------------------:|
| gemma3:12b | q110          |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q258          |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q282          |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q287          |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q328          |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q336          |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q410          |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q502          |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q645          |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q656          |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q657          |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q77           |       10 |                            0.100 |                                 1.000 |
| gemma3:4b  | q166          |       10 |                            0.100 |                                 1.000 |
| gemma3:4b  | q213          |       10 |                            0.100 |                                 1.000 |
| gemma3:4b  | q251          |       10 |                            0.100 |                                 1.000 |
| gemma3:4b  | q257          |       10 |                            0.100 |                                 1.000 |
| gemma3:4b  | q282          |       10 |                            0.100 |                                 1.000 |
| gemma3:4b  | q287          |       10 |                            0.100 |                                 1.000 |
| gemma3:4b  | q290          |       10 |                            0.100 |                                 1.000 |
| gemma3:4b  | q295          |       10 |                            0.100 |                                 1.000 |

## Part 4 - Global Model Comparison (Ignoring Question ID)

This section compares model output variability across all runs/questions together.

| model                    |   total_outputs |   unique_outputs |   unique_normalized_outputs |   global_response_uniqueness_rate |   global_normalized_uniqueness_rate |
|:-------------------------|----------------:|-----------------:|----------------------------:|----------------------------------:|------------------------------------:|
| gemma3:12b               |             500 |              382 |                         379 |                             0.764 |                               0.758 |
| medaibase/medgemma1.5:4b |             500 |              436 |                         434 |                             0.872 |                               0.868 |
| gpt-4.1-nano             |             500 |              441 |                         440 |                             0.882 |                               0.880 |
| gemma3:4b                |             500 |              457 |                         446 |                             0.914 |                               0.892 |
| llama3.1:8b              |             500 |              467 |                         465 |                             0.934 |                               0.930 |

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
| gpt-4.1-nano             |         1185.281 |              87.078 |                  83.284 |            1019.536 |                 89.000 |                     86.212 |
| gemma3:4b                |         1837.743 |             110.932 |                  60.385 |            1811.576 |                109.000 |                     60.482 |
| llama3.1:8b              |         2281.332 |              92.008 |                  40.191 |            2224.692 |                 90.000 |                     40.095 |
| medaibase/medgemma1.5:4b |         2561.894 |              74.156 |                  28.933 |            2487.600 |                 72.000 |                     28.990 |
| gemma3:12b               |         3890.914 |              92.652 |                  23.813 |            3943.084 |                 94.000 |                     23.897 |

## Reading Guide
- Use Part 1 to compare clinical answer quality versus gold.
- Use Part 2 to compare model stability across repeated runs.
- Use Part 3 to find specific unstable model/question pairs.
- Use Part 4 to compare overall model variability without question-level grouping.
- Use Part 5 to compare direct model-to-model behavioral overlap.
- Use Part 6 to compare speed and token output characteristics across models.