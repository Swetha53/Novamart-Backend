package com.novamart.order_service.client;

import com.novamart.order_service.FeignSslConfig;
import com.novamart.order_service.dto.ApiResponse;
import com.novamart.order_service.dto.ReservationRequest;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;

@FeignClient(name = "inventory", url = "https://inventory:8443", configuration = FeignSslConfig.class)
public interface InventoryClient {
    @RequestMapping(method = RequestMethod.PUT, value = "/api/inventory/reserve")
    ApiResponse reserveInventory(@RequestBody ReservationRequest reservationRequest);

    @RequestMapping(method = RequestMethod.PUT, value = "/api/inventory/sell")
    ApiResponse sellInventory(@RequestParam String orderId, @RequestParam String productId, @RequestParam long quantity);

    @RequestMapping(method = RequestMethod.PUT, value = "/api/inventory/release")
    ApiResponse releaseInventory(@RequestParam String orderId, @RequestParam String productId, @RequestParam long quantity);
}
