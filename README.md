## 更新日志：
   2026年1月31日 21:01:52：修复删除对话后对方再次发送消息时被转发到General，导致无法回复的问题
# Telegram 私聊转发机器人 (PM Forwarder Bot)

这是一个基于 Python 的 Telegram 机器人，可以将用户发送给机器人的私聊消息转发到你指定的群组，并支持在群组中回复用户。
<img width="1015" height="941" alt="image" src="https://github.com/user-attachments/assets/cacc4b94-42bb-4cf0-939e-885cbbb31eee" />


## ✨ 功能特点
- 自定义验证问题和密码，杜绝广告骚扰
- 每个私聊都相互独立，回复更方便，再也不会混在一起了
- 无需回复用户的消息才可以发送，直接发送消息即可，就像普通聊天一样方便
- 收到私聊消息自动转发到管理群。
- 在管理群回复（引用消息），自动转发给原用户。
- 支持文字、图片、视频、贴纸等多种媒体格式。
- 新用户自动发送欢迎/验证卡片。
- 自动重建：管理员误删话题后，用户再次发消息会自动恢复连接。
- **数据持久化**：重启不会丢失用户数据。

## 🚀 事先准备项目：
1.tg机器人申请好的token
（没有的话自己去 https://t.me/BotFather 进行申请，发送 /newbot 再根据提示依次输入自己机器人的名称、用户名即可）

<img width="437" height="286" alt="image" src="https://github.com/user-attachments/assets/5a16772f-7232-4d5b-b328-7d65fde94b13" />

2.自己查看消息的群组ID（-100开头的）
创建一个群组，拉自己刚才创建的机器人到自己的群组内，给机器人管理员权限(一定要是私有群组，里面只有你和机器人两个人)

<img width="270" height="340" alt="image" src="https://github.com/user-attachments/assets/9b42820a-b48c-4237-ab85-de1c865bffad" />

<img width="396" height="254" alt="image" src="https://github.com/user-attachments/assets/a4564c74-6cdf-4f94-9897-786a18d2ac04" />

点击群组设置，开启【话题模式】，选择【列表】

<img width="812" height="825" alt="image" src="https://github.com/user-attachments/assets/cef0df0c-422e-4db2-a76d-43939aaafb03" />

Windows客户端点击群组，可以显示群组ID，在这个前面加 -100即可，即 -113320xxxxx

<img width="1018" height="923" alt="image" src="https://github.com/user-attachments/assets/123d4305-aee0-4814-bd5f-2eca527e049e" />

如果自己不知道怎么获取，可以邀请我的机器人进群组 https://t.me/lige0407_bot 无需给予任何权限，在群内发送 /id  就可以看见群组ID，再移除机器人即可

<img width="389" height="606" alt="image" src="https://github.com/user-attachments/assets/6ca50743-2e36-4372-8bbb-3545d3f69163" />

<img width="804" height="169" alt="image" src="https://github.com/user-attachments/assets/9bfc02a7-a3b1-4b4d-b431-842119eaa93c" />

## 🚀 Zeabur 一键部署指南

1. **Fork 本项目** 到你的 GitHub 账号。
2. 登录 [Zeabur](https://zeabur.com)，点击 **Create New Project**。
点击【创建项目】

 <img width="1374" height="639" alt="image" src="https://github.com/user-attachments/assets/0f55f084-73ad-45ea-b39e-792059d31d6f" />
点击【共享集群】，免费试用集群随便二选一都可以，最后点击右下角的【创建项目】

<img width="914" height="1143" alt="image" src="https://github.com/user-attachments/assets/c2ff5601-415b-43f6-8241-441b59484603" />

3.点击【部署新服务】

<img width="430" height="442" alt="image" src="https://github.com/user-attachments/assets/bfeb4f88-b92d-4293-8222-422f566abb42" />

 选择【从github部署】
 
<img width="603" height="599" alt="image" src="https://github.com/user-attachments/assets/a88a5848-927d-4af6-83a3-4593fef852db" />

4. 选择 **Deploy New Service** -> **GitHub** -> 选择你刚才 Fork 的仓库。

<img width="633" height="193" alt="image" src="https://github.com/user-attachments/assets/01683fde-1ce2-4dfb-ab0e-01d70f049eef" />

5.点击【配置】

<img width="719" height="373" alt="image" src="https://github.com/user-attachments/assets/649a44ce-6dd7-4fda-b10f-973739174df9" />

添加以下变量：
| 变量名 | 必填 | 说明 | 示例 |
| :--- | :--- | :--- | :--- |
| `BOT_TOKEN` | ✅ | 你的机器人 Token (找 @BotFather 获取) | `123456:ABC-Def...` |
| `GROUP_ID` | ✅ | 消息转发的目标群组 ID (必须带 -100) | `-10012345678` |
| `VERIFY_QUESTION` | ❌ | (可选) 自定义验证问题 | `请输入验证密码：4399` |
| `VERIFY_ANSWER` | ❌ | (可选) 自定义验证答案 | `4399` |

6.点击【下一步】，再点击【部署】，等待几到十几分钟自动部署即可
显示【运行中】则代表部署完成，机器人已经在运行，可以在群组发送 /id 进行测试

<img width="997" height="593" alt="image" src="https://github.com/user-attachments/assets/718ab9e6-a858-4ceb-ae4f-9bda5c1cb210" />


5. **⚠️ 重要：挂载数据卷 (防止重启后数据丢失)**
   - 在 Zeabur 服务页面，点击 **硬盘**。
   - 点击 **挂载硬盘**。
   - **硬盘IP** 填写：`data`
   - **挂载目录** 填写：`/data`
   - 点击确认。

6. 显示【运行中】则代表部署完成，机器人已经在运行，可以在群组发送 /id 进行测试

<img width="997" height="593" alt="image" src="https://github.com/user-attachments/assets/718ab9e6-a858-4ceb-ae4f-9bda5c1cb210" />
