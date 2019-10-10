package com.example.cache.controller;

import com.example.cache.service.TokenCacheService;
import com.example.cache.vo.Token;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping(value = "tokens")
public class CacheController {
  private static Logger log = LoggerFactory.getLogger(CacheController.class);

  private final TokenCacheService service;

  public CacheController(TokenCacheService service) {
    this.service = service;
  }

  @PostMapping(consumes = MediaType.APPLICATION_JSON_VALUE)
  public ResponseEntity<Token> cacheToken(@RequestBody Token token) {
    log.info("token: {}", token);
    Token response = service.cacheToken(token);
    return new ResponseEntity<>(response, HttpStatus.CREATED);
  }

  @GetMapping(params = "applicationToken")
  public ResponseEntity<Token> getToken(@RequestParam String applicationToken) {
    log.info("applicationToken: {}", applicationToken);
    Token response = service.getToken(applicationToken);
    return ResponseEntity.ok(response);
  }
}
