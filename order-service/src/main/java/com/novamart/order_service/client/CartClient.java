package com.novamart.order_service.client;

import com.novamart.order_service.dto.ApiResponse;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;

@FeignClient(name = "cart-service", url = "http://localhost:8092")
public interface CartClient {
    @RequestMapping(method = RequestMethod.DELETE, value = "/api/cart/clear")
    ApiResponse clearCart(@RequestParam String userId);
}
