jQuery(function($) {
    $("#membership_app_fields-group div.inline-group").sortable({
        axis: 'y',
        placeholder: 'ui-state-highlight',
        forcePlaceholderSize: 'true',
        items: '.row1, .row2',
        update: update
    });
});
function update() {
    $('.row1, .row2').each(function(i) {
        $(this).find('input[id$=position]').val(i+1);
    });
}
jQuery(document).ready(function($){
    // hide order
    var order_index = $('#membership_app_fields-group div.inline-related').find('td.field-position').index();
    $('#membership_app_fields-group div.inline-related').find('td.field-position').hide();
    $('#membership_app_fields-group div.inline-related').find('th:nth-child(' + order_index +')').hide();

    $('.add-row a').click(update);

    $('#membershipapp_form').on("submit", function() {
        update();
    });
});
