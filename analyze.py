# -*- coding: utf-8 -*-
"""城市收缩文献结构化分析 —— 改写自论文附录代码。

原附录用 GPT-4-turbo + openai 0.x 老写法（openai.ChatCompletion.create），
在 openai>=1.0 下已无法运行。这里改为：
  - 新版 openai SDK（client.chat.completions.create）
  - 智谱 GLM-4-Flash（免费，OpenAI 兼容接口）
  - MAX_FILES=3，只跑 3 篇验证流程
"""
import os
import csv
import json
import time
from openai import OpenAI

# 智谱 GLM 的 OpenAI 兼容端点；key 从环境变量读，没有则用占位
API_KEY = os.getenv("ZHIPU_API_KEY", "your-api-key-here")
BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
MODEL = "glm-4-flash"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# 文件路径
DATA_DIR = "./data/articles"
STRUCTURED_OUTPUT = os.path.join(DATA_DIR, "structured_output.csv")

# 参数
MAX_FILES = 3      # 只处理 3 篇做验证
SLEEP_TIME = 1.0
MAX_CHARS = 50000  # 单篇截断，避免超 token（GLM-4-Flash 上下文较大）

# 情感分析（sentiment）领域 28 题标准化问卷，来自《标准化问题.docx》
# 要求模型用中文回答，并尽量从给定选项中选择。
QUESTIONS = [
    # 一、基础信息类（6题）
    "1.【基础信息】该研究的核心目标是什么？（单选：Sentiment分类模型优化 / 特定场景Sentiment分析应用 / Sentiment影响因素挖掘 / Sentiment与其他变量关联研究 / 其他）",
    "2.【基础信息】研究的Sentiment分析对象是哪种文本类型？（多选：社交媒体评论（如Twitter、微博）/ 电商商品评价 / 新闻报道 / 金融文本（如财报、股吧）/ 医疗反馈 / 政策文本 / 其他）",
    "3.【基础信息】研究覆盖的时间范围或数据时效性如何？（单选：实时动态数据 / 历史静态数据（标注具体年份范围）/ 无明确时间限定）",
    "4.【基础信息】文献的研究尺度是？（单选：宏观领域层面（如某行业整体）/ 中观群体层面（如某类用户）/ 微观文本层面（如单条评论）/ 跨尺度）",
    "5.【基础信息】数据来源具体是？（需明确：公开数据集名称（如IMDB、AmazonReviews）/ 自有爬取数据（标注平台）/ 合作机构提供数据 / 其他）",
    "6.【基础信息】数据样本量及标注情况如何？（需包含：样本总量 + 标注方式（人工/自动/半监督）+ 标注类别（如二分类正面/负面；多分类等））",
    # 二、技术方法类（8题）
    "7.【技术方法】该研究采用的核心Sentiment分析方法属于哪类？（单选：词典法（如VADER、LIWC）/ 传统机器学习（如SVM、LR、RF）/ 深度学习（如CNN、LSTM、BERT、GPT类大模型）/ 混合方法（如词典+机器学习）/ 其他）",
    "8.【技术方法】若使用深度学习模型，是否对基础模型进行改进？（单选：无改进（直接使用预训练模型）/ 模型结构改进（如注意力机制、多模态融合）/ 数据增强改进（如回译、同义词替换）/ 其他改进）",
    "9.【技术方法】研究中使用的具体工具或框架有哪些？（多选：Python库（NLTK、TextBlob、Scikit-learn、PyTorch、TensorFlow）/ 商业工具（如IBMWatson、GoogleCloudNLP）/ 自定义代码框架 / 其他）",
    "10.【技术方法】模型评估采用了哪些核心指标？（多选：准确率Accuracy / 精确率Precision / 召回率Recall / F1值 / AUC-ROC / 混淆矩阵 / 人工评估一致性（如Kappa系数）/ 其他）",
    "11.【技术方法】研究是否处理了Sentiment分析中的典型挑战？（多选：讽刺/反讽Sarcasm处理 / 歧义句消歧 / slang俚语或网络用语识别 / 跨语言Sentiment迁移 / 领域适配 / 未处理上述挑战）",
    "12.【技术方法】若涉及多模态Sentiment分析（文本+图像+语音），多模态数据如何融合？（单选：早期融合（数据层）/ 中期融合（特征层）/ 晚期融合（结果层）/ 不涉及多模态）",
    "13.【技术方法】研究是否公开了代码或模型权重？（单选：GitHub公开链接 / 期刊附件提供 / 仅描述方法未公开 / 需申请获取）",
    "14.【技术方法】模型训练的硬件环境或计算成本是否提及？（单选：明确提及（如GPU型号、训练时长）/ 简要提及（如使用云服务器）/ 未提及）",
    # 三、应用场景类（5题）
    "15.【应用场景】该研究的具体应用领域是？（单选：社交媒体舆情监测 / 电商用户满意度分析 / 金融市场情绪预测 / 公共政策接受度评估 / 医疗患者反馈分析 / 产品口碑管理 / 其他领域）",
    "16.【应用场景】场景下的核心研究问题是什么？（需简洁描述，如“通过电商评论分析用户对某类产品的负面反馈焦点”）",
    "17.【应用场景】该场景下Sentiment分析面临的特有挑战是什么？（如金融文本专业术语多/社交媒体实时性要求高/医疗文本隐私保护/政策文本语义抽象）",
    "18.【应用场景】研究是否结合场景需求设计了专属Sentiment指标？（单选：是（举例说明）/ 否（使用通用指标）/ 未提及）",
    "19.【应用场景】场景中的利益相关方（企业、政府、用户）如何利用研究结果？（简述）",
    # 四、研究发现与价值类（6题）
    "20.【发现与价值】研究的核心结论是什么？（需简洁，如“BERT在金融文本Sentiment分类中F1比SVM高12%”）",
    "21.【发现与价值】该研究的理论贡献体现在哪里？（单选：提出新的Sentiment分类框架 / 改进现有模型的鲁棒性或效率 / 验证某类因素对Sentiment的影响机制 / 无明显理论贡献，以应用为主）",
    "22.【发现与价值】研究的实践价值或落地效果如何？（单选：有实际案例验证 / 仅通过模拟数据验证 / 未做效果验证仅提出方法 / 提及落地挑战）",
    "23.【发现与价值】研究承认的自身局限性有哪些？（多选：数据样本偏差 / 模型泛化能力差 / 未考虑长期动态变化 / 评估指标单一 / 未讨论伦理风险 / 未提及局限性）",
    "24.【发现与价值】研究是否提及Sentiment分析中的伦理问题？（单选：讨论算法偏见 / 提及数据隐私保护措施 / 未讨论伦理问题）",
    "25.【发现与价值】研究结果与同领域现有研究是否一致？（单选：大部分一致补充细节 / 部分不一致提出新观点 / 完全相悖解释原因 / 未与现有研究对比）",
    # 五、对比与展望类（3题）
    "26.【对比展望】该研究与同领域最新研究（近3年）的核心差异是什么？（如数据规模更大/首次将大模型应用于该细分场景/提出新评估维度）",
    "27.【对比展望】研究明确提出的未来研究方向有哪些？（多选：多模态深度融合 / 跨语言迁移学习 / 实时动态追踪 / 小样本/零样本适配 / 结合知识图谱 / 未提出明确方向）",
    "28.【对比展望】该研究的方法或结论是否可迁移到其他Sentiment应用场景？（单选：可迁移（举例）/ 部分可迁移（需适配）/ 不可迁移（高度依赖当前场景）/ 未讨论迁移性）",
]

