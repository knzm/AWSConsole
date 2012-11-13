(function($) {
  var Dashboard = function(api_endpoints) {
    this.api_endpoints = api_endpoints;
    this.init_buttons();
  };

  Dashboard.prototype = {
      execute: function(url, data, src, wait) {
      src.addClass('disabled');
      if (wait > 0) {
        src.spin();
      };
      $.ajax({
        url: url,
        type: "POST",
        data: data,
        success: function(data, dataType) {
          setTimeout(function() { window.location.reload() }, wait);
        },
        error: function(req, status, exc) {
          alert('Action failed!');
          src.removeClass('disabled');
          src.spin(false);
        }
      });
    },

    init_buttons: function() {
      var app = this;
      $('button[name=sync]').click(function(ev) {
        if (window.confirm('Are you sure to sync this region?')) {
          app.sync_button_clicked($(this), ev);
        }
      });
      $('button[name=start]').click(function(ev) {
        if (window.confirm('Are you sure to start this instance?')) {
          app.start_button_clicked($(this), ev);
        }
      });
      $('button[name=stop]').click(function(ev) {
        if (window.confirm('Are you sure to stop this instance?')) {
          app.stop_button_clicked($(this), ev);
        }
      });
      $('button[name=edit]').click(function(ev) {
        app.edit_button_clicked($(this), ev);
      });
    },

    sync_button_clicked: function(src, ev) {
      var app = this;
      var region = $('#region-dropdown .current').data('region');
      app.execute(app.api_endpoints.sync, {region: region}, src, 0);
    },

    start_button_clicked: function(src, ev) {
      var app = this;
      var id = src.data('id');
      app.execute(app.api_endpoints.start, {id: id}, src, 3000);
    },

    stop_button_clicked: function(src, ev) {
      var app = this;
      var id = src.data('id');
      app.execute(app.api_endpoints.stop, {id: id}, src, 3000);
    },

    save: function(data, success_callback) {
      var app = this;
      $.ajax({
        url: app.api_endpoints.save,
        type: "POST",
        data: data,
        success: function(data, dataType) {
          success_callback(data, dataType);

          var flash = $('<div/>').addClass('alert alert-success');
          $('<strong>Saved!</strong>').appendTo(flash);
          $('#content').prepend(flash);

          var button = $('<button/>').addClass('close')
          button.attr('data-dismiss', 'alert').text('x');
          button.appendTo(flash);

          $('body,html').animate({scrollTop: 0}, 800);
        }
      });
    },

    edit_button_clicked: function(src, ev) {
      var app = this;
      var id = src.data('id');
      var div = $('<div/>');
      div.dialog({
        autoOpen: true,
        width: '600px',
        modal: true,
        buttons: {
          "save": function(ev) {
            app.save(div.find('form').serialize(),
                     function(data, dataType){ div.dialog("destroy") });
          },
          "close": function(ev) {
            div.dialog("destroy");
          }
        },
        open: function() {
          var url = app.api_endpoints.edit;
          url += url.indexOf("?") < 0 ? "?" : "&";
          url += "instance_id=" + id;
          div.load(url);
        }
      });
    }
  };

  window.Dashboard = Dashboard;

})(jQuery);
