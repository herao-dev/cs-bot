# CS Bot — 智能客服 FAQ 机器人

基于 RAG 的智能客服系统，支持文档上传构建知识库与手动编辑 FAQ 问答对，AI 基于知识库精准回答用户问题。

## 核心功能

- **RAG 问答**：上传 PDF / Word / Markdown / TXT 文档后 AI 基于内容回答
- **FAQ 管理**：手动添加标准问答对，支持分类标签与搜索，提问优先匹配 FAQ
- **多轮对话**：保留上下文连续提问，支持多会话切换，历史持久化不丢失
- **快捷回复**：预置回复模板管理，按标签分类（售后/产品/物流/支付）
- **反馈统计**：答案点赞/踩，仪表盘统计会话数、消息数、好评率

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python / Flask / scikit-learn (TF-IDF 检索) / DeepSeek API |
| 前端 | Vue 3 / TypeScript / Vite / Pinia |
| 检索 | TF-IDF + 余弦相似度，char_wb 分词适配中英文 |

## 快速开始

### 1. 后端

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env          # 编辑填入 DEEPSEEK_API_KEY
python app.py                 # → http://localhost:5199
```

### 2. 前端

```bash
cd frontend
npm install
npm run dev                   # → http://localhost:3101
```

## 项目结构

```
ai/
├── backend/
│   ├── app.py                # Flask 入口
│   ├── config.py             # 配置
│   ├── services/             # 文档解析 / TF-IDF 检索 / RAG / FAQ / 会话
│   └── routes/               # 对话 / 知识库 / 统计 / 快捷回复 API
├── frontend/
│   └── src/
│       ├── views/            # 仪表盘 / 对话 / 历史 / 快捷回复 / 知识库
│       ├── stores/           # Pinia 状态管理
│       └── api/              # Axios API 封装
└── README.md




```

<img width="1280" height="596" alt="image" src="https://github.com/user-attachments/assets/0c05231e-0b6f-4665-946f-74e245353dea" />

<img width="1276" height="604" alt="image" src="https://github.com/user-attachments/assets/50017cac-d210-480f-8f0b-8960f28dfcb9" />

<img width="1278" height="602" alt="image" src="https://github.com/user-attachments/assets/e47fac56-168d-4b20-b8db-4e30222a6158" />

## 贡献者

- [herao-dev](https://github.com/herao-dev)
