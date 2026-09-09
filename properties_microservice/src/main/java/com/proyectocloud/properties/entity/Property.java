package com.proyectocloud.properties.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;

/**
 * Tabla "propiedades". id_anfitrion es una referencia logica al MS1 (Usuarios):
 * se guarda como texto plano, sin FK fisica entre microservicios.
 */
@Entity
@Table(name = "propiedades")
public class Property {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_propiedad")
    private Long id;

    @Column(name = "id_anfitrion", nullable = false, length = 255)
    private String idAnfitrion;

    @Column(name = "titulo", nullable = false, length = 200)
    private String titulo;

    @Column(name = "precio_noche", nullable = false, precision = 10, scale = 2)
    private BigDecimal precioNoche;

    @Column(name = "capacidad", nullable = false)
    private Integer capacidad;

    @Column(name = "estado", nullable = false, length = 20)
    private String estado;

    @OneToOne(mappedBy = "property", cascade = CascadeType.ALL, orphanRemoval = true)
    private Location location;

    public Property() {
    }

    // --- getters y setters ---

    public Long getId() {
        return id;
    }

    public String getIdAnfitrion() {
        return idAnfitrion;
    }

    public void setIdAnfitrion(String idAnfitrion) {
        this.idAnfitrion = idAnfitrion;
    }

    public String getTitulo() {
        return titulo;
    }

    public void setTitulo(String titulo) {
        this.titulo = titulo;
    }

    public BigDecimal getPrecioNoche() {
        return precioNoche;
    }

    public void setPrecioNoche(BigDecimal precioNoche) {
        this.precioNoche = precioNoche;
    }

    public Integer getCapacidad() {
        return capacidad;
    }

    public void setCapacidad(Integer capacidad) {
        this.capacidad = capacidad;
    }

    public String getEstado() {
        return estado;
    }

    public void setEstado(String estado) {
        this.estado = estado;
    }

    public Location getLocation() {
        return location;
    }

    public void setLocation(Location location) {
        this.location = location;
        if (location != null) {
            location.setProperty(this);
        }
    }
}
