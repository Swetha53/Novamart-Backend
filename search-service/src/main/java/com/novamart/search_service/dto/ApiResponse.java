package com.novamart.search_service.dto;

import com.novamart.search_service.model.ProductSearch;

import java.util.List;

public record ApiResponse(int status, String message, List<ProductSearch> body) {
}
