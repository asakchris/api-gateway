package com.example.cache.service;

import com.example.cache.vo.Token;

public interface CacheService {
    Token cache(String applicationToken, Token token);
}
