package com.novamart.notification_service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class EmailKeyProvider {
    @Value("${spring.mail.username}")
    private String emailKey;

    public String getEmailKey() {
        return emailKey;
    }
}
