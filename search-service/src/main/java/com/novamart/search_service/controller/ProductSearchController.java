package com.novamart.search_service.controller;

import com.novamart.search_service.dto.ApiResponse;
import com.novamart.search_service.dto.ProductSearchRequest;
import com.novamart.search_service.service.ProductSearchService;
import lombok.AllArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;


@CrossOrigin(origins = "*")
@RestController
@RequestMapping("/api/search")
@AllArgsConstructor
public class ProductSearchController {
    private final ProductSearchService productSearchService;

    @GetMapping
    @ResponseStatus(HttpStatus.OK)
    public ApiResponse searchProducts(@RequestBody ProductSearchRequest productSearchRequest) {
        return productSearchService.searchProducts(productSearchRequest);
    }
}
