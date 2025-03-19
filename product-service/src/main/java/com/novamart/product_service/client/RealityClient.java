package com.novamart.product_service.client;

import com.novamart.product_service.FeignSslConfig;
import com.novamart.product_service.dto.RealityModel;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

@FeignClient(name = "reality", url = "https://reality:8443", configuration = FeignSslConfig.class)
public interface RealityClient {
    @RequestMapping(method = RequestMethod.POST, value = "/reality/generate")
    int generateModel(@RequestBody RealityModel realityModel);

    @RequestMapping(method = RequestMethod.DELETE, value = "/reality/delete/${productId}")
    int deleteModel(String productId);
}
