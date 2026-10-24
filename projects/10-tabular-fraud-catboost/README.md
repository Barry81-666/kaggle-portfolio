# Tabular Fraud Classification · CatBoost

简洁的表格分类示例，覆盖类别变量、十折验证和概率集成。

| 项目 | 记录 |
| --- | --- |
| 领域 | 数据科学 / 表格分类 |
| Kaggle 来源 | [tianchi_finance](https://www.kaggle.com/code/handudu/tianchi-finance) |
| 来源作者 | handudu |
| 归档版本 ID | `116279535` |
| 原版本时间 | 2023-01-13T16:25:30.013Z |
| Notebook 奖牌 | 未显示 Notebook 奖牌 |
| 截至归档日票数 | 3 |

## 技术内容

CatBoostClassifier、LabelEncoder、StratifiedKFold、AUC。

## 来源与贡献范围

公开列表未标记为 fork；这不等同于完整原创性审计。 这里只记录公开 Notebook 的归属和衍生关系，不将团队比赛成绩或上游作者成绩归为个人成绩。

## 使用与复现边界

输入数据为私有，没有归档原始保险数据。原验证 AUC 使用硬分类预测，且编码器拟合于合并的训练/测试表；若扩展为严谨实验，应改用折内预处理和概率 AUC。归档保留原代码，不标注奖牌。

推荐从上面的 Kaggle 原页面查看 Input 和原环境，再决定是否运行。比赛数据需从原比赛自行取得并遵守其访问条件。本仓库没有打包数据、模型权重或离线安装包。

本次检查仅确认文件结构、源码保真和静态可读性；没有运行模型训练、下载依赖或执行 Notebook。Notebook 输出已清理，代码及原有注释保留。具体变更和 SHA-256 见 [provenance.json](provenance.json)。

## 原输入源

- 私有或已不可见的输入源（未归档）

输入源清单是 Kaggle 当前公开列表中的挂载记录，可能不包含代码中手写的所有路径。私有依赖的内容和访问权限均未导出。

## 许可

本次公开元数据未提供可核实的 Notebook 许可证；不推断为 MIT、Apache 或其他许可，不为上游代码重新授权。保留原来源及 Notebook 内已有版权说明，详见仓库 [LICENSE_NOTES.md](../../LICENSE_NOTES.md)。
