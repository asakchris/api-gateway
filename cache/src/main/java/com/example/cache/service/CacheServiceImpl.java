package com.example.cache.service;

import com.example.cache.vo.Token;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

@Service
public class CacheServiceImpl implements CacheService {
    @Override
    @Cacheable(value = "APP_TOKEN", key = "#applicationToken")
    public Token cache(String applicationToken, Token token) {
        return token;
    }
}
