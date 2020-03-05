function hashHandler() {
    // Reset to target tab and pane when loading the page with a hash.
    var url = document.location.toString();

    if (url.match('#')) {
        var panetarget = url.split('#')[1];
        var tabtarget = panetarget + '-tab';

        // Check that the hash isn't referring to a disabled tab.
        var valid_target = $('#' + tabtarget).not('.disabled');

        if (valid_target.length == 1) {
            // Reset to remove existing "active" tab and panel.
            $('#activity-panel-nav .nav-item .nav-link').removeClass('active');
            $('.tab-pane').removeClass('active show');

            // Set target tab and panel to active.
            $('#' + tabtarget).addClass('active');
            $('#' + panetarget).addClass('active show');

            // hack to prevent jumping scroll to the anchor tag on loading
            setTimeout(function() {
                window.scrollTo(0, 0);
            }, 1);
        }
    }
}


$(function () {
    // Change the hash in the URL when a user clicks on a nav item.
    $('#activity-panel-nav .nav-item').not('disabled').on('click', function (e) {
        console.log( $( this ).text() );
        history.pushState({}, '', e.target.hash);
    });

    // Run this to handle a hash on page loading.
    hashHandler();
});
