package com.novamart.order_service.client;

import com.novamart.order_service.FeignSslConfig;
import com.novamart.order_service.dto.ApiResponse;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;

@FeignClient(name = "cart", url = "https://cart:8443", configuration = FeignSslConfig.class)
public interface CartClient {
    @RequestMapping(method = RequestMethod.DELETE, value = "/api/cart/clear")
    ApiResponse clearCart(@RequestParam String userId);
}
