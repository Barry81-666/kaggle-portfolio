# Bacterial Flagellar Motor Detection

从细菌断层图像定位鞭毛马达，包含多模型、多切片推理与融合。

| 项目 | 记录 |
| --- | --- |
| 领域 | 计算生物学 / 三维目标定位 |
| Kaggle 来源 | [P1_1_0.65 74d43e](https://www.kaggle.com/code/handudu/p1-1-0-65-74d43e) |
| 来源作者 | handudu |
| 归档版本 ID | `243588125` |
| 原版本时间 | 2025-06-04T02:38:40.553Z |
| Notebook 奖牌 | 未显示 Notebook 奖牌 |
| 截至归档日票数 | 0 |

## 技术内容

YOLOv10 / MHAF-YOLO、测试时增强、加权框融合、三维 NMS、批量图像预加载。

## 来源与贡献范围

Kaggle 标记为 fork，父 Notebook ID：`84148436`；其作者和公开链接当前不可见。 这里只记录公开 Notebook 的归属和衍生关系，不将团队比赛成绩或上游作者成绩归为个人成绩。

## 使用与复现边界

需要原 Notebook 挂载的多个模型权重；3 个输入源当前标记为私有。标题里的数值和第三方排行榜记录不作为本仓库的获奖或最终排名证明。

推荐从上面的 Kaggle 原页面查看 Input 和原环境，再决定是否运行。比赛数据需从原比赛自行取得并遵守其访问条件。本仓库没有打包数据、模型权重或离线安装包。

本次检查仅确认文件结构、源码保真和静态可读性；没有运行模型训练、下载依赖或执行 Notebook。Notebook 输出已清理，代码及原有注释保留。具体变更和 SHA-256 见 [provenance.json](provenance.json)。

## 原输入源

- 私有或已不可见的输入源（未归档）
- 私有或已不可见的输入源（未归档）
- 私有或已不可见的输入源（未归档）
- [mahf_yolo_train](https://www.kaggle.com/datasets/playwithme/mahf-yolo-train)
- [BYU - Locating Bacterial Flagellar Motors 2025](https://www.kaggle.com/competitions/byu-locating-bacterial-flagellar-motors-2025)
- [MHAFYOLO](https://www.kaggle.com/models/yyyy0201/mhafyolo/PyTorch/default/1)

输入源清单是 Kaggle 当前公开列表中的挂载记录，可能不包含代码中手写的所有路径。私有依赖的内容和访问权限均未导出。

## 许可

本次公开元数据未提供可核实的 Notebook 许可证；不推断为 MIT、Apache 或其他许可，不为上游代码重新授权。保留原来源及 Notebook 内已有版权说明。
