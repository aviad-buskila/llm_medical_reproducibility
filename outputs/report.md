# Clinical Reproducibility Evaluation Report

## Table 1 - Quality (model-level mean with 95% bootstrap CI)

Each cell is `mean [low, high]`. The point estimate is the mean across questions of the per-question mean metric (equal weight per question); the interval is a percentile bootstrap resampling questions with replacement (1000 resamples). Higher is better.

| Model                    | BERTScore F1         | Token F1             | ROUGE-L              | Judge                |
|:-------------------------|:---------------------|:---------------------|:---------------------|:---------------------|
| gemma3:12b               | 0.789 [0.739, 0.839] | 0.201 [0.133, 0.337] | 0.134 [0.084, 0.207] | 0.667 [0.200, 1.000] |
| gemma3:4b                | 0.785 [0.739, 0.828] | 0.165 [0.130, 0.202] | 0.086 [0.072, 0.109] | 0.717 [0.333, 1.000] |
| gpt-4.1-mini             | 0.790 [0.741, 0.838] | 0.212 [0.139, 0.357] | 0.126 [0.071, 0.218] | 0.789 [0.367, 1.000] |
| llama3.1:8b              | 0.789 [0.741, 0.832] | 0.200 [0.137, 0.307] | 0.116 [0.072, 0.185] | 0.750 [0.367, 1.000] |
| medaibase/medgemma1.5:4b | 0.784 [0.738, 0.832] | 0.183 [0.119, 0.240] | 0.103 [0.062, 0.186] | 0.680 [0.300, 1.000] |

## Table 2 - Reproducibility (model-level mean with 95% bootstrap CI)

Each cell is `mean [low, high]`, bootstrap over questions. Lexical self-agreement = fraction of runs matching the modal normalized output (↑ better); lexical uniqueness = distinct normalized outputs / N (↓ better); semantic self-similarity = mean pairwise BERTScore-F1 across runs (↑ better, robust to paraphrase).

| Model                    | Self-agreement (lexical) ↑   | Uniqueness (lexical) ↓   | Semantic self-similarity ↑   |
|:-------------------------|:-----------------------------|:-------------------------|:-----------------------------|
| gemma3:12b               | 0.444 [0.333, 0.667]         | 0.889 [0.667, 1.000]     | 0.980 [0.964, 0.997]         |
| gemma3:4b                | 0.333 [0.333, 0.333]         | 1.000 [1.000, 1.000]     | 0.978 [0.957, 0.989]         |
| gpt-4.1-mini             | 0.333 [0.333, 0.333]         | 1.000 [1.000, 1.000]     | 0.974 [0.959, 0.995]         |
| llama3.1:8b              | 0.333 [0.333, 0.333]         | 1.000 [1.000, 1.000]     | 0.928 [0.900, 0.958]         |
| medaibase/medgemma1.5:4b | 0.444 [0.333, 0.667]         | 0.889 [0.667, 1.000]     | 0.961 [0.938, 0.976]         |

## Part 1 - Model-vs-Gold Quality (Average and Median)

Higher values indicate better alignment to gold answers.

| model                    |   token_f1_avg |   string_similarity_avg |   exact_match_avg |   bleu_avg |   rouge_l_avg |   bertscore_f1_avg |   judge_score_avg |   token_f1_median |   string_similarity_median |   exact_match_median |   bleu_median |   rouge_l_median |   bertscore_f1_median |   judge_score_median |
|:-------------------------|---------------:|------------------------:|------------------:|-----------:|--------------:|-------------------:|------------------:|------------------:|---------------------------:|---------------------:|--------------:|-----------------:|----------------------:|---------------------:|
| gpt-4.1-mini             |          0.212 |                   0.073 |             0.000 |      0.010 |         0.126 |              0.790 |             0.789 |             0.145 |                      0.039 |                0.000 |         0.006 |            0.091 |                 0.790 |                1.000 |
| gemma3:12b               |          0.201 |                   0.109 |             0.000 |      0.019 |         0.134 |              0.789 |             0.667 |             0.133 |                      0.103 |                0.000 |         0.007 |            0.111 |                 0.790 |                0.800 |
| llama3.1:8b              |          0.200 |                   0.084 |             0.000 |      0.015 |         0.116 |              0.789 |             0.750 |             0.152 |                      0.040 |                0.000 |         0.005 |            0.082 |                 0.795 |                0.850 |
| medaibase/medgemma1.5:4b |          0.183 |                   0.074 |             0.000 |      0.010 |         0.103 |              0.784 |             0.680 |             0.149 |                      0.039 |                0.000 |         0.004 |            0.064 |                 0.782 |                0.750 |
| gemma3:4b                |          0.165 |                   0.065 |             0.000 |      0.004 |         0.086 |              0.785 |             0.717 |             0.162 |                      0.027 |                0.000 |         0.003 |            0.077 |                 0.789 |                0.800 |

## Part 2 - Within-Model Reproducibility (Ignoring Gold)

- `normalized_self_agreement_rate`: higher is better (same normalized answer repeated).
- `normalized_response_uniqueness_rate`: lower is better (less variability).

