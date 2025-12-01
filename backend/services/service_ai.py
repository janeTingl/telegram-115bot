import logging
import json
from typing import Optional, Dict, Any
from openai import AsyncOpenAI

logger = logging.getLogger("AIService")

class AIService:
    def __init__(self):
        self.client: Optional[AsyncOpenAI] = None
        self.model: str = "gpt-3.5-turbo"
        self.enabled: bool = False

    def init_config(self, app_config: Dict[str, Any]):
        ai_conf = app_config.get("organize", {}).get("ai", {})
        self.enabled = ai_conf.get("enabled", False)
        if self.enabled and ai_conf.get("apiKey"):
            self.client = AsyncOpenAI(
                api_key=ai_conf["apiKey"],
                base_url=ai_conf.get("baseUrl", "https://api.openai.com/v1")
            )
            self.model = ai_conf.get("model", "gpt-3.5-turbo")

    async def parse_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        if not self.enabled or not self.client: return None
        prompt = f"""
        请分析文件名: "{filename}"。
        返回纯JSON: {{"title": "标题", "year": "年份", "season": 季号(int), "episode": 集号(int)}}
        无法识别设为null。
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"): content = content[7:-3]
            return json.loads(content)
        except Exception as e:
            logger.error(f"AI Error: {e}")
            return None

ai_service = AIService()
