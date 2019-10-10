package com.example.token.service;

import com.example.token.vo.TokenResponse;

public interface CacheService {
    TokenResponse cacheToken(String accessToken, TokenResponse response);
}
