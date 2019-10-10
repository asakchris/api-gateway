package com.example.token.vo;

import lombok.*;

@AllArgsConstructor
@NoArgsConstructor
@Setter
@Getter
@ToString
public class TokenRequest {
    private String scope;
    private String oracle_token_action;
    private String grant_type;
    private String oracle_token_attrs_retrieval;
    private String username;
    private String password;
    private String assertion;
}
