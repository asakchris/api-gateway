package com.example.welcome.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;

import java.util.AbstractMap;
import java.util.Collections;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;

@RestController
public class WelcomeController {
  private static Logger log = LoggerFactory.getLogger(WelcomeController.class);

  @GetMapping(value = "message")
  public ResponseEntity<Map<String, String>> welcome(
      @RequestHeader(name = "authuid") String userName) {
    log.info("userName: {}", userName);
    Map<String, String> message =
        Collections.unmodifiableMap(
            Stream.of(new AbstractMap.SimpleEntry<>("message", "Welcome " + userName))
                .collect(Collectors.toMap((o) -> o.getKey(), (o) -> o.getValue())));
    return ResponseEntity.ok(message);
  }
}
