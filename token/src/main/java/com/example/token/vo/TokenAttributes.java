package com.example.token.vo;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

@AllArgsConstructor
@NoArgsConstructor
@Setter
@Getter
@Builder(toBuilder = true)
@ToString
@JsonInclude(JsonInclude.Include.NON_NULL)
public class TokenAttributes {
    private long exp;
    private String prn;
    @JsonProperty("oracle.oauth.client_origin_id")
    private String clientOrigin;
    private long iat;
}
