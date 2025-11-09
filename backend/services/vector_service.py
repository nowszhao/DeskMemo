import os
# 必须在导入 chromadb 之前设置
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


class VectorService:
    """向量存储和检索服务"""
    
    def __init__(self):
        os.makedirs(settings.chroma_path, exist_ok=True)
        
        # 完全禁用 telemetry
        self.client = chromadb.PersistentClient(
            path=settings.chroma_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 使用默认 embedding（轻量级，内存占用小）
        # 对于 CPU 服务器，这是最佳选择
        # 如果需要更好的中文支持，可以考虑部署独立的 embedding 服务
        self.collection = self.client.get_or_create_collection(
            name="activities",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_activity(self, activity_id: str, text: str, metadata: Dict) -> bool:
        """添加活动到向量数据库"""
        try:
            self.collection.add(
                ids=[activity_id],
                documents=[text],
                metadatas=[metadata]
            )
            return True
        except Exception as e:
            logger.error(f"Error adding to vector DB: {str(e)}")
            return False
    
    def search_similar(self, query: str, limit: int = 10) -> List[Dict]:
        """语义搜索"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            # 格式化结果
            items = []
            if results and results.get("ids") and len(results["ids"]) > 0:
                for i, doc_id in enumerate(results["ids"][0]):
                    items.append({
                        "id": doc_id,
                        "distance": results["distances"][0][i] if "distances" in results else 0,
                        "metadata": results["metadatas"][0][i] if "metadatas" in results else {},
                        "document": results["documents"][0][i] if "documents" in results else ""
                    })
            
            return items
        except Exception as e:
            logger.error(f"Error searching vector DB: {str(e)}")
            return []
    
    def delete_activity(self, activity_id: str) -> bool:
        """删除活动"""
        try:
            self.collection.delete(ids=[activity_id])
            return True
        except Exception as e:
            logger.error(f"Error deleting from vector DB: {str(e)}")
            return False


vector_service = VectorService()
