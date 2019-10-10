package com.example.token.vo;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

import java.io.Serializable;

import static com.fasterxml.jackson.annotation.JsonInclude.*;

@AllArgsConstructor
@NoArgsConstructor
@Setter
@Getter
@Builder(toBuilder = true)
@ToString
@JsonInclude(Include.NON_NULL)
public class TokenResponse implements Serializable {
    @JsonIgnore
    private String username;

    @JsonProperty("access_token")
    private String accessToken;

    @JsonProperty("refresh_token")
    private String refreshToken;

    private Boolean successful;

    @JsonProperty("oracle_token_attrs_retrieval")
    private TokenAttributes attributes;
}
