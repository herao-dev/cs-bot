from __future__ import annotations
from openai import OpenAI
from config import Config
from services.vectorstore import vector_store


class RAGService:
    SYSTEM_PROMPT = """You are a professional customer support agent. Answer the user's question based on the provided context from the knowledge base.

Rules:
- Answer in the same language as the user's question.
- Base your answer ONLY on the provided context. If the context does not contain relevant information, say "抱歉，我目前的知识库中没有关于这个问题的信息。"
- Be concise and accurate. Use bullet points for lists.
- If the context includes step-by-step instructions, present them clearly.
- Cite the source document name when possible.
- Do not make up information or guess."""

    def __init__(self):
        self.client = OpenAI(
            api_key=Config.DEEPSEEK_API_KEY,
            base_url=Config.DEEPSEEK_BASE_URL,
        )

    def _format_context(self, items: list[dict]) -> str:
        parts = []
        for i, item in enumerate(items):
            parts.append(f"[Source {i + 1}] {item['content']}")
        return "\n\n---\n\n".join(parts)

    def generate(self, question: str, context_items: list[dict], history: list[dict] = None) -> str:
        context = self._format_context(context_items)

        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        if history:
            for h in history[-6:]:
                messages.append(h)

        messages.append({
            "role": "user",
            "content": f"Context:\n\n{context}\n\n---\n\nQuestion: {question}",
        })

        response = self.client.chat.completions.create(
            model=Config.DEEPSEEK_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=800,
        )

        return response.choices[0].message.content.strip()

    def chat(self, question: str, history: list[dict] = None) -> dict:
        items = vector_store.search(question)

        if not items or items[0]["score"] < 0.03:
            return {
                "answer": "抱歉，我目前的知识库中没有关于这个问题的信息。请尝试用其他方式提问，或联系管理员补充相关文档。",
                "sources": [],
            }

        answer = self.generate(question, items, history)

        return {
            "answer": answer,
            "sources": [
                {"doc_id": it["doc_id"], "score": it["score"], "excerpt": it["content"][:200]}
                for it in items[:3]
            ],
        }


rag_service = RAGService()