HEADERS = ["File ID"] + [f"Q{i+1}" for i in range(len(QUESTIONS))]


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        with open(path, "r", encoding="latin-1", errors="ignore") as f:
            return f.read()


def ask_model(article_text, question):
    """查询 GLM-4-Flash 做结构化抽取"""
    prompt = (
        f"以下是一篇学术论文的内容：\n{article_text}\n\n"
        f"请仅根据这篇论文回答下面的问题。要求：用中文回答；"
        f"如果是单选/多选题，先给出选中的选项，再用一句话简要说明依据；"
        f"如果论文中没有相关信息，明确回答“文中未提及”，不要编造。\n问题：{question}"
    )
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "你是一名严谨的科研助理，擅长从情感分析（sentiment analysis）相关的学术论文中做结构化信息抽取。只依据论文内容作答，保持高准确度和一致性，绝不编造论文中没有的信息。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=600,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"  Error: {e}")
        return "Error"


def phase3_extract_structure():
    print("Phase 3: 结构化信息抽取 (GLM-4-Flash)")
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".txt")]
    files = sorted(files)[:MAX_FILES]

    results = []
    for i, file in enumerate(files):
        filepath = os.path.join(DATA_DIR, file)
        print(f"\n处理文件 {i+1}/{len(files)}: {file}")
        article = read_file(filepath)[:MAX_CHARS]
        row = [file]
        for j, question in enumerate(QUESTIONS):
            print(f"  抽取 Q{j+1}/{len(QUESTIONS)}")
            row.append(ask_model(article, question))
            time.sleep(SLEEP_TIME)
        results.append(row)

    with open(STRUCTURED_OUTPUT, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        writer.writerows(results)
    print(f"\n完成，结果写入 {STRUCTURED_OUTPUT}")
    return results


def main():
    print("城市收缩文献分析（3 篇验证）")
    print("=" * 50)
    if API_KEY == "your-api-key-here":
        print("错误：未设置 ZHIPU_API_KEY 环境变量")
        return
    os.makedirs(DATA_DIR, exist_ok=True)
    phase3_extract_structure()


if __name__ == "__main__":
    main()
