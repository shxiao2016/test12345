/**
 * Created by tcheng on 11/9/16.
 */
function loopForm(page_url) {
    var sList = "";
    $('input[type=checkbox]').each(function () {
        if (sList.length > 0) {
            sList += "&";
        }
        sList += this.checked ? this.id + "=" + this.name : "";
    });
    // sList = sList.replace('/', '&');    // / cannot be used in url
    console.log(sList);

    var host = "http://" + window.location.hostname;
    var port = window.location.port;

    if (port) {
        newHost = host + ":" + port + page_url + "?" + sList;
    } else {
        newHost = host + page_url + "?" + sList;
    }

    console.log(newHost);
    window.location = newHost;
}

function clearAllStatus() {
    $('input[class="status"]').each(function () {
        this.checked = false;
    });
}
function selectAllStatus() {
    $('input[class="status"]').each(function () {
        this.checked = true;
    });
}
function clearAllCategory() {
    $('input[class="pillar"]').each(function () {
        this.checked = false;
    });
}
function selectAllCategory() {
    $('input[class="pillar"]').each(function () {
        this.checked = true;
    });
}
function clearAllClean() {
    $('input[class="qualified_clean"]').each(function () {
        this.checked = false;
    });
}
function selectAllClean() {
    $('input[class="qualified_clean"]').each(function () {
        this.checked = true;
    });
}
function clearAllPlatform() {
    $('input[class="platform"]').each(function () {
        this.checked = false;
    });
}
function selectAllPlatform() {
    $('input[class="platform"]').each(function () {
        this.checked = true;
    });
}
function clearAllPeriod() {
    $('input[class="period"]').each(function () {
        this.checked = false;
    });
}
function selectAllPeriod() {
    $('input[class="period"]').each(function () {
        this.checked = true;
    });
}
function clearAllOwner() {
    $('input[class="owner"]').each(function () {
        this.checked = false;
    });
}
function selectAllOwner() {
    $('input[class="owner"]').each(function () {
        this.checked = true;
    });
}
function goStatisticPage() {
    var host = "http://" + window.location.hostname;
    var port = window.location.port;
    window.location = host + ":" + port + "/statistic/";
}
function goDetailsPage() {
    var host = "http://" + window.location.hostname;
    var port = window.location.port;
    window.location = host + ":" + port + "/details/";
}
$('table').on('click', 'td', function (e) {
    var time = e.delegateTarget.tHead.rows[0].cells[this.cellIndex],
        day = this.parentNode.cells[0];
    var dayStr = jSecure.parseHTML(day);
    var timeStr = jSecure.parseHTML(time);
    alert([dayStr, timeStr]);
});

function tableText(tableCell) {
    alert(tableCell.innerHTML);
}