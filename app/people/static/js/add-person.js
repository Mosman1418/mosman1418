$(function(){
    $('input:radio[name=birth_date_type]').change(function() {
        var date_type = $('input:radio[name=birth_date_type]:checked').val();
        if (date_type == 'single') {
            $('#id_birth_latest_date_year').parent().parent().hide();
        } else if (date_type == 'range') {
            $('#id_birth_latest_date_year').parent().parent().show();
        }
    });
    $('input:radio[name=death_date_type]').change(function() {
        var date_type = $('input:radio[name=death_date_type]:checked').val();
        if (date_type == 'single') {
            $('#id_death_latest_date_year').parent().parent().hide();
        } else if (date_type == 'range') {
            $('#id_death_latest_date_year').parent().parent().show();
        }
    });
    $('#id_birth_latest_date_year').parent().parent().hide();
    $('#id_death_latest_date_year').parent().parent().hide();
});
