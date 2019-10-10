package com.example.cache.service;

import com.example.cache.vo.Token;
import org.apache.commons.lang3.StringUtils;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
public class TokenCacheServiceImpl implements TokenCacheService {
    private final CacheService service;

    public TokenCacheServiceImpl(CacheService service) {
        this.service = service;
    }

    @Override
    public Token cacheToken(Token token) {
        if (StringUtils.isEmpty(token.getApplicationToken())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "applicationToken is empty");
        }
        if (StringUtils.isEmpty(token.getAccessToken())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "accessToken is empty");
        }
        if (StringUtils.isEmpty(token.getRefreshToken())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "refreshToken is empty");
        }

        return service.cache(token.getApplicationToken(), token);
    }

    @Override
    public Token getToken(String applicationToken) {
        Token cache = service.cache(applicationToken, null);

        if (cache == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Token not found");
        }

        return cache;
    }
}
