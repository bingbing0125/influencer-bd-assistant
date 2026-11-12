# 🚀 AI-Powered Influencer BD Assistant

> AI 海外达人筛选与智能建联工作台 —— 面向跨境电商品牌的 Influencer Marketing / BD 全流程本地工具。
> 求职作品集项目：覆盖 **AI Prompt Engineering · AI Agent 思路 · 海外 KOL 筛选评估 · 英文商务邮件 · BD CRM · 数据分析**。

---

## 1. 项目背景与要解决的问题

跨境品牌进入海外市场时，达人营销（Influencer Marketing）传统流程高度重复：

1. 在 Instagram / TikTok / YouTube 人肉搜索达人；
2. 逐个打开主页，目测粉丝量、内容方向、受众；
3. 判断是否匹配；
4. 手写英文开发信；
5. 手动发信、记回复、做跟进；
6. 月末再用 Excel 手动统计回复率。

这个项目把上述流程整合到一个本地工作台：**评分筛选 → 个性化邮件 → Prompt 工作台 → CRM → 数据看板**。

> ⚠️ 产品目标是"建联效率提升 3× 以上"，但本仓库**不预设结论**。效率倍数由「Analytics & Efficiency」页面里你自己的真实计时计算得出，系统不会编造数字。

## 2. 产品定位

- **用户**：跨境电商品牌的 Influencer Marketing Specialist / BD。
- **场景**：以 HomeGlow（一款 $49.99 的智能氛围灯）进入美国市场为例，从 30 位美/英/加达人中筛选、建联、跟进。
- **核心原则**：
  - 本地优先（SQLite），**无需任何 API Key 即可跑通核心功能**；
  - 不爬平台、不违反 ToS；
  - 没有的数据一律标记 `Unknown`，**绝不编造粉丝数、作品、合作经历**；
  - 不真实发信，只生成邮件与管理状态。

## 3. 系统架构

```
influencer_bd_assistant/
├── app.py                  # Streamlit 入口 + 左侧导航
├── config.py               # 主题色、CRM 状态、评分权重默认值、邮件风格
├── database.py             # SQLite 持久层（品牌/达人/邮件/CRM/回复分析/效率测试/自定义Prompt）
├── seed_demo.py            # 灌入 30 条 Demo 达人 + HomeGlow 示例品牌
├── requirements.txt
├── prompts/
│   └── prompt_library.py   # 8 类 Prompt 模板（Role/Context/Task/Input/Constraints/Output/Eval）
├── modules/
│   ├── brand.py            # Module 01 品牌信息 + Brand Brief
│   ├── influencers.py      # Module 02 达人库：增删改查、CSV/Excel 导入导出、筛选、详情
│   ├── matching.py         # Module 03 100 分加权评分引擎（规则式，可解释）
│   ├── matching_page.py
│   ├── email_gen.py        # Module 04 三风格个性化英文邮件生成
│   ├── email_page.py
│   ├── prompt_page.py      # Module 05 Prompt Engineering 工作台
│   ├── crm_page.py         # Module 06 Influencer CRM（9 状态 + 跟进历史）
│   ├── reply_page.py       # Module 07 英文回复规则式解析 + 回复草稿
│   ├── overview_page.py    # Module 08 KPI / Plotly 图表 / BD 漏斗
│   └── settings_page.py    # Module 09 效率对比计时 + 权重设置
├── data/                   # SQLite 数据库自动生成于此
├── exports/                # 导出目录
└── tests/
    └── smoke_test.py       # 用 streamlit AppTest 跑遍 10 个页面
```

## 4. 技术栈

| 层 | 选型 |
|---|---|
| 前端 | Streamlit（现代 SaaS Dashboard 风格，深蓝主色、卡片式布局） |
| 数据处理 | Pandas |
| 可视化 | Plotly（KPI 卡片、饼图、柱状图、直方图、漏斗图） |
| 存储 | SQLite（标准库 sqlite3，零配置） |
| 导入导出 | openpyxl（.xlsx）+ CSV |
| AI | **第一阶段：规则式本地引擎 + Prompt 模板**（无 Key 可跑）；预留 OpenAI / Anthropic 环境变量接入位 |

## 5. 核心功能（对应模块）

