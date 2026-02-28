package com.example.ach2rtp.controller;

import com.example.ach2rtp.service.AchConversionService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/**
 * REST controller for ACH file upload and conversion.
 */
@RestController
@RequestMapping("/v1/conversion")
@CrossOrigin(origins = "*", maxAge = 3600)
public class FileUploadController {

    private static final Logger logger = LoggerFactory.getLogger(FileUploadController.class);

    @Autowired
    private AchConversionService achConversionService;

    /**
     * Upload and convert an ACH file to RTP messages.
     * 
     * @param file The ACH file to upload
     * @return Conversion result with statistics
     */
    @PostMapping("/upload")
    public ResponseEntity<?> uploadAndConvert(@RequestParam("file") MultipartFile file) {
        logger.info("Received file upload request: {}", file.getOriginalFilename());
        
        if (file.isEmpty()) {
            return ResponseEntity.badRequest().body(createErrorResponse("File is empty"));
        }
        
        try {
            // Validate file size (10 MB max)
            long maxFileSize = 10 * 1024 * 1024; // 10 MB
            if (file.getSize() > maxFileSize) {
                return ResponseEntity.badRequest()
                        .body(createErrorResponse("File size exceeds maximum allowed size of 10 MB"));
            }
            
            // Convert file
            AchConversionService.ConversionResult result = achConversionService.convertAndPublish(
                    file.getInputStream(),
                    file.getOriginalFilename()
            );
            
            logger.info("Conversion completed for file: {}", file.getOriginalFilename());
            
            return ResponseEntity.ok(result);
            
        } catch (IOException e) {
            logger.error("Error reading uploaded file: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(createErrorResponse("Error reading file: " + e.getMessage()));
        } catch (Exception e) {
            logger.error("Unexpected error during conversion: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(createErrorResponse("Unexpected error: " + e.getMessage()));
        }
    }

    /**
     * Create an error response map.
     * 
     * @param message Error message
     * @return Error response map
     */
    private Map<String, Object> createErrorResponse(String message) {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "ERROR");
        response.put("message", message);
        response.put("timestamp", System.currentTimeMillis());
        return response;
    }
}
