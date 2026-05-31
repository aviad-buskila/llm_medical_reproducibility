# Clinical Reproducibility Evaluation Report

## Table 1 - Quality (model-level mean with 95% bootstrap CI)

Each cell is `mean [low, high]`. The point estimate is the mean across questions of the per-question mean metric (equal weight per question); the interval is a percentile bootstrap resampling questions with replacement (1000 resamples). Higher is better.

| Model                    | BERTScore F1         | Token F1             | ROUGE-L              | Judge                |
|:-------------------------|:---------------------|:---------------------|:---------------------|:---------------------|
| gemma3:12b               | 0.843 [0.833, 0.852] | 0.238 [0.218, 0.258] | 0.147 [0.133, 0.160] | 0.580 [0.477, 0.669] |
| gemma3:4b                | 0.845 [0.836, 0.854] | 0.245 [0.225, 0.267] | 0.151 [0.137, 0.166] | 0.460 [0.371, 0.554] |
| gpt-4.1-nano             | 0.848 [0.838, 0.859] | 0.266 [0.241, 0.291] | 0.165 [0.146, 0.182] | 0.733 [0.656, 0.798] |
| llama3.1:8b              | 0.848 [0.837, 0.857] | 0.287 [0.264, 0.311] | 0.172 [0.154, 0.189] | 0.565 [0.480, 0.643] |
| medaibase/medgemma1.5:4b | 0.846 [0.835, 0.855] | 0.244 [0.224, 0.263] | 0.155 [0.140, 0.172] | 0.452 [0.369, 0.545] |

## Table 2 - Reproducibility (model-level mean with 95% bootstrap CI)

Each cell is `mean [low, high]`, bootstrap over questions. Lexical self-agreement = fraction of runs matching the modal normalized output (↑ better); lexical uniqueness = distinct normalized outputs / N (↓ better); semantic self-similarity = mean pairwise BERTScore-F1 across runs (↑ better, robust to paraphrase).

| Model                    | Self-agreement (lexical) ↑   | Uniqueness (lexical) ↓   | Semantic self-similarity ↑   |
|:-------------------------|:-----------------------------|:-------------------------|:-----------------------------|
| gemma3:12b               | 0.190 [0.158, 0.230]         | 0.896 [0.848, 0.934]     | 0.959 [0.954, 0.964]         |
| gemma3:4b                | 0.162 [0.142, 0.184]         | 0.926 [0.898, 0.950]     | 0.958 [0.953, 0.962]         |
| gpt-4.1-nano             | 0.150 [0.128, 0.176]         | 0.944 [0.914, 0.970]     | 0.958 [0.953, 0.962]         |
| llama3.1:8b              | 0.106 [0.100, 0.116]         | 0.994 [0.984, 1.000]     | 0.937 [0.932, 0.941]         |
| medaibase/medgemma1.5:4b | 0.138 [0.118, 0.164]         | 0.952 [0.922, 0.978]     | 0.947 [0.942, 0.952]         |

## Part 1 - Model-vs-Gold Quality (Average and Median)

Higher values indicate better alignment to gold answers.

| model                    |   token_f1_avg |   string_similarity_avg |   exact_match_avg |   bleu_avg |   rouge_l_avg |   bertscore_f1_avg |   judge_score_avg |   token_f1_median |   string_similarity_median |   exact_match_median |   bleu_median |   rouge_l_median |   bertscore_f1_median |   judge_score_median |
|:-------------------------|---------------:|------------------------:|------------------:|-----------:|--------------:|-------------------:|------------------:|------------------:|---------------------------:|---------------------:|--------------:|-----------------:|----------------------:|---------------------:|
| llama3.1:8b              |          0.287 |                   0.053 |             0.000 |      0.035 |         0.172 |              0.848 |             0.559 |             0.284 |                      0.033 |                0.000 |         0.015 |            0.167 |                 0.845 |                0.600 |
| gpt-4.1-nano             |          0.266 |                   0.060 |             0.000 |      0.030 |         0.165 |              0.848 |             0.731 |             0.257 |                      0.034 |                0.000 |         0.010 |            0.144 |                 0.849 |                0.850 |
| gemma3:4b                |          0.245 |                   0.039 |             0.000 |      0.020 |         0.151 |              0.845 |             0.452 |             0.243 |                      0.024 |                0.000 |         0.010 |            0.145 |                 0.847 |                0.400 |
| medaibase/medgemma1.5:4b |          0.244 |                   0.053 |             0.000 |      0.022 |         0.155 |              0.846 |             0.446 |             0.244 |                      0.032 |                0.000 |         0.009 |            0.151 |                 0.850 |                0.500 |
| gemma3:12b               |          0.238 |                   0.048 |             0.000 |      0.019 |         0.147 |              0.843 |             0.570 |             0.241 |                      0.032 |                0.000 |         0.010 |            0.140 |                 0.843 |                0.700 |

