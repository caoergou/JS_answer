# JS_answer

项目实现日志

- 2020.4.13 22:22 
  1. 加入了Flask_Login框架，以实现更加方便的登录、登出管理，提升账户安全性
  2. 加入了Flask_WTF框架，以实现更加完善的表格管理，但出现相关BUG：The CSRF token is missing
     需要去了解CSRF的相关机制
- 2020.4.14 21:58
   1. 修复CSRF token is missing 的bug
   2. 完善了UI展示，实现通过js来提示相关信息，提升了登录体验
   3. 产生了新的BUG：注册后页面无法跳转

Todo List

- [x] 学习CSRF的相关机制
- [ ] 修改页面无法跳转的bug
- [ ] 实现提问题，看回答的功能
- [ ] 简要学习Flask框架的相关内容