import re
import json
import asyncio
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime, timedelta


# --------------- 数据结构定义 ---------------
class CourseSchedule(BaseModel):
    title: str
    start: str
    end: str
    day: str
    locate: str


class ExamNotice(BaseModel):
    name: str
    type: str
    place: str
    date: str
    time: str


class GradeRecord(BaseModel):
    name: str
    date: str
    score: float
    credit: float


# --------------- 数据管理类 ---------------
def fuzzy_match(source: str, target: str) -> bool:
    """模糊匹配算法"""
    source = re.sub(r'\W+', '', source).lower()
    target = re.sub(r'\W+', '', target).lower()
    return target in source


async def safe_load(file_path: str, schema, data_key: str):
    """安全加载数据并验证"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # 从指定键获取数据数组
            items = data.get(data_key, [])
            return [schema(**item) for item in items]
    except json.JSONDecodeError as e:
        print(f"JSON解析错误 ({file_path}): {str(e)}")
        return []
    except KeyError as e:
        print(f"键缺失错误 ({file_path}): {str(e)}")
        return []
    except Exception as e:
        print(f"意外错误 ({file_path}): {str(e)}")
        return []


class AcademicDataManager:
    def __init__(self):
        self.courses: List[CourseSchedule] = []
        self.exams: List[ExamNotice] = []
        self.grades: List[GradeRecord] = []

    async def load_all_data(self):
        """异步加载所有数据（修正版）"""
        # 并行加载所有数据
        self.courses, self.exams, self.grades = await asyncio.gather(
            safe_load("deepseek_api/src/courses.json", CourseSchedule, "courses"),
            safe_load("deepseek_api/src/exams.json", ExamNotice, "notice"),
            safe_load("deepseek_api/src/grades.json", GradeRecord, "datas")
        )

        # 数据排序
        self.courses.sort(key=lambda x: (x.day, x.start))
        self.exams.sort(key=lambda x: x.date)
        self.grades.sort(key=lambda x: x.date)

    # --------------- 查询方法 ---------------
    def search_courses(self, days=7, keyword=None):
        """查询课程"""
        end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        filtered = [c for c in self.courses if c.day <= end_date]
        if keyword:
            filtered = [c for c in filtered if fuzzy_match(c.title, keyword)]
        return [c.dict() for c in filtered]

    def search_exams(self, exam_type=None, keyword=None) -> List[Dict]:
        """查询考试"""
        filtered = self.exams
        if exam_type and exam_type.lower() != "all":
            filtered = [e for e in filtered if fuzzy_match(e.type, exam_type)]
        if keyword:
            filtered = [e for e in filtered if fuzzy_match(e.name, keyword)]
        return [e.dict() for e in filtered]

    def search_grades(self, course_name=None):
        """查询成绩"""
        filtered = self.grades
        if course_name:
            filtered = [g for g in filtered if fuzzy_match(g.name, course_name)]
        return [g.dict() for g in filtered]


# --------------- 工具集成类 ---------------
class AcademicQueryTools:
    def __init__(self):
        self.data = AcademicDataManager()
        self.initialized = False

    async def initialize(self):
        if not self.initialized:
            await self.data.load_all_data()
            self.initialized = True

    async def safe_query(self, func, *args, **kwargs):
        """安全执行查询"""
        try:
            if not self.initialized:
                await self.initialize()
            return func(*args, **kwargs)
        except Exception as e:
            print(f"查询错误: {str(e)}")
            return []

    # --------------- 对外接口 ---------------
    async def query_courses(self, days=7, keyword=None):
        results = await self.safe_query(self.data.search_courses, days, keyword)
        return {"status": "success", "data": {"courses": results, "days": days, "keyword": keyword or "全部"}}

    async def query_exams(self, exam_type=None, keyword=None):
        results = await self.safe_query(self.data.search_exams, exam_type, keyword)
        return {"status": "success", "data": {"exams": results, "type": exam_type or "全部", "keyword": keyword or "全部"}}

    async def query_grades(self, course_name=None):
        results = await self.safe_query(self.data.search_grades, course_name)
        return {"status": "success", "data": {"grades": results, "course": course_name or "全部"}}
