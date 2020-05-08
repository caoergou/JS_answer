from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
        InputRequired)
from wtforms import StringField, PasswordField, IntegerField
from . import code_msg


class RegisterForm(FlaskForm):
    '''注册表单类'''

    email = StringField(validators=[DataRequired('邮箱不能为空'),
            Email('请输入正确的邮箱格式')])
    username = StringField(validators=[DataRequired('用户名不能为空')])
    password = PasswordField(validators=[DataRequired('密码不能为空'),
            Length(6, 26, '密码长度为 6 ~ 26 个字符')])
    repeat_password = PasswordField(validators=[
            EqualTo('password', '两次输入的密码不一致')])
    vercode = StringField(validators=[InputRequired('答案写错了')])


class LoginForm(FlaskForm):
    '''登录表单类'''

    email = StringField(validators=[DataRequired('邮箱不能为空')])
    password = PasswordField(validators=[DataRequired('密码不能为空'),
            Length(6, 26, '密码长度为 6 ~ 26 个字符')])
    vercode = StringField(validators=[InputRequired('答案写错了')])




class PostForm(FlaskForm):
    '''帖子表单类'''

    id = StringField()
    title = StringField(validators=[DataRequired('提问标题不能为空')])
    content = StringField(validators=[DataRequired('提问内容不能为空')])
    topic_id = StringField(validators=[DataRequired('提问主题不能为空')])
    reward = IntegerField(validators=[InputRequired('问题悬赏不能不选')])
    vercode = StringField(validators=[InputRequired('验证码不能为空')])


class TopicForm(FlaskForm):
    '''话题表单类'''

    id = StringField()
    title = StringField(validators=[DataRequired('话题名不能为空')])
    description = StringField(validators=[DataRequired('话题说明不能为空')])
    parent_id = StringField(validators=[DataRequired('父话题ID不能为空')])
    topic_admin = StringField(validators=[DataRequired('管理员邮箱不能为空')])
    vercode = StringField(validators=[InputRequired('验证码不能为空')])

class ChangePassWordForm(FlaskForm):
    nowpassword = StringField(validators=[DataRequired(
            code_msg.NOW_PASSWORD_EMPTY.get_msg())])
    password = PasswordField(validators=[Length(min=6, max=16,
            message=code_msg.PASSWORD_LENGTH_ERROR.get_msg())])
    repassword = PasswordField(validators=[EqualTo('password',
            code_msg.PASSWORD_REPEAT_ERROR.get_msg())])

class SendForgetMailForm(FlaskForm):
    email = StringField(validators=[DataRequired(
            code_msg.EMAIL_EMPTY.get_msg())])
    vercode = StringField(validators=[InputRequired(
            code_msg.VERIFY_CODE_ERROR.get_msg())])


class ForgetPasswordForm(FlaskForm):
    email = StringField(validators=[DataRequired(
            code_msg.EMAIL_EMPTY.get_msg())])
    code = StringField(validators=[DataRequired(
            code_msg.VERIFY_CODE_ERROR.get_msg())])
    vercode = StringField(validators=[InputRequired(
            code_msg.VERIFY_CODE_ERROR.get_msg())])
    password = PasswordField(validators=[Length(min=6, max=16,
            message=code_msg.PASSWORD_LENGTH_ERROR.get_msg())])
    repassword = PasswordField(validators=[EqualTo('password',
            code_msg.PASSWORD_REPEAT_ERROR.get_msg())])