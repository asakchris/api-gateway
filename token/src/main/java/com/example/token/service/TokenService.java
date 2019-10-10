package com.example.token.service;

import com.example.token.vo.TokenRequest;
import com.example.token.vo.TokenResponse;

public interface TokenService {
    TokenResponse generateToken(TokenRequest request);
}