| model                    |   normalized_self_agreement_rate |   normalized_response_uniqueness_rate |
|:-------------------------|---------------------------------:|--------------------------------------:|
| gemma3:12b               |                            0.444 |                                 0.889 |
| medaibase/medgemma1.5:4b |                            0.444 |                                 0.889 |
| gemma3:4b                |                            0.333 |                                 1.000 |
| gpt-4.1-mini             |                            0.333 |                                 1.000 |
| llama3.1:8b              |                            0.333 |                                 1.000 |

## Part 3 - Reproducibility by Model and Question

Rows at the top are least reproducible and should be inspected first.

| model                    | question_id   |   n_runs |   normalized_self_agreement_rate |   normalized_response_uniqueness_rate |
|:-------------------------|:--------------|---------:|---------------------------------:|--------------------------------------:|
| gemma3:12b               | q15846        |        3 |                            0.333 |                                 1.000 |
| gemma3:12b               | q4460         |        3 |                            0.333 |                                 1.000 |
| gemma3:4b                | q15701        |        3 |                            0.333 |                                 1.000 |
| gemma3:4b                | q15846        |        3 |                            0.333 |                                 1.000 |
| gemma3:4b                | q4460         |        3 |                            0.333 |                                 1.000 |
| gpt-4.1-mini             | q15701        |        3 |                            0.333 |                                 1.000 |
| gpt-4.1-mini             | q15846        |        3 |                            0.333 |                                 1.000 |
| gpt-4.1-mini             | q4460         |        3 |                            0.333 |                                 1.000 |
| llama3.1:8b              | q15701        |        3 |                            0.333 |                                 1.000 |
| llama3.1:8b              | q15846        |        3 |                            0.333 |                                 1.000 |
| llama3.1:8b              | q4460         |        3 |                            0.333 |                                 1.000 |
| medaibase/medgemma1.5:4b | q15846        |        3 |                            0.333 |                                 1.000 |
| medaibase/medgemma1.5:4b | q4460         |        3 |                            0.333 |                                 1.000 |
| gemma3:12b               | q15701        |        3 |                            0.667 |                                 0.667 |
| medaibase/medgemma1.5:4b | q15701        |        3 |                            0.667 |                                 0.667 |

## Part 4 - Global Model Comparison (Ignoring Question ID)

This section compares model output variability across all runs/questions together.

| model                    |   total_outputs |   unique_outputs |   unique_normalized_outputs |   global_response_uniqueness_rate |   global_normalized_uniqueness_rate |
|:-------------------------|----------------:|-----------------:|----------------------------:|----------------------------------:|------------------------------------:|
| gemma3:12b               |               9 |                8 |                           8 |                             0.889 |                               0.889 |
| medaibase/medgemma1.5:4b |               9 |                8 |                           8 |                             0.889 |                               0.889 |
| gemma3:4b                |               9 |                9 |                           9 |                             1.000 |                               1.000 |
| gpt-4.1-mini             |               9 |                9 |                           9 |                             1.000 |                               1.000 |
| llama3.1:8b              |               9 |                9 |                           9 |                             1.000 |                               1.000 |

## Part 5 - Pairwise Model Similarity Matrix

Cell value = fraction of aligned `(question_id, run_index)` pairs where two models produced the exact same normalized output.

|                          |   gemma3:12b |   gemma3:4b |   gpt-4.1-mini |   llama3.1:8b |   medaibase/medgemma1.5:4b |
|:-------------------------|-------------:|------------:|---------------:|--------------:|---------------------------:|
| gemma3:12b               |        1.000 |       0.000 |          0.000 |         0.000 |                      0.000 |
| gemma3:4b                |        0.000 |       1.000 |          0.000 |         0.000 |                      0.000 |
| gpt-4.1-mini             |        0.000 |       0.000 |          1.000 |         0.000 |                      0.000 |
| llama3.1:8b              |        0.000 |       0.000 |          0.000 |         1.000 |                      0.000 |
| medaibase/medgemma1.5:4b |        0.000 |       0.000 |          0.000 |         0.000 |                      1.000 |

## Part 6 - Performance (Model Level)

Per-run latency and output token throughput, aggregated at model level.

| model                    |   latency_ms_avg |   output_tokens_avg |   tokens_per_second_avg |   latency_ms_median |   output_tokens_median |   tokens_per_second_median |
|:-------------------------|-----------------:|--------------------:|------------------------:|--------------------:|-----------------------:|---------------------------:|
| gpt-4.1-mini             |         2061.831 |             107.444 |                  56.826 |            1840.819 |                105.000 |                     55.410 |
| gemma3:4b                |         3087.173 |             117.889 |                  57.157 |            1772.072 |                112.000 |                     62.728 |
| medaibase/medgemma1.5:4b |         3222.021 |              82.667 |                  27.183 |            3301.731 |                 81.000 |                     28.861 |
| llama3.1:8b              |         4092.118 |             127.889 |                  40.062 |            3228.234 |                131.000 |                     44.052 |
| gemma3:12b               |         4989.546 |              92.111 |                  23.455 |            3565.846 |                 89.000 |                     25.802 |

## Reading Guide
- Use Part 1 to compare clinical answer quality versus gold.
- Use Part 2 to compare model stability across repeated runs.
- Use Part 3 to find specific unstable model/question pairs.
- Use Part 4 to compare overall model variability without question-level grouping.
- Use Part 5 to compare direct model-to-model behavioral overlap.
- Use Part 6 to compare speed and token output characteristics across models.