package com.example.token.service;

import com.example.token.vo.TokenResponse;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

@Service
public class CacheServiceImpl implements CacheService {
    @Cacheable(value = "ACCESS_TOKEN", key = "#accessToken")
    public TokenResponse cacheToken(String accessToken, TokenResponse response) {
        return response;
    }
}
