# 06-获取token
    
**简要描述：** 

通过appid获取token(带token接口练习)

**请求URL：** 
` http://127.0.0.1:5000/api/user/getToken/?appid=136425`
  
**请求方式：**
GET 

**参数**

|参数名   |必选|类型  |说明   |
|:--------|:---|:-----|-------|
|appid    |是  |String|校验id |


 **返回示例**
成功：

token=b3f80a264a3d11e8956b54ee75704366

失败：

appid错误

**备注**
appid使用136425



