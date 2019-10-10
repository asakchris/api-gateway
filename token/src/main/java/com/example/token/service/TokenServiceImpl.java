package com.example.token.service;

import com.example.token.vo.TokenAttributes;
import com.example.token.vo.TokenRequest;
import com.example.token.vo.TokenResponse;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.util.UUID;

@Service
public class TokenServiceImpl implements TokenService {
    private static Logger log = LoggerFactory.getLogger(TokenServiceImpl.class);

    @Autowired
    private CacheService cacheService;

    @Override
    public TokenResponse generateToken(TokenRequest request) {
        if (StringUtils.equals(request.getOracle_token_action(), "validate")) {
            return validateToken(request);
        }

        if (!StringUtils.equals(request.getScope(), "UserProfile.me")) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Invalid scope");
        }

        if (!StringUtils.equals(request.getGrant_type(), "password")) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Invalid grant_type");
        }

        if (StringUtils.equals(request.getUsername(), "foo@bar.com")) {
            if (request.getPassword().equals("Foo1234")) {
                return createToken(request.getUsername());
            } else {
                throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Invalid Password");
            }
        } else {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Invalid User");
        }
    }

    private TokenResponse createToken(String username) {
        String accessToken = UUID.randomUUID().toString();
        TokenResponse response = TokenResponse.builder().username(username).accessToken(accessToken).refreshToken(UUID.randomUUID().toString()).build();
        return cacheService.cacheToken(accessToken, response);
    }

    private TokenResponse validateToken(TokenRequest request) {
        if (!StringUtils.equals(request.getGrant_type(), "oracle-idm:/oauth/grant-type/resource-access-token/jwt")) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Invalid grant_type");
        }

        if (StringUtils.isEmpty(request.getAssertion())) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Invalid assertion");
        }

        TokenResponse cacheResponse = cacheService.cacheToken(request.getAssertion(), null);
        if (cacheResponse == null) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Invalid Token");
        }
        TokenAttributes attributes = TokenAttributes
                .builder()
                .exp(1570640471)
                .prn(cacheResponse.getUsername())
                .clientOrigin("OAUTH_EXT_GW")
                .iat(1570636871)
                .build();
        TokenResponse response = cacheResponse
                .toBuilder()
                .successful(true)
                .attributes(attributes)
                .build();
        return response;
    }
}
