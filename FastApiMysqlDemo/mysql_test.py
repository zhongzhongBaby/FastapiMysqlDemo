import pymysql

db = pymysql.connect("127.0.0.1", "root", "123456", "demo")
cursor = db.cursor()


def add_course():
    sql = "INSERT INTO course(id,name)values('%s','%s')" % ("12", "222222")
    try:
        cursor.execute(sql)
        db.commit()
        return "ok"
    except Exception as e:
        print(str(e))
        db.rollback()
        return "err"
    db.close()


def find_course():
    sql1 = 'SELECT * from course WHERE 1=1 order by id limit 0 , 10'
    cursor.execute(sql1)
    pnlist = []
    alldata = cursor.fetchall()
    count = cursor.rowcount;
    for singl_company in alldata:
        pnlist.append(singl_company[0])
    print('列表总长度: ', count)
    print(alldata)


find_course()
