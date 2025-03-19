package com.novamart.product_service.client;

import com.novamart.product_service.FeignSslConfig;
import com.novamart.product_service.dto.ApiResponse;
import com.novamart.product_service.dto.InventoryRequest;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;

@FeignClient(name = "inventory", url = "https://inventory:8443", configuration = FeignSslConfig.class)
public interface InventoryClient {
    @RequestMapping(method = RequestMethod.POST, value = "/api/inventory/create")
    ApiResponse createProductInventory(@RequestBody InventoryRequest inventoryRequest);

    @RequestMapping(method = RequestMethod.GET, value = "/api/inventory")
    ApiResponse getInventoryByProductId(@RequestParam String productId);

    @RequestMapping(method = RequestMethod.DELETE, value = "/api/inventory/delete-all")
    ApiResponse deleteAllInventory();
}
