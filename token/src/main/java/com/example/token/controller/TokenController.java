package com.example.token.controller;

import com.example.token.service.TokenService;
import com.example.token.vo.TokenRequest;
import com.example.token.vo.TokenResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class TokenController {
    private static Logger log = LoggerFactory.getLogger(TokenController.class);

    private final TokenService service;

    public TokenController(TokenService service) {
        this.service = service;
    }

    @PostMapping(value = "tokens", consumes = MediaType.APPLICATION_FORM_URLENCODED_VALUE)
    public ResponseEntity<TokenResponse> token(
            @RequestHeader(name = "Authorization") String authorization,
            @RequestHeader(name = "Host") String host,
            TokenRequest request) {
        log.info("authorization: {}, host: {}", authorization, host);
        log.info("request: {}", request);
        TokenResponse tokenResponse = service.generateToken(request);
        return new ResponseEntity<>(tokenResponse, HttpStatus.CREATED);
    }
}
