# Cell Instance Segmentation with MMDetection

细胞实例分割的推理与提交示例，包含重叠掩膜处理和 RLE 编码。

| 项目 | 记录 |
| --- | --- |
| 领域 | 生物医学图像 / 实例分割 |
| Kaggle 来源 | [how to use mmdectetion](https://www.kaggle.com/code/handudu/how-to-use-mmdectetion) |
| 来源作者 | handudu |
| 归档版本 ID | `83951341` |
| 原版本时间 | 2021-12-30T14:50:03.363Z |
| Notebook 奖牌 | 未显示 Notebook 奖牌 |
| 截至归档日票数 | 10 |

## 技术内容

MMDetection 2.14、Mask R-CNN、类别阈值、掩膜去重、RLE。

## 来源与贡献范围

基于 [KUGAI CHEN](https://www.kaggle.com/code/kugaichen/how-to-use-mmdectetion) 修改。 这里只记录公开 Notebook 的归属和衍生关系，不将团队比赛成绩或上游作者成绩归为个人成绩。

## 使用与复现边界

保留 2021 年环境与原安装单元：PyTorch 1.7 / CUDA 11.0、MMCV 和本地 wheel。需要原模型检查点；2 个输入源为私有。运行前需逐格检查旧环境安装和清理命令。

推荐从上面的 Kaggle 原页面查看 Input 和原环境，再决定是否运行。比赛数据需从原比赛自行取得并遵守其访问条件。本仓库没有打包数据、模型权重或离线安装包。

本次检查仅确认文件结构、源码保真和静态可读性；没有运行模型训练、下载依赖或执行 Notebook。Notebook 输出已清理，代码及原有注释保留。具体变更和 SHA-256 见 [provenance.json](provenance.json)。

## 原输入源

- [PyTorch 1.7.0 + Cuda Toolkit 11.0.221](https://www.kaggle.com/datasets/sreevishnudamodaran/pytorch-170-cuda-toolkit-110221)
- [MMDetection v2.14.0 ](https://www.kaggle.com/datasets/sreevishnudamodaran/mmdetectionv2140)
- [mmdetection_new](https://www.kaggle.com/datasets/kugaichen/mmdetection-new)
- [timtim](https://www.kaggle.com/datasets/kugaichen/timtim)
- 私有或已不可见的输入源（未归档）
- 私有或已不可见的输入源（未归档）
- [Sartorius - Cell Instance Segmentation](https://www.kaggle.com/competitions/sartorius-cell-instance-segmentation)

输入源清单是 Kaggle 当前公开列表中的挂载记录，可能不包含代码中手写的所有路径。私有依赖的内容和访问权限均未导出。

## 许可

本次公开元数据未提供可核实的 Notebook 许可证；不推断为 MIT、Apache 或其他许可，不为上游代码重新授权。保留原来源及 Notebook 内已有版权说明，详见仓库 [LICENSE_NOTES.md](../../LICENSE_NOTES.md)。
