package com.example.token.service;

import java.util.Base64;

public class Main {
  public static void main(String[] args) {
    String gw = "OAUTH_EXT_GW:Pass^v!?D@zCTa*YJ?zCT&uy";
    System.out.println("encodedString: " + encode(gw));
    System.out.println("decodeString: " + decode(encode(gw)));
  }

  private static String encode(String value) {
    return new String(Base64.getEncoder().encode(value.getBytes()));
  }

  private static String decode(String value) {
    return new String(Base64.getDecoder().decode(value));
  }
}
