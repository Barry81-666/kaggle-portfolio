# RSNA Knee MRI Inference

较新的膝关节 MRI 推理脚本，内含可独立阅读的 22 个 rsna Python 模块。

| 项目 | 记录 |
| --- | --- |
| 领域 | 医学影像 / 分类推理 |
| Kaggle 来源 | [rsna-knee-teacher-probs-exp017-v1-infer](https://www.kaggle.com/code/handudu/rsna-knee-teacher-probs-exp017-v1-infer) |
| 来源作者 | handudu |
| 归档版本 ID | `358098927` |
| 原版本时间 | 2026-10-13T19:03:54.023Z |
| Notebook 奖牌 | 未显示 Notebook 奖牌 |
| 截至归档日票数 | 0 |

## 技术内容

模型构建、DICOM 处理、折分、训练、评估、推理与提交格式验证。

## 来源与贡献范围

公开列表未标记为 fork；这不等同于完整原创性审计。 这里只记录公开 Notebook 的归属和衍生关系，不将团队比赛成绩或上游作者成绩归为个人成绩。

## 使用与复现边界

原公开脚本内嵌 gzip/base64 源码包。本仓库另将其安全解包为 source/，仅静态检查，没有运行安装、训练或推理。检查点输入为私有，无法用当前公开材料完整复现。当前比赛结果不作为获奖证明。

推荐从上面的 Kaggle 原页面查看 Input 和原环境，再决定是否运行。比赛数据需从原比赛自行取得并遵守其访问条件。本仓库没有打包数据、模型权重或离线安装包。

`source/rsna/` 是从原脚本内嵌源码包解出的可阅读源码；`inference.py` 保持原样。

本次检查仅确认文件结构、源码保真和静态可读性；没有运行模型训练、下载依赖或执行 Notebook。Notebook 输出已清理，代码及原有注释保留。具体变更和 SHA-256 见 [provenance.json](provenance.json)。

## 原输入源

- 私有或已不可见的输入源（未归档）
- [RSNA Knee Abnormality Detection](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection)

输入源清单是 Kaggle 当前公开列表中的挂载记录，可能不包含代码中手写的所有路径。私有依赖的内容和访问权限均未导出。

## 许可

本次公开元数据未提供可核实的 Notebook 许可证；不推断为 MIT、Apache 或其他许可，不为上游代码重新授权。保留原来源及 Notebook 内已有版权说明。
