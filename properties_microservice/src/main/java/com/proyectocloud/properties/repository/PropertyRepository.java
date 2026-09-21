package com.proyectocloud.properties.repository;

import com.proyectocloud.properties.entity.Property;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PropertyRepository extends JpaRepository<Property, Long> {

    Page<Property> findByEstado(String estado, Pageable pageable);
}
