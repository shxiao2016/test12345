$(document).ready(function () {
    $(".nav-tabs li:first").addClass("active");
    $(".tab-content div:first").addClass("in active");
    $('lix_detail_table_platform').DataTable();

    $('#subscribe').editable({
        placement: 'bottom',
        name: 'subscribed_pillars',
        source: [
            {value: 'career', text: 'career'},
            {value: 'content', text: 'content'},
            {value: 'profile', text: 'profile'},
            {value: 'growth', text: 'growth'}
        ],
        display: function (value, sourceData) {
            var checked = $.fn.editableutils.itemsByValue(value, sourceData);
            if (checked.length) {
                $(this).html('subscribed');
            } else {
                $(this).html('subscribe');
            }
        }
    });

    $('.add_to_watch_list_checkbox_not_login span').click(function () {
        bootbox.alert({
            message: "Please login in first!",
            size: 'small',
            closeButton: false
        });
    });

    $('.add_to_watch_list_checkbox span').click(function () {
        var name = $(this).parent().find('a').first().text();
        var checked = $(this).hasClass('glyphicon-heart-empty');
        var ele = $(this);

        if (checked) {
            $.ajax({
                url: $SCRIPT_ROOT + Flask.url_for('add_to_watch_list'),
                type: 'POST',
                data: {"name": name, "checked": checked},
                statusCode: {
                    200: function () {
                        bootbox.alert({
                            message: "Added successfully!",
                            size: 'small',
                            closeButton: false,
                            callback: function () {
                                ele.removeClass('glyphicon-heart-empty').addClass('glyphicon-heart');
                            }
                        });
                    }
                }
            });
        } else {
            $.ajax({
                url: $SCRIPT_ROOT + Flask.url_for('add_to_watch_list'),
                type: 'POST',
                data: {"name": name, "checked": checked},
                statusCode: {
                    200: function () {
                        bootbox.alert({
                            message: "Removed successfully!",
                            closeButton: false,
                            size: 'small',
                            callback: function () {
                                ele.removeClass('glyphicon-heart').addClass('glyphicon-heart-empty');
                            }
                        });
                    }
                }
            });
        }
    });

    $('#lix_detail_table_platform_android').DataTable({
        "columnDefs": [{
            "targets": -3,
            "render": function (data, type, row, meta) {
                return new Date(parseInt(data)).format("yyyy-MM-dd");
            }
        }],
        "order": [[6, "asc"]]
    });
    $('#lix_detail_table_platform_ios').DataTable(
        {
            "columnDefs": [{
                "targets": -3,
                "render": function (data, type, row, meta) {
                    return new Date(parseInt(data)).format("yyyy-MM-dd");
                }
            }],
            "order": [[6, "asc"]]
        }
    );
    $('#lix_detail_table_platform_api').DataTable(
        {
            "columnDefs": [{
                "targets": -3,
                "render": function (data, type, row, meta) {
                    return new Date(parseInt(data)).format("yyyy-MM-dd");
                }
            }],
            "order": [[6, "asc"]]
        }
    );

    $('#lix_detail_table_pillar_career').DataTable(
        {
            "columnDefs": [{
                "targets": -3,
                "render": function (data, type, row, meta) {
                    return new Date(parseInt(data)).format("yyyy-MM-dd");
                }
            }],
            "order": [[6, "asc"]]
        }
    );
    $('#lix_detail_table_pillar_content').DataTable(
        {
            "columnDefs": [{
                "targets": -3,
                "render": function (data, type, row, meta) {
                    return new Date(parseInt(data)).format("yyyy-MM-dd");
                }
            }],
            "order": [[6, "asc"]]
        }
    );
    $('#lix_detail_table_pillar_profile').DataTable(
        {
            "columnDefs": [{
                "targets": -3,
                "render": function (data, type, row, meta) {
                    return new Date(parseInt(data)).format("yyyy-MM-dd");
                }
            }],
            "order": [[6, "asc"]]
        }
    );
    $('#lix_detail_table_pillar_growth').DataTable(
        {
            "columnDefs": [{
                "targets": -3,
                "render": function (data, type, row, meta) {
                    return new Date(parseInt(data)).format("yyyy-MM-dd");
                }
            }],
            "order": [[6, "asc"]]
        }
    );


    $('#option_days').on('click', function () {
        $('.between').val("");
    });

    $('#option_between').on('click', function () {
        $('#last_days').val("");
    });
    $('#last_days').on('click', function () {
        $('#option_between').prop('checked', false);
        $('#option_days').prop('checked', true);
        $('.between').val("");

    });

    $('.between').on('click', function () {
        $('#option_days').prop('checked', false);
        $('#option_between').prop('checked', true);
        $('#last_days').val("");
    });

    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });
    $('.input-daterange input').each(function () {
        $(this).datepicker({
            format: {

                toDisplay: function (date, format, language) {
                    var d = new Date(date);
                    return d.toISOString();
                },
                toValue: function (date, format, language) {
                    var d = new Date(date);
                    return new Date(d);
                }
            }
        });
    });
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar, #content').toggleClass('active');
        $('.collapse.in').toggleClass('in');
        $('a[aria-expanded=true]').attr('aria-expanded', 'false');
    });
});

Date.prototype.format = function (format) {
    var date = {
        "M+": this.getMonth() + 1,
        "d+": this.getDate(),
        "h+": this.getHours(),
        "m+": this.getMinutes(),
        "s+": this.getSeconds(),
        "q+": Math.floor((this.getMonth() + 3) / 3),
        "S+": this.getMilliseconds()
    };
    if (/(y+)/i.test(format)) {
        format = format.replace(RegExp.$1, (this.getFullYear() + '').substr(4 - RegExp.$1.length));
    }
    for (var k in date) {
        if (new RegExp("(" + k + ")").test(format)) {
            format = format.replace(RegExp.$1, RegExp.$1.length == 1
                ? date[k] : ("00" + date[k]).substr(("" + date[k]).length));
        }
    }
    return format;
}
