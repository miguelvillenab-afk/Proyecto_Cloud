package com.proyectocloud.properties.controller;

import com.proyectocloud.properties.dto.PropertyDtos.*;
import com.proyectocloud.properties.entity.Location;
import com.proyectocloud.properties.entity.Property;
import com.proyectocloud.properties.repository.PropertyRepository;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

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

    @GetMapping
    public List<PropertyResponse> getAllProperties() {
        return propertyRepository.findAll().stream()
                .map(PropertyController::toResponse)
                .toList();
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
