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

    // if it's not a subtring, abort
    if (!longer.includes(shorter)) {
        return 0;
    }
    return (longerLength - strDistance(longer, shorter)) / parseFloat(longerLength);
}


function scoreWord(word, inputStr, highlight = true, hide = true) {
    // Looks through all definitions of a word, returns the maximum score of any
    // of the definitions. Optionally highlights matched portions of glosses.
    // If hide = true, will hide any word with a score of 0.
    let glosses = $(word).find(".glosses");
    var score = 0;

    $(glosses).each(function(_) {
        let glossList = this.innerHTML.split(",").map(s => s.trim());
        for (i in glossList) {
            let s = similarity(glossList[i], inputStr);
            score = Math.max(score, s);
        }

        if (highlight) {
            let regex_input = new RegExp(inputStr, "g");
            $(this).html(
                $(this).html().replace(regex_input, "<span class = 'highlight'>" + inputStr + "</span>")
            );
        }
    });

    if (hide && score <= 0) {
        $(word).hide();
    }
    $(word).data("score", score);
    return score;
}

function sortAll() {
    $("#content .word.main").sort((a, b) => {
        return ($(b).data("score") - $(a).data("score"));
    }).appendTo("#content");
}

function filterWordByPos(word, pos) {
    // Takes a word and pos, hides all definitions that do not match the
    // specified pos. If not definitions are left at the end, hide the word.

    pos = pos.replace(/\W/g, '');
    var matched = false;

    $(word).find(".pos").each(function(_) {
        var innerMatched = false;
        let posList = this.innerHTML.split(",");
        console.log(posList);
        for (i in posList) {
            let wordPos = posList[i].replace(/\W/g, '')
            if (wordPos === pos) {
                matched = true;
                innerMatched = true;
            }
        }
        if (!innerMatched) {
            $(this).closest(".def.main").hide();
        }
    });

    if (!matched) {
        $(word).hide();
    }
}

function filterWords(input, pos) {
    resetDom();

    let filterPos = (pos !== "all");

    $("#content").find(".word.main").each(function(_) {
        if (filterPos) {
            filterWordByPos(this, pos);
        }
        if (input) {
            scoreWord(this, input);
        }
    });

    if (input) {
        sortAll();
    }
}

function resetDom() {
    $("#content").html(cache);
}

$(document).ready(function () {
    cache = $("#content").html();

    $("#select").change(function () {
        let input = $("#search").val().toLowerCase();
        let pos = $(this).val().toLowerCase();
        filterWords(input, pos);
    });

    $("#search").bind("search", function (_) {
        let pos = $("#select").val().toLowerCase();
        filterWords(search.value, pos);
    });
});
