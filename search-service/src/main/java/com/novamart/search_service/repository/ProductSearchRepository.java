package com.novamart.search_service.repository;

import com.novamart.search_service.model.ProductSearch;
import org.springframework.data.elasticsearch.annotations.Query;
import org.springframework.data.elasticsearch.repository.ElasticsearchRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

public interface ProductSearchRepository extends ElasticsearchRepository<ProductSearch, String> {
    @Query("{\"bool\": {\"must\": [{\"match\": {\"name\": \"?0\"}}]}}")
    List<ProductSearch> searchByName(String name);

    @Query("{\"bool\": {\"must\": [{\"match\": {\"currencyCode\": \"?0\"}}]}}")
    List<ProductSearch> searchByCurrencyCode(String currencyCode);

    @Query("{\"bool\": {\"must\": [{\"match\": {\"categories\": \"?0\"}}]}}")
    List<ProductSearch> searchByCategories(List<String> categories);

    @Query("{\"bool\": {\"must\": [{\"match\": {\"attributes.color\": \"?0\"}}]}}")
    List<ProductSearch> searchByColorAttribute(Object attributes);

    @Query("{\"bool\": {\"must\": [{\"match\": {\"name\": \"?0\"}}, {\"match\": {\"currencyCode\": \"?1\"}}]}}")
    List<ProductSearch> searchByNameAndCurrencyCode(String name, String currencyCode);

    @Query("{\"bool\": {\"must\": [{\"match\": {\"name\": \"?0\"}}, {\"match\": {\"categories\": \"?1\"}}]}}")
    List<ProductSearch> searchByNameAndCategories(String name, List<String> categories);

    @Query("{\"bool\": {\"must\": [{\"match\": {\"name\": \"?0\"}}, {\"match\": {\"attributes.color\": \"?1\"}}]}}")
    List<ProductSearch> searchByNameAndColorAttribute(String name, Object attributes);

    @Query("{\"bool\": {\"must\": [{\"match\": {\"currencyCode\": \"?0\"}}, {\"match\": {\"categories\": \"?1\"}}]}}")
    List<ProductSearch> searchByCurrencyCodeAndCategories(String currencyCode, List<String> categories);

    @Query("{\"bool\": {\"must\": [{\"match\": {\"currencyCode\": \"?0\"}}, {\"match\": {\"attributes.color\": \"?1\"}}]}}")
    List<ProductSearch> searchByCurrencyCodeAndColorAttribute(String currencyCode, Object attributes);

    @Query("{\"bool\": {\"must\": [{\"match\": {\"categories\": \"?0\"}}, {\"match\": {\"attributes.color\": \"?1\"}}]}}")
    List<ProductSearch> searchByCategoriesAndColorAttribute(List<String> categories, Object attributes);

    @Query("{\"bool\": {\"must\": [{\"match\": {\"name\": \"?0\"}}, {\"match\": {\"currencyCode\": \"?1\"}}, {\"match\": {\"categories\": \"?2\"}}]}}")
    List<ProductSearch> searchByNameCurrencyCodeAndCategories(String name, String currencyCode, List<String> categories);

    @Query("{\"bool\": {\"must\": [{\"match\": {\"name\": \"?0\"}}, {\"match\": {\"currencyCode\": \"?1\"}}, {\"match\": {\"attributes.color\": \"?2\"}}]}}")
    List<ProductSearch> searchByNameCurrencyAndColorAttribute(String name, String currencyCode, Object attributes);

    @Query("{\"bool\": {\"must\": [{\"match\": {\"name\": \"?0\"}}, {\"match\": {\"categories\": \"?1\"}}, {\"match\": {\"attributes.color\": \"?2\"}}]}}")
    List<ProductSearch> searchByNameCategoriesAndColorAttribute(String name, List<String> categories, Object attributes);

    @Query("{\"bool\": {\"must\": [{\"match\": {\"currencyCode\": \"?0\"}}, {\"match\": {\"categories\": \"?1\"}}, {\"match\": {\"attributes.color\": \"?2\"}}]}}")
    List<ProductSearch> searchByCurrencyCodeCategoriesAndColorAttribute(String currencyCode, List<String> categories, Object attributes);

    @Query("{\"bool\": {\"must\": [{\"match\": {\"name\": \"?0\"}}, {\"match\": {\"currencyCode\": \"?1\"}}, {\"match\": {\"categories\": \"?2\"}}, {\"match\": {\"attributes.color\": \"?3\"}}]}}")
    List<ProductSearch> searchByAllFilters(String name, String currencyCode, List<String> categories, Object attributes);
}
