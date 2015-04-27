$(function() {
    $.tablesorter.themes.bootstrap = {
        table        : 'table table-bordered table-striped',
caption      : 'caption',
// header class names
header       : 'bootstrap-header', // give the header a gradient background (theme.bootstrap_2.css)
sortNone     : '',
sortAsc      : '',
sortDesc     : '',
active       : '', // applied when column is sorted
hover        : '', // custom css required - a defined bootstrap style may not override other classes
// icon class names
icons        : 'icon-white', // add "icon-white" to make them white; this icon class is added to the <i> in the header
iconSortNone : 'bootstrap-icon-unsorted', // class name added to icon when column is not sorted
iconSortAsc  : 'icon-chevron-up glyphicon glyphicon-chevron-up', // class name added to icon when column has ascending sort
iconSortDesc : 'icon-chevron-down glyphicon glyphicon-chevron-down', // class name added to icon when column has descending sort
filterRow    : '', // filter row class
footerRow    : '',
footerCells  : '',
even         : '', // even row zebra striping
odd          : ''  // odd row zebra striping
    };

    $("table").tablesorter({
        theme: "bootstrap",
        widthFixed: false,
        headerTemplate : '{content} {icon}',
        widgets : [ "uitheme", "filter", "zebra" ],

        widgetOptions : {
            zebra : ["even", "odd"],
        filter_reset : ".reset"
        }
    });

    // beeeeeeeeeeeh
    $(".tablesorter-filter").addClass("form-control");
    $(".tablesorter-filter").slice(2).parents("td").addClass("hidden-xs");
    $(".tablesorter-filter").slice(3).parents("td").addClass("hidden-sm");

    $('#myTab a').click(function (e) {
        e.preventDefault()
        $(this).tab('show')
    });

    $(".caret-toggle").click(function(e) {
        var a = $(this);
        e.preventDefault();
        $(a.attr("data-target")).toggle();
        a.toggleClass("toggled");
    })

    $("#openAll").click(function(e) {
        e.preventDefault();
        $(".subsection").show();
        $(".caret-toggle").addClass("toggled");
    })

    $("#closeAll").click(function(e) {
        e.preventDefault();
        $(".subsection").hide();
        $(".toggled").removeClass("toggled");
    })

    var activate_section = function(event) {
        var a = $(this);
        event.preventDefault();
        $(".section").hide();
        $(".menu-toggle").removeClass("menu-toggle");
        $(a.attr("data-target")).show();
        a.addClass("menu-toggle");
        a.prev().addClass("menu-toggle");
        $("#title").text(a.attr("data-title"));
    }

    $(".section-menu-link").click(activate_section);

    if ($('.section[visible="true"][has-video="true"]').length > 0) {
        var section_menu_to_clik = $('.section[visible="true"][has-video="true"]').first().attr("data-menu-link");
    } else if ($('.section[visible="true"]').length > 0) {
        var section_menu_to_clik = $('.section[visible="true"]').first().attr("data-menu-link");
    } else {
        var section_menu_to_clik = $('.section').first().attr("data-menu-link");
    }

    $("#" + section_menu_to_clik).click();
});
