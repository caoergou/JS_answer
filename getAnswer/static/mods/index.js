/**
 
 @Name: Fly社区主入口

**/


layui.define(['form'], function (exports) {

  var $ = layui.jquery
    , form = layui.form
    , device = layui.device()

    , DISABLED = 'layui-btn-disabled';

  //阻止IE7以下访问
  if (device.ie && device.ie < 8) {
    layer.alert('如果您非得使用 IE 浏览器访问Fly社区，那么请使用 IE8+');
  }

  layui.focusInsert = function (obj, str) {
    var result, val = obj.value;
    obj.focus();
    if (document.selection) { //ie
      result = document.selection.createRange();
      document.selection.empty();
      result.text = str;
    } else {
      result = [val.substring(0, obj.selectionStart), str, val.substr(obj.selectionEnd)];
      obj.focus();
      obj.value = result.join('');
    }
  };

  var fly = {

    //Ajax
    // 定义 json 函数
    json: function (url, data, success, options) {
      // typeof 返回字符串，表示 data 的类型
      // type 为 true 或 false
      var that = this, type = typeof data === 'function';

      if (type) {
        options = success
        success = data;
        data = {};
      }

      options = options || {};
      // 返回
      return $.ajax({
        type: options.type || 'post',
        dataType: options.dataType || 'json',
        data: data,
        url: url,
        success: function (res) {
          if (res.status === 0) {
            success && success(res);
          } else {
            layer.msg(res.msg || res.code, { shift: 6 });
            options.error && options.error();
          }
        },
        error: function (e) {
          layer.msg('请求异常，请重试', { shift: 6 });
          options.error && options.error(e);
        }
      });
    }
  }
})
