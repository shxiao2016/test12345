$(document).ready(function () {
    $(".nav-tabs li:first").addClass("active");
    $(".tab-content div:first").addClass("in active");

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
        "order": [[6, "desc"], [8, "asc"]]
    });
    $('#lix_detail_table_platform_ios').DataTable({
        "order": [[6, "desc"], [8, "asc"]]
    });
    $('#lix_detail_table_platform_api').DataTable({
        "order": [[6, "desc"], [8, "asc"]]
    });

    $('#lix_detail_table_pillar_career').DataTable({
        "order": [[6, "desc"], [8, "asc"]]
    });
    $('#lix_detail_table_pillar_content').DataTable({
        "order": [[6, "desc"], [8, "asc"]]
    });
    $('#lix_detail_table_pillar_profile').DataTable({
        "order": [[6, "desc"], [8, "asc"]]
    });
    $('#lix_detail_table_pillar_growth').DataTable({
        "order": [[6, "desc"], [8, "asc"]]
    });
});
