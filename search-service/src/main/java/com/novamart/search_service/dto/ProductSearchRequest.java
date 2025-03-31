package com.novamart.search_service.dto;

import java.util.List;

public record ProductSearchRequest(String name, String currencyCode, List<String> categories, Object attributes) {
}
