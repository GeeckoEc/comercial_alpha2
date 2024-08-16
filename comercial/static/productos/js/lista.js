function crear () {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", "{{ csrf_token }}");
        }
    });
    $.ajax({
        url:        '{% url "crear_producto" %}',
        dataType:   'JSON',
        type:       'POST',
        data:       {
            codigo:         $('#codigo').val(),
            marca:          $('#marca').val(),
            nombre:         $('#nombre').val(),
            presentacion:   $('#presentacion').val(),
            descripcion:    $('#descripcion').val(),
            precio:         $('#precio').val()
        }
    }).done(function (data) {
        alert(JSON.stringify(data))
    })
}