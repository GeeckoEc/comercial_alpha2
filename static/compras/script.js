let lista_productos = []
        $(document).ready(()=>{
            // sessionStorage.clear()
            lista_seleccionados()
        })
        function abrir_selector () {
            $('#productos-modal').modal('toggle')
            productos_sin_seleccionar()
        }

        function productos_sin_seleccionar () {
            let filtrar = []
            if (sessionStorage.getItem('seleccionados') !== null) {
                let lista = JSON.parse(sessionStorage.getItem('seleccionados'))
                $.each(lista, function(index, item){
                    filtrar.push(item.id)
                })
            } else {
                filtrar = null
            }
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    xhr.setRequestHeader("X-CSRFToken", "{{ csrf_token }}");
                }
            });
            $.ajax({
                    url:        '{% url "gestion_productos" %}',
                    type:       'POST',
                    dataType:   'JSON',
                    data:       {
                        accion:     'lista_filtrada',
                        filtrar:    JSON.stringify(filtrar)
                    }
                }).done(function (data){
                    if (data.success) {
                        lista_productos = data.productos
                        $('#productos').html('')
                        $.each(data.productos, function (index, producto) {
                            $('#productos').append(`
                                <tr>
                                    <td>${producto.nombre}</td>
                                    <td>
                                        <button class="btn btn-primary" onclick="agregar(${producto.id})"><i class="bi bi-check2-circle"></i></button>
                                    </td>
                                </tr>
                            `)
                        })
                    } else {
                        $.alert({
                            icon:               'fa-circle-xmark',
                            title:              'Error',
                            type:               'red',
                            content:            data.message,
                            animateFromElement: false,
                            theme:              'modern'
                        })
                    }
                })
        }

        function agregar (id) {
            let producto = lista_productos.find((item) => item.id === id);
            $('#productos-modal').modal('toggle')
            $.confirm({
                icon:               'fa-boxes-stacked',
                title:              'Cantidad',
                type:               'blue',
                content:            '' + 
                                    '<p>Ingresa la cantidad y costo para <strong>' + producto.nombre + ' ' + producto.presentacion + '</strong>.</p>' +     
                                    '<div class="form-floating">' +
                                    '<input type="number" id="cantidad" name="cantidad" class="form-control" placeholder="cantidad">' + 
                                    '<label for="cantidad">Cantidad</label>' +
                                    '</div>' +
                                    '<div class="form-floating mt-3">' +
                                    '<input type="text" id="costo" name="costo" class="form-control" placeholder="costo">' + 
                                    '<label for="costo">Costo $</label>' +
                                    '</div>',
                animateFromElement: false,
                theme:              'modern',
                buttons:            {
                    Aceptar:    function () {
                        if (sessionStorage.getItem('seleccionados') == null) {
                            sessionStorage.setItem('seleccionados', JSON.stringify([{id: id, cantidad: $('#cantidad').val(), costo: $('#costo').val()}]))
                        } else {
                            let seleccionados = JSON.parse(sessionStorage.getItem('seleccionados'))
                            seleccionados.push({id: id, cantidad: $('#cantidad').val()})
                            sessionStorage.setItem('seleccionados', JSON.stringify(seleccionados))
                        }
                        lista_seleccionados()
                    }, 
                    Cancelar:   function () {}
                }
            })
            if (sessionStorage.getItem('seleccionados') == null) {

            }
        }

        function lista_seleccionados () {
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    xhr.setRequestHeader("X-CSRFToken", "{{ csrf_token }}");
                }
            });
            $.ajax({
                url:        '{% url "gestion_productos" %}',
                type:       'POST',
                dataType:   'JSON',
                data:       {
                    accion: 'lista', 
                    estado: true
                }
            }).done(function (data){
                $('#productos-seleccionados').html('')
                if (data.success) {
                    let ids = JSON.parse(sessionStorage.getItem('seleccionados'))
                    let total = 0.00
                    $.each(ids, function(index, id){
                        let info = data.productos.find((producto) => producto.id == id.id)
                        let marca = data.marcas.find((item) => item.id === info.marca)
                        total = parseFloat(total) + (parseFloat(info.precio) * parseInt(id.cantidad))
                        $('#productos-seleccionados').append(`
                            <tr>
                                <td style="vertical-align: middle;">${index + 1}</td>
                                <td style="vertical-align: middle;">${info.nombre} ${marca.nombre} ${info.presentacion}</td>
                                <td style="vertical-align: middle; text-align: right;">${id.cantidad}</td>
                                <td style="vertical-align: middle; text-align: right;">${parseFloat(info.precio).toFixed(2)}</td>
                                <td style="vertical-align: middle; text-align: right;">${parseFloat((info.precio) * parseInt(id.cantidad)).toFixed(2)}</td>
                                <td style="vertical-align: middle;">
                                    <button class="btn btn-danger" onclick="quitar_producto(${id.id})"><i class="bi bi-x"></i></button>
                                </td>
                            </tr>
                        `)
                    })
                    $('#total').val(total.toFixed(2))
                }
            })
        }

        function quitar_producto (id) {
            $.alert({
                icon:               'fa fa-circle-exclamation',
                title:              'Quitar Producto',
                type:               'red',
                content:            '¿Desea quitar el producto de la lista?',
                theme:              'modern',
                animateFromElement: false,
                buttons:            {
                    Sí: () => {
                        let seleccionados = JSON.parse(sessionStorage.getItem('seleccionados'))
                        seleccionados = seleccionados.filter(item => item.id !== id)
                        sessionStorage.setItem('seleccionados', JSON.stringify(seleccionados))
                        lista_seleccionados()
                    },
                    No: () => {}
                }
            })
        }

        function procesar () {
            $.alert({
                icon:               'fa fa-circle-exclamation',
                title:              'Procesar Compra',
                type:               'red',
                content:            '¿Desea procesar la compra?',
                theme:              'modern',
                animateFromElement: false,
                buttons:            {
                    Sí: () => {
                        $.ajax({
                            url:        '{% url "gestion_compras" %}',
                            type:       'POST',
                            dataType:   'JSON',
                            data:       {
                                accion:     'crear_compra',
                                productos:  JSON.parse(sessionStorage.getItem('seleccionados')),
                                proveedor:  $('#proveedor').val(),
                                factura:    $('#factura').val(),
                                total:      $('#total').val()
                            }
                        }).then((respuesta) => {
                            if (respuesta.success) {
                                mensaje('green', 'fa fa-circle-check', 'Procesar Compra', respuesta.message)
                                sessionStorage.removeItem('seleccionados')
                                $('#proveedor').val('0')
                                $('#factura').val('')
                                $('#total').val('')
                            }
                        }).catch((error) => {
                            let respuesta = JSON.parse(error.responseText)
                            mensaje('red', 'fa fa-circle-xmark', 'Error al crear la compra: ', respuesta.message)
                        })
                    },
                    No: () => {}
                }
            })
        }

        function buscar (buscar) {
            let seleccionados   =   JSON.parse(sessionStorage.getItem('seleccionados'))
            let filtrar         =   []
            $.each(seleccionados, (index, item) => {
                filtrar.push(item.id)
            })
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    xhr.setRequestHeader("X-CSRFToken", "{{ csrf_token }}");
                }
            });
            $.ajax({
                url:        '{% url "gestion_productos" %}',
                type:       'POST',
                dataType:   'JSON',
                data:       {
                    accion:     'buscar_sin_seleccionar',
                    buscar:     buscar,
                    filtrar:    JSON.stringify(filtrar)
                }
            }).then((respuesta) => {
                lista_productos = respuesta.productos
                $('#productos').html('')
                $.each(lista_productos, function (index, producto) {
                    $('#productos').append(`
                        <tr>
                            <td>${producto.nombre}</td>
                            <td>
                                <button class="btn btn-primary" onclick="agregar(${producto.id})"><i class="bi bi-check2-circle"></i></button>
                            </td>
                        </tr>
                    `)
                })
            }).catch((error) => {
                let respuesta = JSON.parse(error.responseText)
                mensaje('red', 'fa fa-circle-xmark', 'Error al Buscar', respuesta.message)
            })
        }

        function mensaje (color, icono, titulo, mensaje) {
            $.alert({
                icon:               icono,
                title:              titulo,
                type:               color,
                content:            mensaje,
                theme:              'modern',
                animateFromElement: false,
                buttons:            {
                    Cerrar: function () {}
                }
            })
        }