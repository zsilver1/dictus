function strDistance(s1, s2) {
    s1 = s1.toLowerCase();
    s2 = s2.toLowerCase();

    var costs = new Array();
    for (var i = 0; i <= s1.length; i++) {
        var lastValue = i;
        for (var j = 0; j <= s2.length; j++) {
            if (i == 0)
                costs[j] = j;
            else {
                if (j > 0) {
                    var newValue = costs[j - 1];
                    if (s1.charAt(i - 1) != s2.charAt(j - 1))
                        newValue = Math.min(Math.min(newValue, lastValue),
                                            costs[j]) + 1;
                    costs[j - 1] = lastValue;
                    lastValue = newValue;
                }
            }
        }
        if (i > 0)
            costs[s2.length] = lastValue;
    }
    return costs[s2.length];
}

function similarity(s1, s2) {
    var longer = s1;
    var shorter = s2;
    if (s1.length < s2.length) {
        longer = s2;
        shorter = s1;
    }
    var longerLength = longer.length;
    if (longerLength == 0) {
        return 1.0;
    }
    return (longerLength - strDistance(longer, shorter)) / parseFloat(longerLength);
}


function sortResults() {
    $("#content .word").sort((a, b) => {
        return ($(b).data("similarity") - $(a).data("similarity"));
    }).appendTo("#content");
}

function filterOnSearch(input) {
    if (input.length === 0) {
        $("#content").html(cache);
        $("#content").show();
        // TODO
        // filterByPos($("#select").val().toLowerCase());
        return;
    }
    $("#content").children(".word").each((i, word) => {
        var def = $(word).children(".def");
        $(def).html($(def).data("orig_html"));
        let def_text = $(def).text().toLowerCase();
        if (!def_text.includes(input)) {
            $(word).hide();
            $(word).data("similarity", 0);
        } else {
            if (!$(word).data("hiddenPosFilter")) {
                $(word).data("similarity", rateDef(input, def_text));
                let regex_input = new RegExp(input, "g");
                $(def).data("orig_html", $(def).html())
                $(def).html(
                    $(def).html().replace(regex_input, "<span class = 'highlight'>" + input + "</span>")
                );
                $(word).show();
            }
        }
    })
    sortResults();
}

function filterByPos(pos) {
    if (pos === "all") {
        $("#content").html(cache);
        $("#content").show();
    }
    // TODO
    // filter again by search if need be
    let val = $("#search").val().toLowerCase();
    if (val.length > 0) {
        filterOnSearch(val);
    }
}


$(document).ready(function () {
    cache = $("#content").html();

    $("#select").change(function () {
        let pos = $(this).val().toLowerCase();
        filterByPos(pos);
    });

    $("#search").keyup(function (e) {
        if (e.keyCode === 13) {
            let input = $(this).val().toLowerCase();
            filterOnSearch(input);
        }
    });
});
