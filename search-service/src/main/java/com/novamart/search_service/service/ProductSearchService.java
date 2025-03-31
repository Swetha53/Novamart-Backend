package com.novamart.search_service.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.novamart.search_service.dto.ApiResponse;
import com.novamart.search_service.dto.ProductSearchRequest;
import com.novamart.search_service.model.ProductSearch;
import com.novamart.search_service.repository.ProductSearchRepository;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@AllArgsConstructor
@Slf4j
public class ProductSearchService {
    private final ProductSearchRepository productSearchRepository;
    private final ObjectMapper objectMapper;

    @KafkaListener(topics = "product", groupId = "product")
    public void consumeProduct(String product) {
        try {
            ProductSearch productModel = objectMapper.readValue(product, ProductSearch.class);
            productSearchRepository.save(productModel);
        } catch (Exception e) {
            log.error("Error consuming product: {}", e.getMessage());
        }
    }

    public ApiResponse searchProducts(ProductSearchRequest productSearchRequest) {
        List<ProductSearch> productSearches;
        if (productSearchRequest.name() == null) {
            if (productSearchRequest.currencyCode() == null) {
                if (productSearchRequest.categories() == null) {
                    if (productSearchRequest.attributes() == null) {
                        return new ApiResponse(400, "Bad Request", null);
                    } else {
                        productSearches = productSearchRepository.searchByColorAttribute(productSearchRequest.attributes());
                    }
                } else {
                    if (productSearchRequest.attributes() == null) {
                        productSearches = productSearchRepository.searchByCategories(productSearchRequest.categories());
                    } else {
                        productSearches = productSearchRepository.searchByCategoriesAndColorAttribute(productSearchRequest.categories(), productSearchRequest.attributes());
                    }
                }
            } else {
                if (productSearchRequest.categories() == null) {
                    if (productSearchRequest.attributes() == null) {
                        productSearches = productSearchRepository.searchByCurrencyCode(productSearchRequest.currencyCode());
                    } else {
                        productSearches = productSearchRepository.searchByCurrencyCodeAndColorAttribute(productSearchRequest.currencyCode(), productSearchRequest.attributes());
                    }
                } else {
                    if (productSearchRequest.attributes() == null) {
                        productSearches = productSearchRepository.searchByCurrencyCodeAndCategories(productSearchRequest.currencyCode(), productSearchRequest.categories());
                    } else {
                        productSearches = productSearchRepository.searchByCurrencyCodeCategoriesAndColorAttribute(productSearchRequest.currencyCode(), productSearchRequest.categories(), productSearchRequest.attributes());
                    }
                }
            }
        } else {
            if (productSearchRequest.currencyCode() == null) {
                if (productSearchRequest.categories() == null) {
                    if (productSearchRequest.attributes() == null) {
                        productSearches = productSearchRepository.searchByName(productSearchRequest.name());
                    } else {
                        productSearches = productSearchRepository.searchByNameAndColorAttribute(productSearchRequest.name(), productSearchRequest.attributes());
                    }
                } else {
                    if (productSearchRequest.attributes() == null) {
                        productSearches = productSearchRepository.searchByNameAndCategories(productSearchRequest.name(), productSearchRequest.categories());
                    } else {
                        productSearches = productSearchRepository.searchByNameCategoriesAndColorAttribute(productSearchRequest.name(), productSearchRequest.categories(), productSearchRequest.attributes());
                    }
                }
            } else {
                if (productSearchRequest.categories() == null) {
                    if (productSearchRequest.attributes() == null) {
                        productSearches = productSearchRepository.searchByNameAndCurrencyCode(productSearchRequest.name(), productSearchRequest.currencyCode());
                    } else {
                        productSearches = productSearchRepository.searchByNameCurrencyAndColorAttribute(productSearchRequest.name(), productSearchRequest.currencyCode(), productSearchRequest.attributes());
                    }
                } else {
                    if (productSearchRequest.attributes() == null) {
                        productSearches = productSearchRepository.searchByNameCurrencyCodeAndCategories(productSearchRequest.name(), productSearchRequest.currencyCode(), productSearchRequest.categories());
                    } else {
                        productSearches = productSearchRepository.searchByAllFilters(productSearchRequest.name(), productSearchRequest.currencyCode(), productSearchRequest.categories(), productSearchRequest.attributes());
                    }
                }
            }
        }
        return new ApiResponse(200, "Success", productSearches);
    }
}