| Module | 功能 | 亮点 |
|---|---|---|
| 01 Brand | 品牌/产品录入，自动生成 Brand Brief | 作为后续评分与邮件的"单一事实源" |
| 02 Database | 达人 CRUD、Excel/CSV 批量导入、多条件筛选、导出 | 缺数据留空，不补全 |
| 03 Matching | 6 维 100 分加权评分，权重可调 | 每个维度给 0–10 分 + 理由 + 数据可信度标签（real/partial/unknown）；不以粉丝量论英雄 |
| 04 Email | 三风格（Friendly / Professional / Short）批量个性化开发信 | 按 niche 自动切换场景角度（卧室改造 vs 智能家居 vs 日常生活）；附中文翻译、匹配理由、合作方式建议、3 个备选主题；一键导出 Excel |
| 05 Prompt | 8 类 Prompt 库（Research/Scoring/Outreach/Follow-up/Negotiation/Campaign/Competitor/Reply） | 自动注入品牌+达人信息；一键复制到 ChatGPT/Claude；支持粘贴结果回写；可另存自定义 Prompt |
| 06 CRM | 9 状态流转（To Contact → … → Closed） | 记录首联时间、发信时间、回复时间、下次跟进、报价、合作方式、事件历史 |
| 07 Reply | 粘贴英文回复自动解析 | 识别意向/免费样品/付费/佣金/独家/时间节点；抽取报价；风险提示；自动生成英文回复草稿并回写 CRM |
| 08 Dashboard | 8 个 KPI + 平台/国家/niche 分布 + 评分分布 + BD 漏斗 | 严格区分"已生成邮件"与"已发送邮件"，不造假 |
| 09 Efficiency | 人工 vs AI 计时对比 | 效率提升倍数 = 人工/AI；时间节省% = (人工−AI)/人工，两个指标分开展示 |

## 6. Prompt Engineering 设计

8 个模板都遵循同一结构：

```
# Role        —— 你是谁（资深 Influencer Marketing analyst / partnership manager …）
# Context     —— 品牌信息（自动注入）
# Task        —— 具体要做什么
# Input       —— 达人资料（自动注入；缺数据写 Unknown）
# Constraints —— 硬性约束：不许编造粉丝数/视频名/合作经历；Unknown 就明说
# Output Format —— 固定输出格式（表格 / 分节）
# Evaluation Criteria —— 怎么算这份输出合格
```

工作流：在系统里选 Prompt + 选达人 → 自动渲染 → 复制到 ChatGPT/Claude → 把结果粘回 → 追加到达人 notes。

## 7. 数据分析逻辑

- **Reply Rate** = Replies ÷ Emails Sent（分母必须是真实发信数，不是生成数）。
- **Qualified** = 评分 ≥ 70 的达人。
- **评分加权**：`Σ (维度分/10 × 权重%)`，权重在 Settings 调整后自动归一化到 100。
- **预算适配分**：从 `estimated_rate` 里正则抽美元数，与 `cooperation_budget` 里的预算上限对比。
- **效率提升**：必须先在页面里分别录入人工用时与 AI 用时，否则不出倍数。

## 8. 运行方法

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2.（可选）灌入 30 条 Demo 达人 + HomeGlow 示例品牌
python seed_demo.py

# 3. 启动
streamlit run app.py
# 浏览器打开 http://localhost:8501
```

Demo 数据全部在 `notes` 字段标注 `Demo Data`，**不是真实达人**。

## 9. 测试

```bash
python tests/smoke_test.py
```

会用 Streamlit 官方 `AppTest` 依次渲染 10 个页面，捕获未处理异常。

冒烟测试结果（本机）：
- 30 位达人入库；
- 评分 Top3 均为美国本土 Home Decor / Lifestyle / 高互动 mid-tier 达人（符合 HomeGlow 目标受众）；
- 三风格邮件均可生成，主题与正文随 niche 变化；
- 回复分析正确识别 "interested / asks_free_product / asks_paid"；
- 10 个页面 AppTest 渲染全部 OK，无 exception。

## 10. 项目局限性（诚实声明）

1. **第一阶段没有接 LLM API**：评分与邮件是规则引擎，不是真·GPT 生成。优点是零成本、可解释、不幻觉；缺点是个性化深度不如大模型。Prompt 工作台就是为此留的桥。
2. **不自动发信**：第一阶段只生成邮件、记录状态，不接 Gmail/Outlook 发送。
3. **不爬平台**：达人数据靠手动录入或 Excel 导入，没有对接 Modash / Upfluence 等数据源。
4. **效率提升 3× 是设计目标，不是已验证事实**：必须由你自己跑计时测试得出。
5. **30 条达人是模拟数据**，仅用于演示 UI 与流程，不要当成真实 KOL 名单外发。
6. **Demo 邮箱是 `*.example.com` 占位域名**，不可真实联系。

## 11. 求职面试讲述建议

- 讲「为什么不用 LLM 硬刚」：本地优先、可解释、不幻觉、零成本——体现产品判断。
- 讲评分模型：6 维权重、数据缺失按中性分并打标，而不是瞎猜——体现数据严谨。
- 讲邮件个性化：按 niche 簇切换角度，而不是替换名字——体现 Prompt 工程思维。
- 讲诚实指标：生成数 ≠ 发送数，效率倍数必须实测——体现业务素养。
