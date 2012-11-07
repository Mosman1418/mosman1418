$(function(){
    $('#person_select').select2({
        placeholder: "Search for a person",
        minimumInputLength: 1,
        allowClear: true,
        ajax: {
                url: "/people/autocomplete/",
                    dataType: 'json',
                    data: function (term, page) {
                        return {
                            query: term,
                            page: page
                        };
                    },
                    results: function (data, page) { // parse the results into the format expected by Select2.
                        // since we are using custom formatting functions we do not need to alter remote JSON data
                        return {results: data.results, more: data.more};
                    }
                }
    });
    $('#add_person').click(function(event) {
        event.preventDefault();
        var data = $('#person_select').select2('data');
        $person = $('<li data-id="' + data.id + '" class="btn btn-info person-info">' + data.text + ' <i class="icon-white icon-remove-sign"></li>')
            .click(function() {
                remove_person($(this));
            });
        $('#related_people').append($person).append(' ');
        $('form').append('<input id="people-' + data.id + '" type="hidden" name="people" value="' + data.id + '">');
    });
    function remove_person(elem) {
        var id = elem.data('id');
        elem.remove();
        $('#people-' + id).remove();
    }
    $(".person-info").click(function() {
        remove_person($(this));
    });
});
