# Multilingual Chatbot Preference · LoRA

多语言对话偏好分类的 Gemma 2 / PEFT 推理；Notebook 铜牌。

| 项目 | 记录 |
| --- | --- |
| 领域 | 机器学习 / 大模型推理 |
| Kaggle 来源 | [LMSYS_peft0.14.0](https://www.kaggle.com/code/handudu/lmsys-peft0-14-0) |
| 来源作者 | handudu |
| 归档版本 ID | `217218292` |
| 原版本时间 | 2025-01-12T07:39:42.693Z |
| Notebook 奖牌 | 铜牌 |
| 截至归档日票数 | 9 |

## 技术内容

Gemma 2 9B、四位量化、PEFT / LoRA、tokenization、多 GPU 推理。

## 来源与贡献范围

公开列表未标记为 fork；这不等同于完整原创性审计。 这里只记录公开 Notebook 的归属和衍生关系，不将团队比赛成绩或上游作者成绩归为个人成绩。

## 使用与复现边界

依赖特定离线 wheel、基础模型和 LoRA 检查点；3 个输入源为私有。尚未验证依赖兼容性、模型加载或推理指标。

推荐从上面的 Kaggle 原页面查看 Input 和原环境，再决定是否运行。比赛数据需从原比赛自行取得并遵守其访问条件。本仓库没有打包数据、模型权重或离线安装包。

本次检查仅确认文件结构、源码保真和静态可读性；没有运行模型训练、下载依赖或执行 Notebook。Notebook 输出已清理，代码及原有注释保留。具体变更和 SHA-256 见 [provenance.json](provenance.json)。

## 原输入源

- [LMSYS wheel files](https://www.kaggle.com/datasets/emiz6413/lmsys-wheel-files)
- [Gemma-2 9b Instruct 4bit L=16/42](https://www.kaggle.com/datasets/emiz6413/73zap2gx)
- [peft-0.14.0](https://www.kaggle.com/datasets/tonyxu/peft-0-14-0)
- [peft n friends](https://www.kaggle.com/datasets/kevinwang1434/peft-n-friends)
- 私有或已不可见的输入源（未归档）
- 私有或已不可见的输入源（未归档）
- [hf-libraries](https://www.kaggle.com/datasets/nbroad/hf-libraries)
- 私有或已不可见的输入源（未归档）
- [WSDM Cup - Multilingual Chatbot Arena](https://www.kaggle.com/competitions/wsdm-cup-multilingual-chatbot-arena)
- [gemma-2](https://www.kaggle.com/models/emiz6413/gemma-2/Transformers/gemma-2-9b-it-4bit/1)

输入源清单是 Kaggle 当前公开列表中的挂载记录，可能不包含代码中手写的所有路径。私有依赖的内容和访问权限均未导出。

## 许可

本次公开元数据未提供可核实的 Notebook 许可证；不推断为 MIT、Apache 或其他许可，不为上游代码重新授权。保留原来源及 Notebook 内已有版权说明，详见仓库 [LICENSE_NOTES.md](../../LICENSE_NOTES.md)。
