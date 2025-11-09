import httpx
import asyncio
from typing import Optional, Dict
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


class AIService:
    """AI 解析服务"""
    
    def __init__(self):
        self.api_url = settings.ai_api_url
        self.model_name = settings.ai_model_name
        self.max_tokens = settings.ai_max_tokens
        self.image_server = settings.ai_image_server
    
    async def analyze_screenshot(self, image_url: str) -> Optional[Dict]:
        """
        使用 AI 分析截屏内容
        
        Args:
            image_url: 图片的 URL 地址
            
        Returns:
            解析结果字典
        """
        prompt = """请分析这张桌面截图，提供以下信息：
1. 活动类型（从以下选择一个：工作/学习/娱乐/其他）
2. 正在使用的主要应用程序或网站
3. 当前活动的简短描述（1-2句话）
4. 内容摘要（重点内容、关键词）

请以JSON格式返回，格式如下：
{
    "activity_type": "工作/学习/娱乐/其他",
    "application": "应用名称",
    "description": "活动描述",
    "content_summary": "内容摘要"
}"""
        
        try:
            # 增加超时时间到 120 秒（视觉模型处理图片需要更长时间）
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.api_url,
                    json={
                        "model": self.model_name,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": image_url}
                                    }
                                ]
                            }
                        ],
                        "max_tokens": self.max_tokens
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    # 尝试解析 JSON 响应
                    import json
                    try:
                        # 提取 JSON 部分
                        if "```json" in content:
                            json_str = content.split("```json")[1].split("```")[0].strip()
                        elif "{" in content and "}" in content:
                            start = content.index("{")
                            end = content.rindex("}") + 1
                            json_str = content[start:end]
                        else:
                            json_str = content
                        
                        parsed = json.loads(json_str)
                        return parsed
                    except json.JSONDecodeError:
                        # 如果无法解析，使用默认结构
                        logger.warning(f"Failed to parse AI response as JSON: {content}")
                        return {
                            "activity_type": "其他",
                            "application": "未知",
                            "description": content[:200],
                            "content_summary": content[:500]
                        }
                else:
                    logger.error(f"AI API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error calling AI API: {str(e)}", exc_info=True)
            return None
    
    async def generate_hourly_report(self, activities: list) -> str:
        """生成小时报告"""
        if not activities:
            return "本小时无活动记录"
        
        activities_text = "\n".join([
            f"- {a.timestamp.strftime('%H:%M')}: {a.description}"
            for a in activities[:10]  # 最多取10条
        ])
        
        prompt = f"""基于以下活动记录，生成一份简洁的小时工作总结：

{activities_text}

请总结：
1. 主要活动内容
2. 时间分配情况
3. 工作效率评价

限制在200字以内。"""
        
        try:
            # 增加超时时间到 120 秒（视觉模型处理图片需要更长时间）
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.api_url,
                    json={
                        "model": self.model_name,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 300
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("choices", [{}])[0].get("message", {}).get("content", "生成失败")
                    
        except Exception as e:
            logger.error(f"Error generating hourly report: {str(e)}")
            
        return "报告生成失败"
    
    async def generate_daily_report(self, activities: list) -> str:
        """生成日报"""
        if not activities:
            return "今日无活动记录"
        
        # 按活动类型分组
        type_counts = {}
        for a in activities:
            t = a.activity_type or "其他"
            type_counts[t] = type_counts.get(t, 0) + 1
        
        summary = f"今日共记录 {len(activities)} 次活动\n"
        summary += "活动分布：\n"
        for t, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            summary += f"- {t}: {count} 次\n"
        
        # 取一些关键活动
        key_activities = activities[::max(1, len(activities)//10)][:10]
        activities_text = "\n".join([
            f"- {a.timestamp.strftime('%H:%M')}: {a.description}"
            for a in key_activities
        ])
        
        prompt = f"""基于以下活动统计和关键活动，生成一份日报：

{summary}

关键活动：
{activities_text}

请总结：
1. 今日主要工作内容
2. 时间分配和效率
3. 建议或反思

限制在400字以内。"""
        
        try:
            # 增加超时时间到 120 秒（视觉模型处理图片需要更长时间）
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.api_url,
                    json={
                        "model": self.model_name,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 600
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("choices", [{}])[0].get("message", {}).get("content", summary)
                    
        except Exception as e:
            logger.error(f"Error generating daily report: {str(e)}")
            
        return summary


ai_service = AIService()
