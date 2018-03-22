$(document).ready(function () {
    $(".nav-tabs li:first").addClass("active");
    $(".tab-content div:first").addClass("in active");
    $('.between').on('click', function () {
        $('#fully_ramp_time_range').prop('checked', true);
        $('#key_vague_search_text').val("");
        $('#sprint_version_text').val("");
    });
    $('#key_vague_search_text').on('click', function () {
        $('#key_vague_search').prop('checked', true);
        $('.between').val("");
        $('#sprint_version_text').val("");
    });
    $('#non_fully_ramped_lix').on('click', function () {
        $('.between').val("");
        $('#key_vague_search_text').val("");
        $('#sprint_version_text').val("");
    });
    $('#sprint_version_text').on('click', function () {
        $('#sprint_version').prop('checked', true);
        $('.between').val("");
        $('#key_vague_search_text').val("");
    });

    $('#key_vague_search').on('click', function () {
        $('.between').val("");
    });

    $('#fully_ramp_time_range').on('click', function () {
        $('#key_vague_search_text').val("");
    });

    $('.sprint').editable({
        type: 'text',
        emptytext: "<span style='color: grey'>Click to add version</span>"
    });

    $('.ramped').editable({
        type: 'select',
        source: [
            {value: 'True', text: 'True'},
            {value: 'False', text: 'False'}
        ]
    });

    $('.comments').editable({
        type: 'textarea',
        name: 'comments',
        title: 'Enter Notes',
        placeholder: "please input note:",
        emptytext: "<span style='color: grey'>Click to add note</span>"
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
                            size: 'small',
                            closeButton: false,
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
        "autoWidth": false,
        "columnDefs": [{
            "targets": -4,
            "render": function (data, type, row, meta) {
                return new Date(parseInt(data)).format("yyyy-MM-dd");
            }
        }],
        "order": [[6, "desc"]],
        "columns": [
            {"width": "6%"},
            {"width": "4%"},
            {"width": "5%"},
            {"width": "5%"},
            {"width": "15%"},
            {"width": "15%"},
            {"width": "10%"},
            {"width": "25%"},
            {"width": "8%"},
            {"width": "8%"}
        ]
    });
    $('#lix_detail_table_platform_ios').DataTable(
        {
            "autoWidth": false,
            "columnDefs": [{
                "targets": -4,
                "render": function (data, type, row, meta) {
                    return new Date(parseInt(data)).format("yyyy-MM-dd");
                }
            }],
            "order": [[6, "desc"]],
            "columns": [
                {"width": "6%"},
                {"width": "4%"},
                {"width": "5%"},
                {"width": "5%"},
                {"width": "15%"},
                {"width": "15%"},
                {"width": "10%"},
                {"width": "25%"},
                {"width": "8%"},
                {"width": "8%"}
            ]
        }
    );
    $('#lix_detail_table_platform_api').DataTable(
        {
            "autoWidth": false,
            "columnDefs": [{
                "targets": -4,
                "render": function (data, type, row, meta) {
                    return new Date(parseInt(data)).format("yyyy-MM-dd");
                }
            }],
            "order": [[6, "desc"]],
            "columns": [
                {"width": "6%"},
                {"width": "4%"},
                {"width": "5%"},
                {"width": "5%"},
                {"width": "15%"},
                {"width": "15%"},
                {"width": "10%"},
                {"width": "25%"},
                {"width": "8%"},
                {"width": "8%"}
            ]
        }
    );

    $('#lix_detail_table_pillar_career').DataTable(
        {
            "autoWidth": false,
            "columnDefs": [{
                "targets": -4,
                "render": function (data, type, row, meta) {
                    return new Date(parseInt(data)).format("yyyy-MM-dd");
                }
            }],
            "order": [[6, "desc"]],
            "columns": [
                {"width": "6%"},
                {"width": "4%"},
                {"width": "5%"},
                {"width": "5%"},
                {"width": "15%"},
                {"width": "15%"},
                {"width": "10%"},
                {"width": "25%"},
                {"width": "8%"},
                {"width": "8%"}
            ]
        }
    );
    $('#lix_detail_table_pillar_content').DataTable(
        {
            "autoWidth": false,
            "columnDefs": [{
                "targets": -4,
                "render": function (data, type, row, meta) {
                    return new Date(parseInt(data)).format("yyyy-MM-dd");
                }
            }],
            "order": [[6, "desc"]],
            "columns": [
                {"width": "6%"},
                {"width": "4%"},
                {"width": "5%"},
                {"width": "5%"},
                {"width": "15%"},
                {"width": "15%"},
                {"width": "10%"},
                {"width": "25%"},
                {"width": "8%"},
                {"width": "8%"}
            ]
        }
    );
    $('#lix_detail_table_pillar_profile').DataTable(
        {
            "autoWidth": false,
            "columnDefs": [{
                "targets": -4,
                "render": function (data, type, row, meta) {
                    return new Date(parseInt(data)).format("yyyy-MM-dd");
                }
            }],
            "order": [[6, "desc"]],
            "columns": [
                {"width": "6%"},
                {"width": "4%"},
                {"width": "5%"},
                {"width": "5%"},
                {"width": "15%"},
                {"width": "15%"},
                {"width": "10%"},
                {"width": "25%"},
                {"width": "8%"},
                {"width": "8%"}
            ]
        }
    );
    $('#lix_detail_table_pillar_growth').DataTable(
        {
            "autoWidth": false,
            "columnDefs": [{
                "targets": -4,
                "render": function (data, type, row, meta) {
                    return new Date(parseInt(data)).format("yyyy-MM-dd");
                }
            }],
            "order": [[6, "desc"]],
            "columns": [
                {"width": "6%"},
                {"width": "4%"},
                {"width": "5%"},
                {"width": "5%"},
                {"width": "15%"},
                {"width": "15%"},
                {"width": "10%"},
                {"width": "25%"},
                {"width": "8%"},
                {"width": "8%"}
            ]
        }
    );
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
