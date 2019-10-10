package com.example.cache.hazelcast;

import com.hazelcast.client.config.ClientConfig;
import com.hazelcast.client.config.XmlClientConfigBuilder;
import com.hazelcast.config.Config;
import com.hazelcast.config.ConfigLoader;
import com.hazelcast.config.XmlConfigBuilder;
import com.hazelcast.core.HazelcastInstance;
import com.hazelcast.spring.cache.HazelcastCacheManager;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.cache.CacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.net.URL;

import static com.hazelcast.client.HazelcastClient.newHazelcastClient;
import static com.hazelcast.core.Hazelcast.newHazelcastInstance;

@Configuration
public class HazelcastConfiguration {
    @Value("${hazelcast.file.path:hazelcast-LOCAL.xml}")
    private String cacheFilePath;

    @Value("${hazelcast.client.mode.enabled:false}")
    private boolean isClientModeEnabled;

    public Config config() throws Exception {
        URL url = ConfigLoader.locateConfig(cacheFilePath);
        return new XmlConfigBuilder(url).build();
    }

    public HazelcastInstance hazelcastLocalInstance() throws Exception {
        return newHazelcastInstance(config());
    }

    public ClientConfig clientConfig() throws Exception {
        return new XmlClientConfigBuilder(cacheFilePath).build();
    }

    public HazelcastInstance hazelcastClientInstance() throws Exception {
        return newHazelcastClient(clientConfig());
    }

    @Bean(name = "hazelcastInstance")
    @ConditionalOnMissingBean(HazelcastInstance.class)
    public HazelcastInstance hazelcastInstance() throws Exception {
        if (isClientModeEnabled) {
            return hazelcastClientInstance();
        }
        return hazelcastLocalInstance();
    }

    @Bean
    public CacheManager cacheManager() throws Exception {
        return new HazelcastCacheManager(hazelcastInstance());
    }
}
