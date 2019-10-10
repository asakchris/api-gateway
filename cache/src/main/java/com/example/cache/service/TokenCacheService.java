package com.example.cache.service;

import com.example.cache.vo.Token;

public interface TokenCacheService {
    Token cacheToken(Token token);
    Token getToken(String applicationToken);
}
