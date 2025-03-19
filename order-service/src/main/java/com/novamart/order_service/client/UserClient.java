package com.novamart.order_service.client;

import com.novamart.order_service.FeignSslConfig;
import com.novamart.order_service.dto.ApiResponse;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;

@FeignClient(name = "user", url = "https://user:8443", configuration = FeignSslConfig.class)
public interface UserClient {
    @RequestMapping(method = RequestMethod.GET, value = "/api/users/authenticate")
    ApiResponse authenticateUser(@RequestParam String userId, @RequestParam String checkField, @RequestParam String value);
}
