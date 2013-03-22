$(function(){
    $('#person-select').select2({
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
});
