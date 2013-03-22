$(function(){
    function show_url_only(help) {
        $('.form-field:not(.url)').hide();
        $('#id_url_help').text(help);
    }
    $('#id_birth_record').select2('disable');
    $('#id_death_record').select2('disable');
    $('#id_category').change(function() {
        var category = $('#id_category').val();
        if (category == 'trove') {
            show_url_only('Enter the url of a Trove newspaper article');
        } else if (category == 'naa') {
            show_url_only('Enter the url of a National Archives file (just cut and paste from RecordSearch)');
        } else if (category == 'awm') {
            show_url_only('Enter the url of a record from the AWM\'s biographical or collection databases');
        } else if (category == 'cwgc') {
            show_url_only('Enter the url of a record from the CWGC\'s database');
        } else {
            $('.form-field').show();
            $('#id_publication_date_end_year').parent().parent().hide();
            $('#id_url_help').text('');
        }
    });
    $('input:radio[name=publication_date_type]').change(function() {
        var date_type = $('input:radio[name=publication_date_type]:checked').val();
        if (date_type == 'single') {
            $('#id_publication_date_end_year').parent().parent().hide();
        } else if (date_type == 'range') {
            $('#id_publication_date_end_year').parent().parent().show();
        }
    });
    $('#id_publication_date_end_year').parent().parent().hide();
});
