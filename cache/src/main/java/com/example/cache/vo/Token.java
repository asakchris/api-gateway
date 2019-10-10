package com.example.cache.vo;

import lombok.*;

import java.io.Serializable;

@AllArgsConstructor
@NoArgsConstructor
@Setter
@Getter
@ToString
public class Token implements Serializable {
    private String applicationToken;
    private String accessToken;
    private String refreshToken;
}
