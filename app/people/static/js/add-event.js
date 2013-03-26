$(function(){
    $('#id_person').select2('disable');
    $('input:radio[name=start_date_type]').change(function() {
        var date_type = $('input:radio[name=start_date_type]:checked').val();
        if (date_type == 'single') {
            $('#id_start_latest_date_year').parent().parent().hide();
        } else if (date_type == 'range') {
            $('#id_start_latest_date_year').parent().parent().show();
        }
    });
    $('input:radio[name=end_date_type]').change(function() {
        var date_type = $('input:radio[name=end_date_type]:checked').val();
        if (date_type == 'single') {
            $('#id_end_latest_date_year').parent().parent().hide();
        } else if (date_type == 'range') {
            $('#id_end_latest_date_year').parent().parent().show();
        }
    });
    $('#id_start_latest_date_year').parent().parent().hide();
    $('#id_end_latest_date_year').parent().parent().hide();
});