## Part 2 - Within-Model Reproducibility (Ignoring Gold)

- `normalized_self_agreement_rate`: higher is better (same normalized answer repeated).
- `normalized_response_uniqueness_rate`: lower is better (less variability).

| model                    |   normalized_self_agreement_rate |   normalized_response_uniqueness_rate |
|:-------------------------|---------------------------------:|--------------------------------------:|
| gemma3:12b               |                            0.190 |                                 0.896 |
| gemma3:4b                |                            0.162 |                                 0.926 |
| gpt-4.1-nano             |                            0.150 |                                 0.944 |
| medaibase/medgemma1.5:4b |                            0.138 |                                 0.952 |
| llama3.1:8b              |                            0.106 |                                 0.994 |

## Part 3 - Reproducibility by Model and Question

Rows at the top are least reproducible and should be inspected first.

| model      | question_id   |   n_runs |   normalized_self_agreement_rate |   normalized_response_uniqueness_rate |
|:-----------|:--------------|---------:|---------------------------------:|--------------------------------------:|
| gemma3:12b | q10088        |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q1035         |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q10548        |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q11229        |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q11246        |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q13067        |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q14403        |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q14779        |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q150          |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q15500        |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q15840        |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q15842        |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q15996        |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q16323        |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q2519         |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q2989         |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q3155         |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q3456         |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q3838         |       10 |                            0.100 |                                 1.000 |
| gemma3:12b | q4150         |       10 |                            0.100 |                                 1.000 |

## Part 4 - Global Model Comparison (Ignoring Question ID)

This section compares model output variability across all runs/questions together.

| model                    |   total_outputs |   unique_outputs |   unique_normalized_outputs |   global_response_uniqueness_rate |   global_normalized_uniqueness_rate |
|:-------------------------|----------------:|-----------------:|----------------------------:|----------------------------------:|------------------------------------:|
| gemma3:12b               |             500 |              450 |                         448 |                             0.900 |                               0.896 |
| gemma3:4b                |             500 |              469 |                         463 |                             0.938 |                               0.926 |
| gpt-4.1-nano             |             500 |              472 |                         472 |                             0.944 |                               0.944 |
| medaibase/medgemma1.5:4b |             500 |              476 |                         476 |                             0.952 |                               0.952 |
| llama3.1:8b              |             500 |              497 |                         497 |                             0.994 |                               0.994 |

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
| gpt-4.1-nano             |         1242.931 |             102.754 |                  97.918 |            1018.209 |                103.000 |                    100.401 |
| gemma3:4b                |         2039.984 |             124.422 |                  60.953 |            1958.500 |                119.000 |                     60.996 |
| llama3.1:8b              |         2860.802 |             118.192 |                  41.312 |            2775.705 |                114.500 |                     40.952 |
| medaibase/medgemma1.5:4b |         3160.229 |              92.172 |                  29.133 |            3210.429 |                 94.000 |                     29.229 |
| gemma3:12b               |         4461.035 |             105.854 |                  23.744 |            4437.619 |                106.000 |                     23.869 |

## Reading Guide
- Use Part 1 to compare clinical answer quality versus gold.
- Use Part 2 to compare model stability across repeated runs.
- Use Part 3 to find specific unstable model/question pairs.
- Use Part 4 to compare overall model variability without question-level grouping.
- Use Part 5 to compare direct model-to-model behavioral overlap.
- Use Part 6 to compare speed and token output characteristics across models.