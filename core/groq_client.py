import time
from openai import AsyncOpenAI
from .role_config import get_intimacy_prompt

TEXT_MODEL = "llama-3.3-70b-versatile"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

class GroqClient:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.model_name = TEXT_MODEL
        self._rate_limit: dict[str, list[float]] = {}

    def _check_rate_limit(self, user_id: str) -> bool:
        now = time.time()
        if user_id not in self._rate_limit:
            self._rate_limit[user_id] = []

        self._rate_limit[user_id] = [ts for ts in self._rate_limit[user_id] if now - ts < 60]

        if len(self._rate_limit[user_id]) >= 3:
            return False

        self._rate_limit[user_id].append(now)
        return True

    def _build_system_prompt(self, role_config: dict, intimacy_prompt: str) -> str:
        return f"{role_config['system_prompt']}\n\n{intimacy_prompt}"

    def _build_history(self, history: list[dict]) -> list[dict]:
        groq_history = []
        for msg in history:
            role = "assistant" if msg["is_bot"] else "user"
            groq_history.append({
                "role": role,
                "content": msg["content"]
            })
        return groq_history

    async def generate(self, prompt: str, system_instruction: str = None) -> str:
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages
        )
        return response.choices[0].message.content

    async def chat(self, user_id: str, message: str, role_config: dict, history: list[dict], intimacy_score: int, image_bytes: bytes = None, mime_type: str = None) -> str:
        if not self._check_rate_limit(user_id):
            raise Exception("Bạn nhắm hơi nhanh rồi, hãy chậm lại một chút nhé!")

        try:
            intimacy_prompt = get_intimacy_prompt(intimacy_score)
            system_prompt = self._build_system_prompt(role_config, intimacy_prompt)
            formatted_history = self._build_history(history)

            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(formatted_history)

            if image_bytes:
                import base64
                img_b64 = base64.b64encode(image_bytes).decode("utf-8")

                if mime_type:
                    actual_mime = mime_type
                else:
                    sig = image_bytes[:8]
                    if sig[:3] == b'\xff\xd8\xff':
                        actual_mime = "image/jpeg"
                    elif sig[:8] == b'\x89PNG\r\n\x1a\n':
                        actual_mime = "image/png"
                    elif sig[:3] == b'GIF':
                        actual_mime = "image/gif"
                    elif sig[:4] == b'RIFF' and sig[8:12] == b'WEBP':
                        actual_mime = "image/webp"
                    else:
                        actual_mime = "image/png"
                content = []
                if message:
                    content.append({"type": "text", "text": message})
                else:
                    content.append({"type": "text", "text": "Hãy mô tả và phân tích ảnh này cho tôi."})
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{actual_mime};base64,{img_b64}"}
                })
                messages.append({"role": "user", "content": content})
                model = VISION_MODEL
            else:
                messages.append({"role": "user", "content": message})
                model = self.model_name

            response = await self.client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Groq API Error: {e}")
            raise Exception("Xin lỗi, tôi đang gặp chút sự cố kết nối. Vui lòng thử lại sau nhé!")
