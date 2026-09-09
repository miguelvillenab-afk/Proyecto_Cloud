package com.proyectocloud.properties.entity;

import jakarta.persistence.*;

/** Tabla "ubicaciones". Dueña de la FK id_propiedad (relación 1 a 1 con Property). */
@Entity
@Table(name = "ubicaciones")
public class Location {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_ubicacion")
    private Long id;

    @OneToOne
    @JoinColumn(name = "id_propiedad", nullable = false, unique = true)
    private Property property;

    @Column(name = "pais", nullable = false, length = 100)
    private String pais;

    @Column(name = "ciudad", nullable = false, length = 100)
    private String ciudad;

    @Column(name = "direccion", nullable = false, length = 255)
    private String direccion;

    public Location() {
    }

    public Long getId() {
        return id;
    }

    public Property getProperty() {
        return property;
    }

    public void setProperty(Property property) {
        this.property = property;
    }

    public String getPais() {
        return pais;
    }

    public void setPais(String pais) {
        this.pais = pais;
    }

    public String getCiudad() {
        return ciudad;
    }

    public void setCiudad(String ciudad) {
        this.ciudad = ciudad;
    }

    public String getDireccion() {
        return direccion;
    }

    public void setDireccion(String direccion) {
        this.direccion = direccion;
    }
}
