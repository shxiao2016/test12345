$(document).ready(function () {
    $(".nav-tabs li:first").addClass("active");
    $(".tab-content div:first").addClass("in active");
    $('.delete-favorite').click(function () {
        var name = $(this).parent().parent().find('.name').children().first().text();
        bootbox.confirm({
            message: "Really want to delete this lix?",
            size: "small",
            buttons: {
                confirm: {
                    label: 'Yes'
                },
                cancel: {
                    label: 'No'
                }
            },
            callback: function (result) {
                if (result) {
                    $.ajax({
                        url: $SCRIPT_ROOT + Flask.url_for('delete_a_lix'),
                        type: 'POST',
                        data: {"lix_name": name},
                        statusCode: {
                            200: function () {
                                bootbox.alert({
                                    message: "Removed successfully!",
                                    size: 'small',
                                    closeButton: false,
                                    callback: function () {
                                        location.reload()
                                    }
                                });
                            }
                        }
                    });
                }
            }
        });
    });

    $('#upload_button').click(function () {
        var name = $("input[name='lix_name']").val();
        $("#upload_button").attr("disabled", "disabled");
        $("#lix_name_id").attr("disabled", "disabled");
        $.ajax({
            url: $SCRIPT_ROOT + Flask.url_for('upload_a_lix'),
            type: 'POST',
            data: {"lix_name": name},
            success: function (message) {
                bootbox.alert({
                    message: message,
                    size: 'small',
                    closeButton: false,
                    callback: function () {
                        $("#lix_name_id").removeAttr("disabled");
                        if (message == "successfully added") {
                            location.reload();
                        } else {
                            $("input[name='lix_name']").val("");
                        }
                    }
                });
            }
        });
    });

    $('#watch_list_table').DataTable({
        searching: false,
        bLengthChange: false,
        ordering: false,
        bInfo: false,
        "columnDefs": [{
            "targets": -4,
            "render": function (data, type, row, meta) {
                return new Date(parseInt(data)).format("yyyy-MM-dd");
            }
        }]
    });

    $("#lix_name_id").on("input", function (evt) {
        if ($(this).val().trim().length) {
            $("#upload_button").removeAttr("disabled");
        } else {
            $("#upload_button").attr("disabled", "disabled");
        }
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
