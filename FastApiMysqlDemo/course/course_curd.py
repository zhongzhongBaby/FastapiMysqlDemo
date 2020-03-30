# 课程的增删改查模块
from fastapi import Body
from utils.mysql_utils import sql_helper
from common.entity import FindRequestBase
from common.entity import ResponseBase
from fastapi import APIRouter
from pydantic import Field

course_router = APIRouter()


class FindCourseListRequest(FindRequestBase):
    course_id: str = Field(None, title="课程id", max_length=300)
    name: str = Field(None, title="名称", max_length=300)
    subject: str = Field(..., title="科目", max_length=300)


@course_router.post("/course/find_course",
                    response_model=ResponseBase,
                    response_description=
                    '''
                    {
                    "id": 3,    #课程id
                    "name": "五年级语文",  #课程名称
                    "subject": "语文"    #课程科目
                    }   
                    ''',
                    summary="查找课程列表",
                    )
async def find_course_selective(request: FindCourseListRequest = Body(None, title="课程筛选条件")):
    '''
    这是查找课程列表的接口，可以根据id，名称，科目去筛选
    '''
    sql_exec = find_course_selective_sql_append(request)
    result = sql_helper.fetch_all2(sql_exec)
    responseVo = ResponseBase()
    responseVo.date = {"courses": result}
    return responseVo


def find_course_selective_sql_append(request: FindCourseListRequest):
    # 这里将sql拼接抽取出为一个函数，可以时主函数代码更加简洁，增强代码可读性。
    # =====sql 拼接开始=======
    # 我这里将参数直接拼接到sql中，也可以直接在执行sql时传参，个人比较青睐于这一种，方便排查sql问题
    sql_col = "*"
    sql_exec = "select %s from course where  1=1 " % sql_col
    sql_where = ""
    sql_limit = ""
    if request.course_id is not None and request.course_id != '':
        sql_where += " and id = %s" % request.course_id
    if request.name is not None and request.name != '':
        sql_where += " and name = %s" % request.name
    if request.subject is not None and request.subject != '':
        sql_where += " and subject = %s" % request.subject
    if request.limit is not None and request.page is not None:
        sql_limit += " limit %s ,  %s" % (str(request.limit * request.page), (str(request.limit)))
    sql_exec = sql_exec + sql_where + sql_limit
    # =====sql 拼接结束=======
    return sql_exec
