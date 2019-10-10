package com.example.random.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;

import java.util.AbstractMap;
import java.util.Collections;
import java.util.Map;
import java.util.concurrent.ThreadLocalRandom;
import java.util.stream.Collectors;
import java.util.stream.Stream;

@RestController
public class RandomController {
  private static Logger log = LoggerFactory.getLogger(RandomController.class);

  @GetMapping(value = "/number")
  public ResponseEntity<Map<String, Integer>> number(
      @RequestHeader(name = "authuid") String userName) {
    log.info("userName: {}", userName);
    Map<String, Integer> message =
        Collections.unmodifiableMap(
            Stream.of(new AbstractMap.SimpleEntry<>("message", getRandomNumber()))
                .collect(Collectors.toMap((o) -> o.getKey(), (o) -> o.getValue())));
    return ResponseEntity.ok(message);
  }

  private Integer getRandomNumber() {
    return ThreadLocalRandom.current().nextInt(1, 101);
  }
}
