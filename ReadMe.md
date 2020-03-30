# FastApi+mysql 快速搭建web后端接口框架


## 项目描述：
最近从java转来学习FastApi，想要快速搭建一个FastApi+mysql的后端接口框架，但是网上没有找到demo，所以自己简单写了一个，做了一些简单的封装，希望对和我一样的新学者有所帮助。<br>

## 项目特点：
1.使用数据源访问mysql<br>
2.实现中文api文档<br>
3.数据验证<br>
api文档实现效果：
![image](https://note.youdao.com/yws/api/personal/file/39E175C1C29846E5AE92B1A8D222EA95?method=download&shareKey=428a760f737abeffd2b59b357ede0c35)

## 运行步骤：
Terminal窗口运行：

```
icorn main:app --reload
```
**解读**：<br>
main ->main.py <br>
app ->生成的FastApi对象<br>
-- reload -> 热编译,无须重启服务<br>

命令运行之后会看到
```
?[32mINFO?[0m:     Uvicorn running on ?[1mhttp://127.0.0.1:8000?[0m (Press CTRL+C to quit)
?[32mINFO?[0m:     Started reloader process [?[36m?[1m13208?[0m]
?[32mINFO?[0m:     Started server process [?[36m18004?[0m]
?[32mINFO?[0m:     Waiting for application startup.
?[32mINFO?[0m:     Application startup complete.

```
说明服务已经启动。

访问http://127.0.0.1:8000 即可看到api文档。


