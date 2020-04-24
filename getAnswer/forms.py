from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
        InputRequired)


class RegisterForm(FlaskForm):
    '''注册表单类'''

    email = StringField(validators=[DataRequired('邮箱不能为空'),
            Email('请输入正确的邮箱格式')])
    username = StringField(validators=[DataRequired('用户名不能为空')])
    password = PasswordField(validators=[DataRequired('密码不能为空'),
            Length(5, 26, '密码长度为 5 ~ 26 个字符')])
    repeat_password = PasswordField(validators=[
            EqualTo('password', '两次输入的密码不一致')])
    vercode = StringField(validators=[InputRequired('答案写错了')])


class LoginForm(FlaskForm):
    '''登录表单类'''

    email = StringField(validators=[DataRequired('邮箱不能为空')])
    password = PasswordField(validators=[DataRequired('密码不能为空'),
            Length(5, 26, '密码长度为 5 ~ 26 个字符')])
    vercode = StringField(validators=[InputRequired('答案写错了')])

from wtforms import StringField, PasswordField, IntegerField


class PostForm(FlaskForm):
    '''帖子表单类'''

    id = StringField()
    title = StringField(validators=[DataRequired('提问标题不能为空')])
    content = StringField(validators=[DataRequired('提问内容不能为空')])
    catalog_id = StringField(validators=[DataRequired('提问主题不能为空')])
    reward = IntegerField(validators=[InputRequired('问题悬赏不能不选')])
    vercode = StringField(validators=[InputRequired('验证码不能为空')])