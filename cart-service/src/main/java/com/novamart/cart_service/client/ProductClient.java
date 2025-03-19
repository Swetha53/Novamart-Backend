package com.novamart.cart_service.client;

import com.novamart.cart_service.FeignSslConfig;
import com.novamart.cart_service.dto.ApiResponse;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.List;

@FeignClient(name = "product", url = "https://product:8443", configuration = FeignSslConfig.class)
public interface ProductClient {
    @RequestMapping(method = RequestMethod.GET, value = "/api/products")
    ApiResponse getProduct(@RequestParam("productId") String productId);
}
