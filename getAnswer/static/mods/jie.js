/**

 @Name: 求解板块

 */

layui.define('fly', function (exports) {

  var $ = layui.jquery;
  var layer = layui.layer;
  var util = layui.util;
  var laytpl = layui.laytpl;
  var form = layui.form;
  var fly = layui.fly;

  var gather = {}, dom = {
    jieda: $('#jieda')
    , content: $('#L_content')
    , jiedaCount: $('#jiedaCount')
  };

  //监听专栏选择
  // form.on('select(column)', function(obj){
  //   var value = obj.value
  //   ,elemQuiz = $('#LAY_quiz')
  //   ,tips = {
  //     tips: 1
  //     ,maxWidth: 250
  //     ,time: 10000
  //   };
  //   elemQuiz.addClass('layui-hide');
  //   if(value === '0'){
  //     layer.tips('下面的信息将便于您获得更好的答案', obj.othis, tips);
  //     elemQuiz.removeClass('layui-hide');
  //   } else if(value === '99'){
  //     layer.tips('系统会对【分享】类型的帖子予以飞吻奖励，但我们需要审核，通过后方可展示', obj.othis, tips);
  //   }
  // });

  //提交回答
  fly.form['/api/reply'] = function (data, required) {
    //这一步操作只是为了及时在前端上显示新的回答，提升用户的体验
    var tpl =
      '<li data-id="{{ d._id }}" \
      <div class="fly-panel detail-box">\
        <div class="detail-about detail-about-reply">\
            <a class="fly-avatar" href="/user/{{ layui.cache.user.uid }}" target="_blank">\
              <img src="{{= d.user.avatar}}" alt="{{= d.user.username}}">\
            </a>\
            <div class="fly-detail-user">\
              <a href="/user/{{ layui.cache.user.uid }}" target="_blank" class="fly-link">\
                <cite>{{d.user.username}}</cite>\
              </a>\
            </div>\
            <div class="detail-hits">\
              <span>刚刚</span>\
            </div>\
        </div>\
        <div class="detail-body jieda-body photos">\
          {{ d.content}}\
        </div>\
      </div>\
    </li>'
    data.content = fly.content(data.content);
    laytpl(tpl).render($.extend(data, {
      user: layui.cache.user
    }), function (html) {
      required[0].value = '';
      dom.jieda.find('.fly-none').remove();
      dom.jieda.append(html);

      var count = dom.jiedaCount.text() | 0;
      dom.jiedaCount.html(++count);
    });
  };

  //求解管理
  gather.jieAdmin = {
    //删求解
    del: function (div) {
      layer.confirm('确认删除该帖子么？', function (index) {
        layer.close(index);
        fly.json('/api/post/delete/' + div.data('id'), function (res) {
          layer.msg(res.msg);
          if (res.status === 0) {
            setTimeout(function () {
              location.href = res.action;
            }, 1000);
          }
        });
      });
    }

    //设置置顶、状态
    , set: function (div) {
      var othis = $(this);
      layer.confirm('是否确定执行此操作', function (index) {
        layer.close(index);
        fly.json('/api/post/set/' + div.data('id') + '/' + othis.attr('field') + '/' + othis.attr('rank'), function (res) {
          if (res.status === 0) {
            location.reload();
          }
        });
      });

    }

    //收藏
    // , collect: function (div) {
    //   var othis = $(this), type = othis.data('type');
    //   fly.json('/collection/' + type + '/' + div.data('id'), function (res) {
    //     if (type === 'add') {
    //       othis.data('type', 'remove').html('取消收藏').addClass('layui-btn-danger');
    //     } else if (type === 'remove') {
    //       othis.data('type', 'add').html('收藏').removeClass('layui-btn-danger');
    //     }
    //   });
    // }
  };

  $('body').on('click', '.jie-admin', function () {
    var othis = $(this), type = othis.attr('type');
    gather.jieAdmin[type] && gather.jieAdmin[type].call(this, othis.parent());
  });

  //异步渲染
  // var asyncRender = function () {
  //   var div = $('.fly-admin-box'), jieAdmin = $('#LAY_jieAdmin');
  //   //查询帖子是否收藏
  //   if (jieAdmin[0] && layui.cache.user.uid != '') {
  //     fly.json('/collection/find/' + div.data('id'), function (res) {
  //       jieAdmin.append('<span class="layui-btn layui-btn-xs jie-admin ' + (res.data.collection ? 'layui-btn-danger' : '') + '" type="collect" data-type="' + (res.data.collection ? 'remove' : 'add') + '">' + (res.data.collection ? '取消收藏' : '收藏') + '</span>');
  //     });
  //   }
  // }();

  //解答操作
  gather.jiedaActive = {
    addone: function (li) { //编辑
      var div = $('.fly-admin-box');
      fly.json('/api/reply/content/' + li.data('id'), function (res) {
        var data = res.data;
        layer.prompt({
          formType: 2
          , value: data
          , maxlength: 100000
          , title: '写回答'
          , area: ['728px', '300px']
          , success: function (layero) {
            fly.layEditor({
              elem: layero.find('textarea')
            });
          }
        }, function (value, index) {
          fly.json('/api/reply/update/' + li.data('id'), {
            content: value
          }, function (res) {
            layer.close(index);
            li.find('.detail-body').html(fly.content(value));
          });
        });
      });
    },
    zan: function (li) { //赞
      var othis = $(this), ok = othis.hasClass('zanok');
      var div = $(".jieda-admin");
      
      fly.json('/api/reply/zan/' + li.data('id'), {
        ok: ok
      }, function (res) {
        if (res.status === 0) {
          var zans = othis.find('em').html() | 0;
          othis[ok ? 'removeClass' : 'addClass']('zanok');
          othis.find('em').html(ok ? (--zans) : (++zans));
        } else {
          layer.msg(res.msg);
        }
      });
    },
    putCoin: function (li) { //投币
      var othis = $(this), ok = othis.hasClass('putCoinok');
      var div = $(".jieda-admin");
      
      fly.json('/api/reply/putCoin/' + li.data('id'), {
        ok: ok
      }, function (res) {
        if (res.status === 0) {
          var coins = othis.find('em')[1].html() | 0;
          othis[ok ? 'removeClass' : 'addClass']('putCoinok');
          othis.find('em')[1].html(ok ? (--coins) : (++coins));
          layer.msg(res.msg);
        } else {
          layer.msg(res.msg);
        }
      });
    }
    , reply: function (li) { //回复
      var val = dom.content.val();
      var aite = '@' + li.find('.fly-detail-user cite').text().replace(/\s/g, '');
      dom.content.focus()
      if (val.indexOf(aite) !== -1) return;
      dom.content.val(aite + ' ' + val);
    }
    , accept: function (li) { //采纳
      var othis = $(this);
      var div = $('.fly-admin-box')
      layer.confirm('是否采纳该回答为最佳答案？', function (index) {
        layer.close(index);
        fly.json('/api/adopt/' + li.data('id'), function (res) {
          if (res.status === 0) {
            $('.jieda-accept').remove();
            li.addClass('jieda-daan');
            li.find('.detail-about').append('<i class="iconfont icon-caina" title="最佳答案"></i>');
          } else {
            layer.msg(res.msg);
          }
        });
      });
    }
    , edit: function (li) { //编辑
      var div = $('.fly-admin-box')
      fly.json('/api/reply/content/' + li.data('id'), function (res) {
        var data = res.data;
        layer.prompt({
          formType: 2
          , value: data
          , maxlength: 100000
          , title: '编辑回答'
          , area: ['728px', '300px']
          , success: function (layero) {
            fly.layEditor({
              elem: layero.find('textarea')
            });
          }
        }, function (value, index) {
          fly.json('/api/reply/update/' + li.data('id'), {
            content: value
          }, function (res) {
            layer.close(index);
            li.find('.detail-body').html(fly.content(value));
          });
        });
      });
    }

    , del: function (li) { //删除
      var div = $('.fly-admin-box');
      layer.confirm('确认删除该回答么？', function (index) {
        layer.close(index);
        fly.json('/api/reply/delete/' + li.data('id'), function (res) {
          if (res.status === 0) {
            var count = dom.jiedaCount.text() | 0;
            dom.jiedaCount.html(--count);
            li.remove();
            //如果删除了最佳答案
            if (li.hasClass('jieda-daan')) {
              $('.jie-status').removeClass('jie-status-ok').text('求解中');
            }
          } else {
            layer.msg(res.msg);
          }
        });
      });
    }
  };

  $('.jieda-reply span').on('click', function () {
    var othis = $(this), type = othis.attr('type');
    gather.jiedaActive[type].call(this, othis.parents('li'));
  });


  //定位分页
  if (/\/page\//.test(location.href) && !location.hash) {
    var replyTop = $('#flyReply').offset().top - 80;
    $('html,body').scrollTop(replyTop);
  }

  exports('jie', null);
});
