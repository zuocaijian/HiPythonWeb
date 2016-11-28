# HiPythonWeb 项目运行流程
---
1. app.py作为应用入口，主要是配置环境，初始化变量 app , 为app设置好 request 处理方法， response 处理方法;
2. 启动后通过 add_routes 方法将 handlers.py中的每一api与url联系起来，并制定相应的处理方法（处理方法有post和get之分，通过python的装饰器语法来判别）;
3. 在 RequestHandler 类中最先处理请求request， 根据求情的方式 post 和 get 提取请求的类型（Content-Type, 键值对参数）, 根据Content_Type 和键值对参数生成dict，交给 add_routes 中添加的方法做处理，并获取处理后的返回值;
4. 通过步骤2获取的返回值，再根据 webApp 的 reponse-factory方法返回请求的 response. 主要response的Content-Type, 返回JSON格式的数据(针对移动端), 或是返回dict+html模板生成的html页面(针对浏览器).  