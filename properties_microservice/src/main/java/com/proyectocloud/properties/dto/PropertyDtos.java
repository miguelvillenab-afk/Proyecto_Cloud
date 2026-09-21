package com.proyectocloud.properties.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import java.math.BigDecimal;

/** Equivalente a schemas.py: separa lo que la API recibe/devuelve del modelo de BD. */
public class PropertyDtos {

    public record LocationDto(
            @NotBlank String pais,
            @NotBlank String ciudad,
            @NotBlank String direccion
    ) {}

    public record PropertyCreateRequest(
            @NotBlank String idAnfitrion,
            @NotBlank @Size(max = 200) String titulo,
            @NotNull @DecimalMin(value = "0.0", inclusive = false) BigDecimal precioNoche,
            @NotNull @Min(1) Integer capacidad,
            @Valid @NotNull LocationDto ubicacion
    ) {}

    public record PropertyUpdateRequest(
            @NotBlank @Size(max = 200) String titulo,
            @NotNull @DecimalMin(value = "0.0", inclusive = false) BigDecimal precioNoche,
            @NotNull @Min(1) Integer capacidad,
            @NotBlank String estado,
            @Valid @NotNull LocationDto ubicacion
    ) {}

    public record PropertyResponse(
            Long id,
            String idAnfitrion,
            String titulo,
            BigDecimal precioNoche,
            Integer capacidad,
            String estado,
            LocationDto ubicacion
    ) {}

    /**
     * Envelope paginado para GET /properties.
     * Contiene todo lo que el frontend necesita para renderizar
     * controles de paginación sin hacer peticiones extra:
     * - content: items de la página actual
     * - page/size: eco de lo pedido (page base 0)
     * - totalElements/totalPages: para "Página X de Y" y "20,000 resultados"
     * - first/last/hasNext/hasPrevious: para habilitar/deshabilitar botones
     */
    public record PagedPropertyResponse(
            java.util.List<PropertyResponse> content,
            int page,
            int size,
            long totalElements,
            int totalPages,
            boolean first,
            boolean last,
            boolean hasNext,
            boolean hasPrevious
    ) {}
}
