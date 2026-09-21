package com.proyectocloud.properties.controller;

import com.proyectocloud.properties.dto.PropertyDtos.*;
import com.proyectocloud.properties.entity.Location;
import com.proyectocloud.properties.entity.Property;
import com.proyectocloud.properties.repository.PropertyRepository;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import jakarta.validation.Valid;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.Set;

/**
 * API de Catálogo de Propiedades (Microservicio 2).
 * Sin capa de service separada: para un CRUD de este tamaño, el controller
 * hablando directo con el repositorio es suficiente (mismo criterio que
 * main.py + crud.py en el microservicio de Usuarios).
 */
@RestController
@RequestMapping("/properties")
@CrossOrigin(origins = "*")
public class PropertyController {

    private final PropertyRepository propertyRepository;

    public PropertyController(PropertyRepository propertyRepository) {
        this.propertyRepository = propertyRepository;
    }

    private static final Set<String> SORTABLE_FIELDS =
            Set.of("id", "titulo", "precioNoche", "capacidad", "estado", "idAnfitrion");

    private static final int MAX_PAGE_SIZE = 100;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public PropertyResponse createProperty(@Valid @RequestBody PropertyCreateRequest request) {
        Property property = new Property();
        property.setIdAnfitrion(request.idAnfitrion());
        property.setTitulo(request.titulo());
        property.setPrecioNoche(request.precioNoche());
        property.setCapacidad(request.capacidad());
        property.setEstado("ACTIVO");

        Location location = new Location();
        location.setPais(request.ubicacion().pais());
        location.setCiudad(request.ubicacion().ciudad());
        location.setDireccion(request.ubicacion().direccion());
        property.setLocation(location);

        return toResponse(propertyRepository.save(property));
    }

    @Operation(summary = "Listar propiedades con paginación",
            description = "Devuelve una página de propiedades. page base 0, size máx 100. "
                    + "Filtra opcionalmente por estado (ACTIVO/INACTIVO).")
    @GetMapping
    public PagedPropertyResponse getAllProperties(
            @Parameter(description = "Número de página, base 0", example = "0")
            @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Tamaño de página (1-100)", example = "20")
            @RequestParam(defaultValue = "20") int size,
            @Parameter(description = "Campo de ordenamiento", example = "id")
            @RequestParam(defaultValue = "id") String sortBy,
            @Parameter(description = "Dirección: asc o desc", example = "asc")
            @RequestParam(defaultValue = "asc") String direction,
            @Parameter(description = "Filtro opcional por estado", example = "ACTIVO")
            @RequestParam(required = false) String estado) {

        if (page < 0) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "page debe ser >= 0");
        }
        if (size < 1 || size > MAX_PAGE_SIZE) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST, "size debe estar entre 1 y " + MAX_PAGE_SIZE);
        }
        if (!SORTABLE_FIELDS.contains(sortBy)) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST, "sortBy inválido. Permitidos: " + SORTABLE_FIELDS);
        }
        Sort.Direction dir;
        try {
            dir = Sort.Direction.fromString(direction);
        } catch (IllegalArgumentException e) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "direction debe ser 'asc' o 'desc'");
        }

        Pageable pageable = PageRequest.of(page, size, Sort.by(dir, sortBy));

        Page<Property> result;
        if (estado != null && !estado.isBlank()) {
            result = propertyRepository.findByEstado(estado.trim().toUpperCase(), pageable);
        } else {
            result = propertyRepository.findAll(pageable);
        }

        List<PropertyResponse> content = result.getContent().stream()
                .map(PropertyController::toResponse)
                .toList();

        return new PagedPropertyResponse(
                content,
                result.getNumber(),
                result.getSize(),
                result.getTotalElements(),
                result.getTotalPages(),
                result.isFirst(),
                result.isLast(),
                result.hasNext(),
                result.hasPrevious()
        );
    }

    @GetMapping("/{id}")
    public PropertyResponse getPropertyById(@PathVariable Long id) {
        return toResponse(findOrThrow(id));
    }

    @PutMapping("/{id}")
    public PropertyResponse updateProperty(@PathVariable Long id, @Valid @RequestBody PropertyUpdateRequest request) {
        Property property = findOrThrow(id);
        property.setTitulo(request.titulo());
        property.setPrecioNoche(request.precioNoche());
        property.setCapacidad(request.capacidad());
        property.setEstado(request.estado());

        Location location = property.getLocation();
        if (location == null) {
            location = new Location();
            property.setLocation(location);
        }
        location.setPais(request.ubicacion().pais());
        location.setCiudad(request.ubicacion().ciudad());
        location.setDireccion(request.ubicacion().direccion());

        return toResponse(propertyRepository.save(property));
    }

    /** Borrado lógico: marca INACTIVO en vez de eliminar la fila (ver README). */
    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deleteProperty(@PathVariable Long id) {
        Property property = findOrThrow(id);
        property.setEstado("INACTIVO");
        propertyRepository.save(property);
    }

    private Property findOrThrow(Long id) {
        return propertyRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Propiedad no encontrada"));
    }

    private static PropertyResponse toResponse(Property p) {
        LocationDto locationDto = null;
        if (p.getLocation() != null) {
            Location l = p.getLocation();
            locationDto = new LocationDto(l.getPais(), l.getCiudad(), l.getDireccion());
        }
        return new PropertyResponse(
                p.getId(), p.getIdAnfitrion(), p.getTitulo(),
                p.getPrecioNoche(), p.getCapacidad(), p.getEstado(), locationDto
        );
    }
}
