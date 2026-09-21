package com.proyectocloud.properties.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Health check para el ALB Target Group (tg-ms-properties-8081).
 * No toca la BD a propósito: el TG debe medir si el proceso responde,
 * no la latencia de MySQL (un COUNT sobre 20k cruzando AZ en t3.micro
 * supera el timeout del check y marca el target como unhealthy).
 */
@RestController
public class HealthController {

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of("status", "UP"));
    }
}
