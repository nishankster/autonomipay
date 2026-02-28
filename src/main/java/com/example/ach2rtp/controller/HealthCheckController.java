package com.example.ach2rtp.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

/**
 * REST controller for health checks and service status.
 */
@RestController
@RequestMapping("/v1/health")
public class HealthCheckController {

    /**
     * Get service health status.
     * 
     * @return Health status
     */
    @GetMapping("/status")
    public ResponseEntity<?> getHealthStatus() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "UP");
        response.put("service", "ach-to-rtp-service");
        response.put("version", "1.0.0");
        response.put("timestamp", System.currentTimeMillis());
        
        return ResponseEntity.ok(response);
    }

    /**
     * Liveness probe for Kubernetes.
     * 
     * @return Liveness status
     */
    @GetMapping("/live")
    public ResponseEntity<?> liveness() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "UP");
        return ResponseEntity.ok(response);
    }

    /**
     * Readiness probe for Kubernetes.
     * 
     * @return Readiness status
     */
    @GetMapping("/ready")
    public ResponseEntity<?> readiness() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "READY");
        return ResponseEntity.ok(response);
    }
}
