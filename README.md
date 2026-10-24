# Handudu · Kaggle Portfolio

从 [handudu 的 Kaggle 公开作品](https://www.kaggle.com/handudu)整理的计算生物学、医学影像、数据科学和机器学习代码档案。归档日期：**2026-10-24**。

本次检查 20 个公开 Notebook / Script，精选 **10 个项目**：5 个生物与医学相关项目，以及 5 个数据科学、时间序列和机器学习项目；其中包含 **1 个银牌、3 个铜牌 Notebook**。这里的奖牌均为 **Notebook 奖牌**，不是对应比赛的名次或奖金。

公开档案显示账号为竞赛 **Expert**，累计竞赛 **7 银、4 铜**，Notebook **1 银、3 铜**。登录后已逐项核实 11 项竞赛奖牌及团队排名，见 [竞赛成绩清单](COMPETITION_RESULTS.md)。现有代码版本与最终计分提交的对应关系仍需核对。[账号快照](account-snapshot.json)。

## 项目导航

| 项目 | 方向 | Notebook 奖牌 |
| --- | --- | --- |
| [RNA 3D Folding · EDA](projects/01-rna-folding) | 计算生物学 / 探索性分析 | 🥈 银牌 |
| [Bacterial Flagellar Motor Detection](projects/02-bacterial-motor-detection) | 计算生物学 / 三维目标定位 | — |
| [Image2Biomass Training Baseline](projects/03-image2biomass) | 生物与农业 / 回归建模 | — |
| [Cell Instance Segmentation with MMDetection](projects/04-cell-instance-segmentation) | 生物医学图像 / 实例分割 | — |
| [RSNA Knee MRI Inference](projects/05-rsna-knee-inference) | 医学影像 / 分类推理 | — |
| [Hull Tactical · Time Series Validation](projects/06-time-series-validation) | 数据科学 / 时间序列 | 🥉 铜牌 |
| [Multilingual Chatbot Preference · LoRA](projects/07-chatbot-preference-lora) | 机器学习 / 大模型推理 | 🥉 铜牌 |
| [Great Barrier Reef · YOLOv5 + WBF](projects/08-reef-object-detection) | 生态图像 / 目标检测 | 🥉 铜牌 |
| [Mathematical Reasoning · Annotated Notebook](projects/09-llm-code-reasoning) | 机器学习 / 数学推理 | — |
| [Tabular Fraud Classification · CatBoost](projects/10-tabular-fraud-catboost) | 数据科学 / 表格分类 | — |

生物方向以 RNA 探索分析、生物图像检测、分割和回归为主，当前公开作品中没有单独整理出经典临床试验、生存分析或因果推断项目。

## 如何使用

1. 打开项目目录的 README，查看研究内容、上游来源和依赖限制。
2. 在 GitHub 预览 `notebook.ipynb`，或阅读 RSNA 项目的 `source/rsna/` 模块。
3. 如需运行，优先打开每个项目的原 Kaggle 页面，按其 Input 和原环境配置数据及模型。

这是源码归档与作品索引。本次没有重训或复现排行榜结果。多数项目需要原模型权重，部分输入源当前为私有；没有将私有输入或比赛原始数据打包进仓库。

RNA 银牌 Notebook 的后段含未执行的 R 单元，MMDetection 项目使用旧环境，部分学习 / 调试代码存在方法或环境限制，已逐项写在项目 README 中。代码保持原貌，Notebook 运行输出已清理。

## 来源、版本与检查

- [结构化项目清单](catalog.json) / [CSV 索引](catalog.csv)：版本、奖牌、来源、SHA-256 和依赖。
- [全部 20 个公开项目的筛选记录](inventory.json)：包括未选原因和空导出项。
- [来源与贡献说明](SOURCES.md)：区分自己的发布版本与 fork 的上游作品。
- [许可说明](LICENSE_NOTES.md)：保留原作者、来源与已有许可，不统一重新授权。
- [静态检查记录](VALIDATION.md)：文件结构、源码保真与敏感内容检查范围。

## English

A curated source archive of 10 public projects from [handudu](https://www.kaggle.com/handudu), covering computational biology, biomedical imaging, data science and machine learning. Four included notebooks hold Kaggle Notebook medals (one silver, three bronze). Verified team competition ranks and medals are documented separately in COMPETITION_RESULTS.md. No claim is made that a particular archived notebook is the selected final submission, independently authored, or reproduced during this archival pass. Upstream fork relationships are recorded in each project's provenance file. Dataset files, model weights, credentials and notebook outputs are excluded. Training and inference were not executed during this archival pass.
