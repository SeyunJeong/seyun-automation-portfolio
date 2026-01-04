from jsonschema import validate, ValidationError

class ResponseSchemas:
    """API 응답 스키마 정의"""
    
    @staticmethod
    def validate_accounts_response(data):
        """내 투자 탭 응답 스키마 검증"""
        schema = {
            "type": "object", # 응답 데이터가 JSON 객체(object)임을 명시
            "properties": {   # 객체에 포함된 키들을 정의
                "accounts":           { "type": "array" },  # 'accounts' 키의 값은 배열(array) 타입
                "total_tnav":         { "type": "number" }, # 'total_tnav' 키의 값은 숫자(number) 타입
                "total_stocks":       { "type": "number" },
                "total_profit":       { "type": "number" },
                "total_profit_ratio": { "type": "number" }
            },
            "required": [ # 필수적으로 존재해야 하는 키 목록
                "accounts", 
                "total_tnav", 
                "total_stocks", 
                "total_profit", 
                "total_profit_ratio"
            ]
        }
        validate(instance=data, schema=schema)
    
    @staticmethod
    def validate_strategies_response(data):
        """전략 탭 응답 스키마 검증"""
        schema = {
            "type": "object",
            "properties": {
                "strategies": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "strategy_id": {"type": "string"},
                            "name": {"type": "string"},
                            "performance": {"type": "number"}
                        }
                    }
                }
            },
            "required": ["strategies"]
        }
        validate(instance=data, schema=schema)
    
    # @staticmethod
    # def validate_notice_response(data):
    #     """공지사항 응답 스키마 검증"""
    #     schema = {
    #         "type": "object",
    #         "properties": {
    #             "notices": {
    #                 "type": "array",
    #                 "items": {
    #                     "type": "object",
    #                     "properties": {
    #                         "notice_id": {"type": "string"},
    #                         "title": {"type": "string"},
    #                         "content": {"type": "string"},
    #                         "created_at": {"type": "string"}
    #                     }
    #                 }
    #             }
    #         },
    #         "required": ["notices"]
    #     }
    #     validate(instance=data, schema=schema)
    
    @staticmethod
    def validate_groups_response(data):
        """관심 그룹 응답 스키마 검증"""
        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "group_id": {"type": "number"},
                    "name": {"type": "string"}
                }
            }
        }
        validate(instance=data, schema=schema)
    
    @staticmethod
    def validate_stories_response(data):
        """스토리 응답 스키마 검증"""
        schema = {
            "type": "object",
            "properties": {
                "status_code": {"type": "number"},
                "message": {"type": "string"},
                "data": {
                    "type": "array",
                    # 'data' 배열의 각 항목 (주식 정보)
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "ticker": {"type": "string"},
                            "current_price": {"type": "number"},
                            "news": {
                                "type": "array",
                                # 'news' 배열의 각 항목 (개별 뉴스)
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "number"},
                                        "date": {"type": "string", "format": "date-time"},
                                        "title": {"type": "string"},
                                        "summary": {"type": "string"},
                                        "emotion": {"type": "string"},
                                        "type": {"type": "string"}
                                    },
                                    "required": ["id", "date", "title", "summary", "emotion", "type"]
                                }
                            }
                        },
                        "required": ["name", "ticker", "news"]
                    }
                }
            },
            "required": ["status_code", "message", "data"]
        }
        validate(instance=data, schema=schema)
    
    @staticmethod
    def validate_news_response(data):
        """페이징된 뉴스 응답 스키마 검증"""
        schema = {
            "type": "object",
            "properties": {
                # --- 최상위 & 페이징 정보 ---
                "status_code": {"type": "integer"},
                "message": {"type": "string"},
                "total_count": {"type": "integer"},
                "total_pages": {"type": "integer"},
                "current_page": {"type": "integer"},
                "size": {"type": "integer"},

                # --- 실제 데이터 영역 ---
                "data": {
                    "type": "object",
                    "properties": {
                        "news": {
                            "type": "array",
                            # 'news' 배열의 각 항목 (개별 뉴스)
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "date": {"type": "string", "format": "date-time"},
                                    "ticker": {"type": "string"},
                                    "title": {"type": "string"},
                                    "summary": {"type": "string"},
                                    "emotion": {"type": "string"},
                                    "name": {"type": "string"}
                                },
                                "required": ["id", "date", "title", "summary", "emotion", "name"]
                            }
                        },
                        "has_next": {"type": "boolean"}
                    },
                    "required": ["news", "has_next"]
                }
            },
            "required": [
                "status_code", "message", "data", "total_count",
                "total_pages", "current_page", "size"
            ]
        }
        
        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            print(f"스키마 검증 실패: {e.message}")
            raise
        validate(instance=data, schema=schema)